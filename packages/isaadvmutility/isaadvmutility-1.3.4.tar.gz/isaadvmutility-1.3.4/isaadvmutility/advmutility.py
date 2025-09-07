from datetime import datetime
import glob
import hashlib
import ipaddress
import logging
import os
from ipaddress import IPv4Address, ip_address
from json import load, JSONDecodeError, dump
from re import search

from isaadvmutility.datastore import DataStoreI
import pandas as pd

from isaadvmutility.logger import get_logger


logger = get_logger(self.__class__.__name__)

class NoScannerIpError(Exception):
    def __init__(self, message):
        super().__init__(message)

container = 'lookup'     
network_excluded_list = 'excluded/networks.csv'
host_excluded_list = 'excluded/hosts.csv'


# Function to convert epoch timestamps to datetime objects
def convert_epoch_to_datetime(value):
    # if pd.notna(value) and (isinstance(value, int) or isinstance(value, float) or (isinstance(value, str) and value.isdigit())):
    if pd.notna(value) and (
        isinstance(value, (int, float))
        or (isinstance(value, str) and value.isdigit())
    ):
        return datetime.utcfromtimestamp(value)
    else:
        return value
    
def set_to_csv(value_set):
    value_set = {x for x in value_set if not (isinstance(x, float) and math.isnan(x))}
    
    unique_values = list(set(value_set))
    return ', '.join(map(str, unique_values))

# Function to create IP ranges from the list of IPs
def combine_ips(ips):
    # Filter out invalid IP addresses (non-string values and empty strings)
    valid_ips = [ip for ip in ips if isinstance(ip, str) and ip]

    # Convert the valid IP addresses to IPv4Address objects and sort them
    ip_objs = sorted([IPv4Address(ip) for ip in valid_ips])

    if not ip_objs:
        return ""

    ranges = []
    
    start = ip_objs[0]
    end = ip_objs[0]
    
    for i in range(1, len(ip_objs)):
        if ip_objs[i].packed == end.packed + 1:
            end = ip_objs[i]
        else:
            ranges.append((start, end))
            start = ip_objs[i]
            end = ip_objs[i]

    ranges.append((start, end))

    # Format the IP ranges as strings
    range_strings = [f"{r[0]}-{r[1]}" if r[0] != r[1] else str(r[0]) for r in ranges]
    
    return ", ".join(range_strings)


    # Format the IP ranges as strings
    range_strings = [f"{r[0]}-{r[1]}" if r[0] != r[1] else str(r[0]) for r in ranges]
    
    return ", ".join(range_strings)

def filteredOut(ip, networkDescription, hostname):
    if is_in_excluded_networks(ip) \
            or is_in_excluded_hosts(ip) \
            or not is_scan_required(networkDescription) \
            or not is_scan_required(hostname):
        logger.debug(f"No scan required for {ip}: {hostname}")
        return True
    return False


def is_valid_ip(param):
    try:
        ip_address(param)
        return True
    except ValueError:
        return False


def is_valid_location(location):
    '''Should return only networks that are not public, or being scanned or excluded'''
    try:
        if search(r'[Dd][Cc][34]', location) or search(r'[Ss]tretch', location):
            return True
    except TypeError:
        return False
    return False


def is_in_excluded_networks(network, data_store: DataStoreI):
    if len(str(network).split('/')) > 1:
        network = str(network).split('/')[0].strip()
    ''' Check the exclusion list to see whether a given network has been excluded '''
    df_excluded_networks = data_store.read(container=container, object_name=network_excluded_list, file_type='csv')
    df_excluded_networks["lower"] = df_excluded_networks.apply(
        lambda row: int(ipaddress.IPv4Network(row.network)[0]), axis=1)
    df_excluded_networks["upper"] = df_excluded_networks.apply(
        lambda row: int(ipaddress.IPv4Network(row.network)[-1]), axis=1)
    query_result = df_excluded_networks.loc[
        (df_excluded_networks.upper >= (int(ipaddress.IPv4Address(network)))) & (
                df_excluded_networks.lower <= (int(ipaddress.IPv4Address(network))))]
    if not query_result.empty:
        return True
    return False


