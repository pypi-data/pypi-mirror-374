from abc import ABC, abstractmethod
from io import BytesIO, StringIO
import os
import re
import time
from configobj import ConfigObj
import pandas as pd
import json
import yaml
from datetime import datetime
import pytz
import yaml
import json
from isaadvmutility.configurator import Configurator
import pyarrow.parquet as pq
from psycopg2 import sql, DatabaseError
from  isaadvmutility.pgdbconnection import DBConnection
import pytz
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from datetime import datetime
import pandas as pd
import pyarrow.parquet as pq
from io import BytesIO, StringIO
from azure.core.exceptions import ResourceExistsError, ServiceRequestError
import dask.dataframe as dd
from dask.distributed import Client
import pyarrow
from isaadvmutility.logger import get_logger


class DataStoreI (ABC):
    def __init__(self):
        self.ds_cfg = None
        
    @abstractmethod
    def create(self, container):
        """_summary_

        Args:
            repository (_type_): _description_
        """
    
    @abstractmethod 
    def days_since_update(self, container: str, object_name: str) -> int:
        """
        Method to get the age of data from the contianer
        Args:
            container (_type_): The type 
            object_name (_type_): _description_
        """
        
    @abstractmethod   
    def read(self, container, object_name):
        """
        Read data from a contaner
        Args:
            bucket_name (_type_): _description_
            file_name (_type_): _description_

        Returns:
            _type_: _description_
        """
        
    @abstractmethod 
    def put(self, container, object_name, data: dict | pd.DataFrame):
        """ write data to a container

        Args:
            container (_type_): _description_
            object_name (_type_): _description_
            data (_type_): _description_

        Returns:
            _type_: _description_
        """
 
class Singleton(type(DataStoreI)):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]




