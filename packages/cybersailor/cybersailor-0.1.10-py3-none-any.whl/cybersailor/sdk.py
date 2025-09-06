from typing import Any, Optional, Dict
from carthooks import Client
from .logger import Logger
from .sqs_listener import SQSListener
from .watch_renewal import WatchRenewal
import traceback
import os
import time
import json

class Task:
    def __init__(self, handler, app_id, collection_id, 
                trigger="pulling_items", 
                filter=None, 
                pagelimit=1,
                include_locked=False,
                sort=['created'], 
                pulling_interval=30):
        self.handler = handler
        self.trigger = trigger
        self.last_pull = 0
        self.last_pull_items = 0
        self.pulling_options = {
            "app_id": app_id,
            "collection_id": collection_id,
            "filter": filter,
            "sort": sort,
            "pulling_interval": pulling_interval,
            "pagelimit": pagelimit,
            "include_locked": include_locked
        }
    
    def pulling_now(self):
        self.last_pull = time.time()

    def is_pull_able(self):
        if self.last_pull_items > 0:
            return True
        return time.time() - self.last_pull > self.pulling_options["pulling_interval"]

class Record:
    def __init__(self, sailor, app_id, collection_id, item_id, data):
        self.sailor = sailor
        self.app_id = app_id
        self.collection_id = collection_id
        self.item_id = item_id
        self.__record = data
        self.id = data.get("id", item_id)
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
        self.creator = data.get("creator")
        self.title = data.get("title")
        self.data = data.get("fields", {})  # Safe field access
        
        # Debug information
        if sailor and sailor.logger:
            sailor.logger.debug(f"Creating Record: {self.item_id}")
    
    def __getitem__(self, key):
        return self.__record.get(key)

    def __str__(self) -> str:
        return f"Record(title={self.__record.get('title')}, item_id={self.item_id})"
    
    def __repr__(self) -> str:
        return f"Record(app_id={self.app_id}, collection_id={self.collection_id}, item_id={self.item_id})"
    
    def lock(self, **kwargs):
        if self.sailor:
            return self.sailor.lock(self, **kwargs)
        else:
            raise Exception("Record has no associated sailor instance")
    
    def unlock(self):
        if self.sailor:
            return self.sailor.unlock(self)
        else:
            raise Exception("Record has no associated sailor instance")
    
    def update(self, map):
        if self.sailor:
            return self.sailor.update(self, map)
        else:
            raise Exception("Record has no associated sailor instance")

    
class Context:
    def __init__(self, sailor, task, logger):
        self.task = task
        self.sailor = sailor
        self.logger = logger

    # def __getattribute__(self, __name: str) -> Any:
    #     return self.sailor.client.__getattribute__(__name)

    # def create(self, app_id, collection_id, data):
    #     return self.sailor.create(app_id, collection_id, data)