def is_in_excluded_hosts(ip, data_store: DataStoreI):
    df_excluded_hosts = data_store.read(container=container, object_name=host_excluded_list)
    rslt = df_excluded_hosts.loc[df_excluded_hosts['ip'] == ip]
    if rslt.empty:
        return False
    return True

def is_scan_required(description):
    try:
        if search(r'fw', description.lower()) \
        or search(r'lb', description.lower()) \
        or search(r'vip', description.lower()) \
                or search(r'_( )?[a-zA-Z]?nat', description.lower()) \
                or search(r'vdi', description.lower()) \
                or search(r'bgp', description.lower()) \
                or search(r'ipsec', description.lower()) \
                or search(r'mpls', description.lower()) \
                or search(r'routing vrf', description.lower()) \
                or search(r'vpn', description.lower()) \
                or search(r'tunnel', description.lower()):
            logger.debug(f"Unscannable based on description: {description}")
            return False
        return True
    except AttributeError:
        return True


def is_vlan_valid(vlanid):
    try:
        if isinstance(int(vlanid), int):
            return True
    except (ValueError, TypeError):
        return False


def sanatize(net_desc):
    name_str = ''
    if isinstance(net_desc, float):
        return ''
    if '\n' in net_desc:
        for word in net_desc.split('\n'):
            name_str = name_str + ' ' + word
    else:
        name_str = net_desc
    s, sanatized_name = name_str.split(','), ''
    if len(s) >= 1:
        for word in s:
            sanatized_name = sanatized_name + ' ' + word
    else:
        sanatized_name = name_str
    return sanatized_name


def get_scanner_ip(network):
    try:
        scanner_ip = ipaddress.IPv4Network(network)[7]
        if int(str(scanner_ip).split('.')[-1]) == 7:
            logger.debug(f"Scanner IP: {scanner_ip}")
            return scanner_ip
        raise NoScannerIpError(f'scanner IP address can be from network: {network}')
    except IndexError:
        raise NoScannerIpError(f'scanner IP address can be from network: {network}')


def get_hash(filename, data_store: DataStoreI):
    try:
        with open(data_store.read(container=',',object_name='')) as inf:
            hashes_store = load(inf)
            return hashes_store[filename]
    except (KeyError, JSONDecodeError, FileNotFoundError):
        return None



def compute_hash(filename):
    sha256_hash = hashlib.sha256()
    hash_value, hashes_store = None, {}
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            hash_value = sha256_hash.hexdigest()
    return hash_value


def store_hash(filename, hash_value, data_store: DataStoreI):
    try:
        with open(fr'{data_store.read(container="", object_name=hash_store_file)}') as inf:
            hashes_store = load(inf)
    except (JSONDecodeError, FileNotFoundError):
        hashes_store = {}
    hashes_store.update({filename: hash_value})
    with open(f'{data_store.read(container="", object_name=hash_store_file)}', 'w') as out_file:
        dump(hashes_store, out_file, indent=4)


def get_lastest_file(path, prefix='', extension='csv'):
    try:
        if path[len(path) - 1] != '/':
            path = path + '/'
        map_reports = glob.iglob(f'{path}{prefix}*.{extension}')
        return max(map_reports, key=os.path.getctime)
    except ValueError:
        raise FileNotFoundError


def logError(logFilePath, message):
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s',
                        filename=logFilePath)
    logging.error(f'{message}')


def logInfo(logFilePath, message):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s',
                        filename=logFilePath)
    logging.info(f'{message}')

def append_to_file(filename, message):
    # Get the current timestamp in a desired format
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Open the file in append mode and write the message with the timestamp
    with open(filename, 'a') as file:
        file.write(f'[{timestamp}] {message}\n')