class RedisDataStore(DataStoreI, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        
    def create(self, container):
        """_summary_

        Args:
            repository (_type_): _description_
        """

    def days_since_update(self, container: str, object_name: str) -> int:
        """
        Method to get the age of data from the contianer
        Args:
            container (_type_): The type 
            object_name (_type_): _description_
        """
        
    def read(self, container, object_name):
        """
        Read data from a contaner
        Args:
            bucket_name (_type_): _description_
            file_name (_type_): _description_

        Returns:
            _type_: _description_
        """
         
    def put(self, container, object_name, data: dict | pd.DataFrame):
        """ write data to a container

        Args:
            container (_type_): _description_
            object_name (_type_): _description_
            data (_type_): _description_

        Returns:
            _type_: _description_
        """

class FileDataStore(DataStoreI, metaclass=Singleton):
    def __init__(self, workingd: str):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.workingd = workingd
        self.config  = self.create()
        self.files = self.config['file']

    def create(self, container = 'path'):
        config = Configurator(self.workingd).generate()[container]
        return config

    def put(self, container, object_name, data: pd.DataFrame | dict):
        file_extension =  object_name.split('.')[-1]
        object_name = object_name.split('.')[0]
            
        if re.match(r'y(a)?ml', file_extension):
            with open (self.files[container][object_name], "w") as file:
                yaml.dump(data, file)
            
        elif re.match(r'json', file_extension):
            with open(self.files[container][object_name], "w") as fp:
                json.dump(data, fp, indent=4)
            
        elif re.match(r'csv', file_extension):
            pd.DataFrame(data).to_csv(self.files[container][object_name], index=False)
    
    def days_since_update(self, container, object_name):
        try:
            today = datetime.datetime.now()
            file_stat = os.stat(self.config[container][object_name])
            modified_time = time.ctime(file_stat.st_mtime)
            try:
                modified_time = datetime.datetime.strptime(modified_time, '%a %b %d %H:%M:%S %Y')
            except ValueError:
                self.logger.warning(f"Modified time (ValueError caught): {modified_time}")
            return (today - modified_time).days
        except FileNotFoundError:
            return 10000
    
    def read(self, container, object_name):
        file_extension =  object_name.split('.')[-1]
        object_name = object_name.split('.')[0]
        if re.match(r'ini', file_extension):
            return self.files[container]['credentials']
        if re.match(r'hash', object_name):
            return self.files[container]['hash']
        elif re.match(r'y(a)?ml', file_extension):
            with open (fr'{self.files[container][object_name]}') as file:
                return yaml.safe_load(file)
        elif re.match(r'json', file_extension):
            with open (fr'{self.files[container][object_name]}') as file:
                return json.load(file)
        elif re.match(r'csv', file_extension):
            return pd.read_csv(self.files[container][object_name])
        
        
class PostgresDataStore(DataStoreI, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.db_conn_instance = DBConnection.getInstance()

    def create(self, table_name, columns):
        columns_str = ", ".join([f"{k} {v}" for k, v in columns.items()])

        create_table_query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            {}
        )
        """).format(sql.Identifier(table_name), sql.SQL(columns_str))

        conn = self.db_conn_instance.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            self.logger.info(f"Table {table_name} created successfully.")
        except (Exception, DatabaseError) as error:
            conn.rollback()
            self.logger.error(f"Failed to create table {table_name}. {error}", exc_info=True)
        finally:
            cursor.close()
            self.db_conn_instance.putconn(conn)

    def days_since_update(self, container: str, object_name: str) -> int:
        conn = self.db_conn_instance.getconn()
        cursor = conn.cursor()
        query = sql.SQL("SELECT last_updated FROM {} WHERE id = %s").format(sql.Identifier(container))
        cursor.execute(query, (object_name,))
        last_updated = cursor.fetchone()
        cursor.close()
        self.db_conn_instance.putconn(conn)
        
        if last_updated is None:
            return None
        return (datetime.now(tz=last_updated.tzinfo) - last_updated[0]).days


    def read(self, table_name, columns=None, conditions=None):
        """ 
        Fetch data from the database.

        Parameters:
        - table_name: The name of the table to read from.
        - columns: A list of columns to select. If None, selects all columns.
        - conditions: A dictionary where the keys are column names and the values are the conditions for those columns.

        Returns:
        - A list of dictionaries representing the retrieved rows.
        """

        # Validate input
        if conditions and not isinstance(conditions, dict):
            raise ValueError("conditions parameter should be a dictionary or None.")

        if columns and not isinstance(columns, list):
            raise ValueError("columns parameter should be a list or None.")

        columns_str = ", ".join(columns) if columns else '*'

        if not conditions:
            query = f"SELECT {columns_str} FROM {table_name}"
            params = tuple()
        else:
            condition_strs = [f"{column} = %s" for column in conditions.keys()]
            query = f"SELECT {columns_str} FROM {table_name} WHERE {' AND '.join(condition_strs)}"
            params = tuple(conditions.values())

        conn = self.db_conn_instance.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
        except (Exception, DatabaseError) as error:
            self.logger.error(f"Failed to execute query. {error}", exc_info=True)
            result = []
        finally:
            self.db_conn_instance.putconn(conn)

        return result


    def put(self, query, params):
        conn = self.db_conn_instance.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
        except (Exception, DatabaseError) as error:
            conn.rollback()
            self.logger.error(f"Failed to execute query: {error}", exc_info=True)
        finally:
            self.db_conn_instance.putconn(conn)



class AzureBlobDataStore:
    def __init__(self):
        connection_string = os.getenv('AZURE_CONNECTION_STRING')
        self.logger = get_logger(self.__class__.__name__)
        self.account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        self.account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def create(self, container):
        try:
            self.blob_service_client.create_container(container)
        except ResourceExistsError:
            pass  # Container already exists
        return self

    def put_with_retry(self, blob_client, data, chunk_size=4*1024**2, max_retries=3, backoff_time=10):
        data_size = len(data.getbuffer())
        if data_size < chunk_size:
            for i in range(max_retries):
                try:
                    blob_client.upload_blob(data, blob_type="BlockBlob", overwrite=True)
                    break  # If the upload was successful, break out of the loop
                except ServiceRequestError as e:
                    if i == max_retries - 1:  # If this was the last retry, re-raise the exception
                        raise e
                    else:
                        self.logger.warning(f"Upload failed, retrying ({i+1}/{max_retries})")
                        time.sleep(backoff_time)  # Wait for the specified backoff time
        else:
            block_ids = []
            for i in range(0, data_size, chunk_size):
                data_chunk = data.read(chunk_size)
                block_id = f"{i}".zfill(16)
                blob_client.stage_block(block_id, data_chunk)
                block_ids.append(block_id)
            blob_client.commit_block_list(block_ids)
            
    
    def put(self, container, object_name, data, index=False, format='csv'):
        import time
        from io import BytesIO
        import json
        import pandas as pd
        import dask.dataframe as dd

        container_client = self.blob_service_client.get_container_client(container)

        if not isinstance(data, (pd.DataFrame, dict, dd.DataFrame)):
            raise TypeError('Data should be either a pandas DataFrame, a dictionary, or a Dask DataFrame.')

        def log_size(obj, label):
            size_mb = obj.getbuffer().nbytes / (1024 * 1024)
            self.logger.debug(f"{label} size: {size_mb:.2f} MB")

        if isinstance(data, pd.DataFrame):
            self.logger.debug(f"[put] DataFrame shape: {data.shape}")
            self.logger.debug(f"[put] Estimated memory: {data.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB")

            if format in ('csv', 'both'):
                try:
                    start = time.time()
                    data_csv = data.reset_index().to_csv(index_label='id') if index else data.to_csv(index=False)
                    csv_buffer = BytesIO(data_csv.encode('utf-8'))
                    log_size(csv_buffer, "CSV")

                    csv_object_name = object_name.split(".")[0] + ".csv"
                    self.logger.info(f"[put] Uploading CSV: {csv_object_name}")
                    self.put_with_retry(container_client.get_blob_client(csv_object_name), csv_buffer)
                    self.logger.info(f"[put] CSV uploaded in {time.time() - start:.2f}s")
                except Exception as e:
                    self.logger.error(f"[put] CSV upload failed: {e}", exc_info=True)
                    raise

            if format in ('parquet', 'both'):
                try:
                    start = time.time()
                    parquet_buffer = BytesIO()
                    data.to_parquet(parquet_buffer, engine='pyarrow', compression='snappy', index=index)
                    parquet_buffer.seek(0)
                    log_size(parquet_buffer, "Parquet")

                    parquet_object_name = object_name.split(".")[0] + ".parquet"
                    self.logger.info(f"[put] Uploading Parquet: {parquet_object_name}")
                    self.put_with_retry(container_client.get_blob_client(parquet_object_name), parquet_buffer)
                    self.logger.info(f"[put] Parquet uploaded in {time.time() - start:.2f}s")
                except Exception as e:
                    self.logger.error(f"[put] Parquet upload failed: {e}", exc_info=True)
                    raise

        elif isinstance(data, dd.DataFrame):
            self.logger.info(f"[put] Uploading Dask DataFrame to: {object_name}")
            blob_path = f'abfs://{container}/{object_name}'
            self.retry_upload(data, blob_path, storage_options={
                'account_name': self.account_name,
                'account_key': self.account_key
            })

        elif isinstance(data, dict):
            try:
                json_object_name = object_name.split(".")[0] + ".json"
                self.logger.info(f"[put] Uploading JSON: {json_object_name}")
                self.put_with_retry(container_client.get_blob_client(json_object_name), BytesIO(json.dumps(data).encode('utf-8')))
                self.logger.info("[put] JSON uploaded.")
            except Exception as e:
                self.logger.error(f"[put] JSON upload failed: {e}", exc_info=True)
                raise

    def days_since_update(self, container, object_name, file_type='parquet'):
        try:
            if not object_name.endswith(f'.{file_type}'):
                object_name = object_name.rsplit('.', 1)[0] + f'.{file_type}'

            container_client = self.blob_service_client.get_container_client(container)
            blob_client = container_client.get_blob_client(object_name)
            props = blob_client.get_blob_properties()
            last_modified = props.last_modified

            tz = pytz.timezone('UTC')
            today = datetime.now(tz)
            delta = today - last_modified.replace(tzinfo=tz)
            days_since_update = delta.days
            return days_since_update
        except Exception as e:
            self.logger.error(f"Error retrieving last update date: {e}", exc_info=True)
            return 1000
    
    def read(self, container, object_name, file_type='parquet', dask: Client = None, skip_rows=0):
        try:
            if dask: 
                path = f'abfs://{container}/{object_name}/*.{file_type}'
                self.logger.info(f"Reading {file_type} data from {path}")
                storage_options = {'account_name': self.account_name, 'account_key': self.account_key}
               
                df = dd.read_parquet(path=path, storage_options=storage_options)
                if skip_rows > 0:
                    df = df.partitions[1:].map_partitions(lambda d: d.iloc[skip_rows:])
                return df
            if not object_name.endswith(f'.{file_type}'):
                object_name = object_name.rsplit('.', 1)[0] + f'.{file_type}'

            container_client = self.blob_service_client.get_container_client(container)
            blob_client = container_client.get_blob_client(object_name)
            stream = blob_client.download_blob().readall()

            if file_type == 'parquet':
                return pq.read_table(BytesIO(stream)).to_pandas()
            elif file_type == 'csv':
                return pd.read_csv(StringIO(stream.decode('utf-8')), skiprows=skip_rows)
            elif file_type == 'json':
                return json.loads(stream.decode('utf-8'))
            else:
                self.logger.error("Unsupported file type. Supported file types are 'csv' and 'parquet'")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving file: {e}", exc_info=True)
            return None
    
    @staticmethod
    def retry_upload(data, blob_path, storage_options, max_retries=5, delay=30):
        """Attempt to upload data to Azure Blob Storage, retrying on failure.
        Args:
            data (dd.DataFrame): The Dask DataFrame to upload.
            blob_path (str): The blob path in Azure Blob Storage.
            storage_options (dict): Storage options including account name and key.
            max_retries (int): Maximum number of retries.
            delay (int): Delay between retries in seconds.
        """
        logger = get_logger("AzureBlobDataStore")
        attempt = 0
        while attempt < max_retries:
            try:
                dd.to_parquet(data, path=blob_path, storage_options=storage_options)
                logger.info("Upload successful.")
                return
            except Exception as e:
                attempt += 1
                logger.warning(f"Upload failed on attempt {attempt}: {str(e)}")
                if attempt < max_retries:
                    logger.warning(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
        
        logger.error("Upload failed after maximum retries.")