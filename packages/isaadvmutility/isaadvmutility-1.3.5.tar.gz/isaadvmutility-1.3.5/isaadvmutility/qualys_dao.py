import xml.etree.ElementTree as ElementTree

import qualysapi
import os 

import requests

from isaadvmutility.datastore import  FileDataStore
from isaadvmutility.logger import get_logger

class NoQCredentialsError(Exception):
    pass

class Qualys():
    def __init__(self, endpoint, config_loader: FileDataStore = None):
        self.logger = get_logger(self.__class__.__name__)
        self.qualys_api_user = os.environ.get('QUALYS_API_USER')
        self.qualys_api_password = os.environ.get('QUALYS_API_PASSWORD')
        
        if config_loader:
            self.__connection = qualysapi.connect(config_loader.read(container=None, object_name='credentials'))
    
        elif self.qualys_api_user and self.qualys_api_password:
            self.__connection = qualysapi.connect(
                hostname ="qualysapi.qg2.apps.qualys.eu", 
                username = os.environ.get('QUALYS_API_USER'),
                password = os.environ.get('QUALYS_API_PASSWORD')
            )
        else:
    
            raise NoQCredentialsError("Invalid Qualys Credentials")
            
        self.api_endpoint = endpoint

    def fetch(self, parameters=None, response_output_file=None, http_method='get', api_version=2.0):
        try:
            response = self.__connection.request(
                self.api_endpoint, data=parameters,
                api_version=api_version,
                http_method=http_method
            )
            
            if response_output_file:
                with open(response_output_file, 'w', encoding='utf-8') as out_file:
                    out_file.write(response)
                    
            return response
        
        except requests.exceptions.ConnectionError as he:
            logging.basicConfig(
                level=logging.ERROR,
                format='%(asctime)s:%(levelname)s:%(message)s',
                filename='../logs/qualysrequest.log'
            )
            logging.error(he)
            return None

    def write(self, parameters=None):
        try:
            # Attempt the request
            response = self.__connection.request(self.api_endpoint, parameters, concurrent_scans_retries=2)
            self.logger.debug(f"Qualys API response received, length: {len(response) if response else 0} bytes")
            
            # Parse the XML response
            root = ElementTree.fromstring(response)
            return root
        except requests.exceptions.ConnectionError as he:
            # Log connection error to file
            self.logger.error(f"Connection error occurred: {he}", exc_info=True)
        except Exception as e:
            # Log any other exceptions that occur
            self.logger.error(f"An error occurred: {e}", exc_info=True)


    def get_connection(self):
        return self.__connection
