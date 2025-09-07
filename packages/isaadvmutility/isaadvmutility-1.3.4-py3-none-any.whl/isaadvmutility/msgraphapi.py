import os
import msal
import requests

from isaadvmutility.datastore import DataStoreI
from isaadvmutility.logger import get_logger

class MSConnection:
    def __init__(self, client_id=None, client_secret=None, tenant_id=None, scope = ['https://api.securitycenter.microsoft.com/.default']):
        self.logger = get_logger(self.__class__.__name__)
         # If client_id is not provided, read from environment variable
        client_id = client_id or os.getenv('AZURE_CLIENT_ID')

        # If client_secret is not provided, read from environment variable
        client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')

        # If tenant_id is not provided, read from environment variable
        tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')

        authority = f"https://{os.getenv('AZURE_AUTHORITY_HOST')}/{tenant_id}"
        
        # Create an MSAL instance providing the client_id, authority and client_credential parameters
        self.client = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

        # First, try to lookup an access token in cache
        self.token_result = self.client.acquire_token_silent(scope, account=None)
        
        # If the token is available in cache, save it to a variable
        if self.token_result:
            self.access_token = 'Bearer ' + self.token_result['access_token']
            self.logger.info("Access token was loaded from cache")

        # If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
        if not self.token_result:
            self.token_result = self.client.acquire_token_for_client(scopes=scope)
            self.access_token = 'Bearer ' + self.token_result['access_token']
            self.logger.info("New access token was acquired from Azure AD")

    def get_access_token(self):
        return self.access_token


class WindowsDefenderAPI:
    def __init__(self, connection: MSConnection = None):
        self.logger = get_logger(self.__class__.__name__)
        if connection is None:
            connection = MSConnection()
        self.connection = connection
        self.headers = {
            'Authorization':  self.connection.get_access_token(),
            'Content-Type': 'application/json'
        }

    def fetch_data(self, api_endpoint):
        host = 'https://api.securitycenter.microsoft.com/api'
        # Check and remove leading '/' in api_endpoint if present
        api_endpoint = api_endpoint[1:] if api_endpoint.startswith('/') else api_endpoint

        url = f"{host}/{api_endpoint}"
        self.logger.debug(f"API Endpoint URL: {url}")

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            results = response.json().get('value', [])  
            while '@odata.nextLink' in response.json():
                response = requests.get(response.json()['@odata.nextLink'], headers=self.headers)
                results.extend(response.json().get('value', []))
        else:
            self.logger.debug(f"API request failed with status: {response.status_code}")
            results = response

        return results
    
    
class MicrosoftGraphAPI:
    def __init__(self, datastore: DataStoreI, connection: MSConnection = None):
        self.logger = get_logger(self.__class__.__name__)
        if connection is None:
            connection = MSConnection()
        self.connection = connection
        self.headers = {
            'Authorization':  self.connection.get_access_token(),
            'Content-Type': 'application/json'
        }
        self.s3_datastore: DataStoreI = datastore

    def fetch_data(self, api_endpoint, object_name, payload, bucket='microsoft',  days=1):
        # Check and remove leading '/' in api_endpoint if present
        api_endpoint = api_endpoint[1:] if api_endpoint.startswith('/') else api_endpoint

        # Removing the '.json' or '.csv' from object_name, if present
        if object_name.endswith('.json') or object_name.endswith('.csv'):
            object_name = object_name.rsplit('.', 1)[0]

        url = f"https://graph.microsoft.com/v1.0/{api_endpoint}"
        self.logger.debug(f"URL: {url}")
        
        # Checking if the data in the store is not older than specified days
        if self.s3_datastore.days_since_update(container=bucket, object_name=object_name + '.csv') <= days:
            self.logger.info(f"The data in the S3 store for the API endpoint '{api_endpoint}' and {object_name} file is not older than {days} day(s). No need to fetch data.")
            return

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            results = response.json().get('results', [])  
            while '@odata.nextLink' in response.json():
                response = requests.post(response.json()['@odata.nextLink'], headers=self.headers, json=payload)
                results.extend(response.json().get('results', []))
        else:
            self.logger.debug(f"API request failed with status: {response.status_code}")
            results = response

        return results
        

