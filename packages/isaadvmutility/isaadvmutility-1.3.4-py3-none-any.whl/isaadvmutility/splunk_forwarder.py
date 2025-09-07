import json
import numpy as np
import requests
import os
import hashlib
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from isaadvmutility.datastore import PostgresDataStore
import urllib3
from requests.adapters import HTTPAdapter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from isaadvmutility.logger import get_logger

class SplunkHEC:
    def __init__(self, sourcetype, table_name=None, prune_time='1d', hec_token=None, 
                    splunk_host=None, index='vulnerability', source='defender'):
            # If splunk_host is not provided, try to get it from the environment variable, 
            # otherwise set it to 'defaulthost'
            self.logger = get_logger(self.__class__.__name__)
            if not splunk_host:
                splunk_host = os.environ.get('SPLUNK_HOST', 'oxsysspkidxhec-lb4.isagrp.local')
            splunk_port = os.environ.get('SPLUNK_PORT', '8088')
            self.hec_url = f'https://{splunk_host.rstrip("/").replace("http://", "").replace("https://", "")}:{splunk_port}/services/collector/event'
            self.hec_token = hec_token or os.environ.get('HEC_TOKEN')

            if not self.hec_token:
                raise ValueError("HEC_TOKEN is neither provided as a parameter nor set as an environment variable.")
            
            self.session = requests.Session()

            retries = urllib3.Retry(
                total=10,  
                backoff_factor=3, 
                status_forcelist=[500, 502, 503, 504],  
            )

            adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=50)
            self.session.mount('https://', adapter)

            self.session.headers.update({
                'Authorization': 'Splunk ' + self.hec_token,
                'Content-Type': 'application/json'
            })

            self.session.verify = False # TODO: to be updated to allow tls certificate verification  by adding our internal ca to the containers
            
            self.sourcetype = sourcetype
            self.index = index
            self.source = source
            
            self.table_name = table_name
            if self.table_name:
                self.db_store = PostgresDataStore()
                
                columns = {
                    "hash": "VARCHAR(255) PRIMARY KEY UNIQUE",
                    "sourcetype": "VARCHAR(255)", 
                    "last_updated": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
                }

                self.db_store.create(self.table_name, columns)
            
            self.prune_time = self._parse_prune_time(prune_time or os.environ.get('PRUNE_TIME', '1d'))
    
    def _handle_nan_values(self, data):
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    new_data[key] = self._handle_nan_values(value)
                elif isinstance(value, float) and np.isnan(value):  
                    new_data[key] = "" 
                else:
                    new_data[key] = value
            return new_data
        elif isinstance(data, list):
            new_list = []
            for item in data:
                if isinstance(item, (dict, list)):
                    new_list.append(self._handle_nan_values(item))
                elif isinstance(item, float) and np.isnan(item):
                    new_list.append("")  
                else:
                    new_list.append(item)
            return new_list
        else:
            return data

    def _send_to_splunk(self, event_data, host=None):
        event = {
            'source': self.source,
            'sourcetype': self.sourcetype,
            'index': self.index,
            'event': event_data
        }
        if host:
            event['host'] = host
       
        response = self.session.post(self.hec_url, data=json.dumps(event))

        success = True
        if response.status_code == 200:
            parsed_json = response.json()
            if int(parsed_json['code']) == 9:
                self.logger.error(f"Failed to write event to Splunk: {event}")
                self.logger.debug(f"Parsed JSON:\n{json.dumps(parsed_json, indent=4)}")
                success = False
        else:
             self.logger.error("Server did not respond")
             success = False
        return success

    def _store_hash(self, event_data):
        hash_str = hashlib.md5(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        self.logger.debug(f"Storing hash: {hash_str}")
        query = f"""
        INSERT INTO {self.table_name} (hash, sourcetype) 
        VALUES (%s, %s) 
        ON CONFLICT (hash) DO UPDATE 
        SET last_updated = CURRENT_TIMESTAMP, sourcetype = EXCLUDED.sourcetype
        """
        self.db_store.put(query, (hash_str, self.sourcetype))

    def _hash_exists(self, event_data):
        hash_str = hashlib.md5(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
        conditions = {"hash": hash_str, "sourcetype": self.sourcetype}
        data = self.db_store.read(table_name=self.table_name, columns=["hash"], conditions=conditions)
        return len(data) > 0

    def prune_hashes(self):
        if self.table_name and self.prune_time:
            cutoff_time = datetime.now() - self.prune_time
            query = f"""
            DELETE FROM {self.table_name} 
            WHERE last_updated < %s AND sourcetype = %s
            """
            self.db_store.put(query, (cutoff_time, self.sourcetype))

        
    def _parse_prune_time(self, prune_time):
        amount = int(prune_time[:-1])
        unit = prune_time[-1]
        if unit == 'h':
            return timedelta(hours=amount)
        elif unit == 'd':
            return timedelta(days=amount)
        elif unit == 'w':
            return timedelta(weeks=amount)
        elif unit == 'm':
            if len(prune_time) >= 3 and prune_time[-2] == 'i':  # '1min' format
                return timedelta(minutes=amount)
            else:
                return timedelta(days=30 * amount)
        else:
            raise ValueError("Invalid prune time format. Use '1h', '1d', '1w', '1m', or '1min'.")

        
    def send_event(self, event_data):
        for key, value in event_data.items():
            if isinstance(value, np.ndarray):
                event_data[key] = value.tolist()

        # Handle NaN values in the event data
        event_data = self._handle_nan_values(event_data)

        host = event_data.pop('host', '')

        if self.table_name:
            event_with_extra_data = {
                "event_data": event_data,
                "host": host,
                "hec_url": self.hec_url
            }
            if not self._hash_exists(event_with_extra_data):
                if self._send_to_splunk(event_data, host):
                    self._store_hash(event_with_extra_data)
                    return 1
        else:
            if self._send_to_splunk(event_data, host):
                return 1
        return 0
    
    def send_events_concurrently(self, events, max_workers=10):
        self.prune_hashes()
        sent_events_count = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_event = {executor.submit(self.send_event, event): event for event in events}
            for future in as_completed(future_to_event):
                try:
                    success = future.result()
                    sent_events_count += success
                except Exception as exc:
                    self.logger.error(f"Event generated an exception: {exc}, Event: {future_to_event[future]}", exc_info=True)
        return sent_events_count