class Sailor:
    def __init__(self, token=None, sailor_id=None):
        # Add debug info to confirm using local version
        print("=" * 60)
        print("🚀 Using local development version of cybersailor SDK")
        print(f"📁 File path: {__file__}")
        print(f"📦 Module path: {__name__}")
        print("=" * 60)
        
        self.tasks = []
        self.logger = Logger("cybersailor")
        self.client = Client()
        self.client.setAccessToken(token)
        
        # New: SQS and renewal related properties
        self.sqs_listener = None
        self.watch_renewal = None
        self._running = False
        
        if sailor_id == None:
            self.sailor_id = os.uname().nodename
        else:
            self.sailor_id = sailor_id

    def subscribe(self, handler, app_id, collection_id, filter=None, 
                 sqs_queue_url=None, watch_name=None, age=432000, 
                 renewal_interval=3600, auto_ack=True, **kwargs):
        """
        Subscribe to data changes
        
        Args:
            handler: Data processing function
            app_id: Application ID
            collection_id: Collection ID
            filter: Filter conditions
            sqs_queue_url: SQS queue URL (if provided, use SQS mode)
            watch_name: Monitoring task name
            age: Monitoring validity period (seconds), default 5 days
            renewal_interval: Renewal interval (seconds), default 1 hour
            auto_ack: Auto acknowledge messages (default True), False requires manual msg.ack()
            **kwargs: Compatibility parameters for old version (like pagelimit, pulling_interval, etc.)
        """
        print("🔔 Local SDK: Setting up subscription...")
        print(f"📋 Subscription params: app_id={app_id}, collection_id={collection_id}")
        print(f"🔧 SQS mode: {'Yes' if sqs_queue_url else 'No'}")
        print(f"🎯 ACK mode: {'Auto' if auto_ack else 'Manual'}")
        
        # Check if using SQS mode
        if sqs_queue_url:
            self._setup_sqs_subscription(
                handler=handler,
                app_id=app_id,
                collection_id=collection_id,
                filter=filter,
                sqs_queue_url=sqs_queue_url,
                watch_name=watch_name or f"watch-{app_id}-{collection_id}",
                age=age,
                renewal_interval=renewal_interval,
                auto_ack=auto_ack
            )
        else:
            # Fallback to polling mode (backward compatibility)
            print("⚠️  Local SDK: No SQS config provided, using polling mode")
            self._setup_polling_subscription(
                handler=handler,
                app_id=app_id,
                collection_id=collection_id,
                filter=filter,
                **kwargs
            )
            
    def _setup_sqs_subscription(self, handler, app_id, collection_id, filter, 
                               sqs_queue_url, watch_name, age, renewal_interval, auto_ack):
        """Setup SQS subscription mode"""
        try:
            # 1. Convert filter format
            filters = self._convert_filter_to_watch_format(filter) if filter else None
            
            # 2. Call start_watch_data to register monitoring
            watch_config = {
                'endpoint_url': sqs_queue_url,
                'name': watch_name,
                'app_id': app_id,
                'collection_id': collection_id,
                'filters': filters,
                'age': age
            }
            
            result = self.client.start_watch_data(**watch_config)
            
            if not result.success:
                raise Exception(f"Failed to register monitoring: {result.error}")
                
            print(f"✅ Monitoring task registered successfully: {watch_name}")
            
            # 3. Start SQS listener
            self.sqs_listener = SQSListener(
                queue_url=sqs_queue_url, 
                handler=handler,
                app_id=app_id,
                collection_id=collection_id,
                auto_ack=auto_ack
            )
            self.sqs_listener.set_sailor(self)  # Set sailor instance
            self.sqs_listener.start()
            
            # 4. Start renewal task
            self.watch_renewal = WatchRenewal(
                self.client, 
                watch_config, 
                renewal_interval
            )
            self.watch_renewal.start_renewal()
            
            print(f"✅ SQS subscription setup completed")
            
        except Exception as e:
            self.logger.error(f"SQS subscription setup failed: {e}")
            print(f"❌ SQS subscription setup failed: {e}")
            # Could consider fallback to polling mode
            raise
            
    def _setup_polling_subscription(self, handler, app_id, collection_id, filter, **kwargs):
        """Setup polling subscription mode (original logic)"""
        task = Task(
            handler=handler,
            app_id=app_id,
            collection_id=collection_id,
            filter=filter,
            **kwargs
        )
        self.tasks.append(task)
        print(f"✅ Polling subscription added, current task count: {len(self.tasks)}")
        
    def _convert_filter_to_watch_format(self, filter_dict: Dict) -> Optional[Dict]:
        """
        Convert subscribe filter format to watch API filters format
        
        Original format: {"f_1009": {"$eq": 1}}
        Target format: {"f_1009": {"$eq": 1}}  # Direct format, no need for conditions wrapper
        """
        if not filter_dict:
            return None
            
        # Based on curl example, return filter conditions directly, no need for mode and conditions wrapper
        return filter_dict

    def lock(self, record, lock_timeout=600, subject=None):
        self.logger.debug(f"Locking task: {record}")
        return self.client.lockItem(record.app_id, record.collection_id, record.item_id, lock_timeout=lock_timeout, lock_id=self.sailor_id, subject=subject)

    def unlock(self, record):
        self.logger.debug(f"Unlocking task: {record}")
        return self.client.unlockItem(record.app_id, record.collection_id, record.item_id, lock_id=self.sailor_id)

    def update(self, task, map):
        self.logger.info(f"Updating task: {task} with map: {map}")
        return self.client.updateItem(task.app_id, task.collection_id, task.item_id, map)

    def create(self, app_id, collection_id, data):
        self.logger.info(f"Creating record in app_id: {app_id}, collection_id: {collection_id} with data: {data}")
        result = self.client.createItem(app_id, collection_id, data)
        return result

    def run(self):
        """Run Sailor"""
        print("🏃 Local SDK: Starting to run...")
        self.logger.debug("Running...")
        self._running = True

        try:
            # If using SQS mode, mainly wait for SQS listener to work
            if self.sqs_listener:
                print("🎯 SQS mode running...")
                while self._running:
                    time.sleep(1)  # Keep main thread alive
            else:
                # Polling mode (original logic)
                print("🔄 Polling mode running...")
                while self._running:
                    for task in self.tasks:
                        if task.trigger == "pulling_items" and task.is_pull_able():
                            self.pull(task)
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n⏹️  Received interrupt signal, stopping...")
            self.stop()
        except Exception as e:
            self.logger.error(f"Runtime error: {e}")
            self.stop()
            
    def stop(self):
        """Stop Sailor and all related services"""
        print("🛑 Stopping Sailor...")
        self._running = False
        
        # Stop SQS listener
        if self.sqs_listener:
            self.sqs_listener.stop()
            print("✅ SQS listener stopped")
            
        # Stop renewal task
        if self.watch_renewal:
            self.watch_renewal.stop_renewal()
            print("✅ Renewal task stopped")
            
        print("✅ Sailor stopped")

    def pull(self,task):
        try:
            app_id = task.pulling_options["app_id"]
            collection_id = task.pulling_options["collection_id"]
            self.logger.info(f"Pulling items from app_id: {app_id}, collection_id: {collection_id}")

            options = {}

            if task.pulling_options["sort"] != None:
                options["sort"] = task.pulling_options["sort"]

            if task.pulling_options["filter"] != None:
                for column in task.pulling_options["filter"]:
                    for operator in task.pulling_options["filter"][column]:
                        options[f"filters[{column}][{operator}]"] = task.pulling_options["filter"][column][operator]

            if task.pulling_options["include_locked"] == False:
                options["unlockedOrLockedBy"] = self.sailor_id

            result = self.client.getItems(app_id, collection_id, limit=task.pulling_options["pagelimit"], **options)
            self.logger.debug(f"Result: {result}")
            
            items = result.data
            if items is None:
                self.logger.info(f"Error: {result.error}")
                task.pulling_now()
                task.last_pull_items = 0
                return
                
            task.pulling_now()
            task.last_pull_items = len(items)
            if len(items) > 0:
                context = Context(sailor=self, task=task, logger=self.logger)
                for item in items:
                    self.logger.info(f"Handling item: {item['id']}")
                    record = Record(sailor=self, app_id=app_id, collection_id=collection_id, item_id=item['id'], data=item)
                    self.logger.debug(f"Record: {record}")
                    try:
                        task.handler(context, record)
                    except Exception as e:
                        traceback.print_exc()
                        # self.logger.error(f"Error: {e}")
        except Exception as e:
            self.logger.error(f"Error: {e}")
            time.sleep(5)