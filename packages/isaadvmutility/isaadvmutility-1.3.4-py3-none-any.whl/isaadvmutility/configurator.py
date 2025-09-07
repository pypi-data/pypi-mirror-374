import json
import os
import sys
from pathlib import Path
from re import search
from configobj import ConfigObj
from pathlib import Path

from isaadvmutility.logger import get_logger

class Configurator:
    
    def __init__(self, workingd) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.workingd = workingd
        
        try: 
            self.packagePath = [ppath for ppath in sys.path if ppath.split('\\')[-1] == workingd ][0]
        except IndexError: 
            self.packagePath = os.getcwd()

        self.base_resources_dir, self.base_dir = self.get_base_dir()

        self.config = ConfigObj(indent_type='\t')
        self.config.filename = os.path.join(self.packagePath, 'config/settings.cfg')
        self.config['path'] = {}
        
    
    def get_base_dir(self):
        self.logger.debug(f"Working Dir: {self.workingd}")
        base_dir = f'~/{self.workingd}'
        # This package should be installed in user choosen directory or user home directory
        base_resources_dir = f'{base_dir}/resources' # TODO: This will go to blob storage
        return base_resources_dir, base_dir

    def generate_data_path_section(self, parent, data):
        """
        :param parent:
        :param data:
        :return:
        """
        for child, value in data.items():
            if isinstance(value, dict):
                parent[child] = {}
                self.generate_data_path_section(data=value, parent=parent[child])
            elif isinstance(value, list):
                parent[child] = {}

    def set_file_path(self,data,   directory=None):
        
        for directory, values in data.items():
            for file in values:
                fp = file.split("/")[-1].split(".")[0]
                if search(r'lookup', directory):
                    self.config['path']['file'][directory][fp] = os.path.join(self.packagePath, file)
                else:
                    self.config['path']['file'][directory][fp] = os.path.join(self.base_resources_dir, file)
                    
        # SETUP FILE PATH
        try:            
            # ADD LOGS SECTION
            self.config['path']['logs'] = {}
            self.config['path']['logs']['map_reports'] = os.path.join(self.base_dir, "logs/map_reports.log") # TODO: To be replace by bucket location
            self.config['path']['logs']['appliances'] = os.path.join(self.base_dir, "logs/appliances.log")  # TODO: To be replace by bucket location

            # ADD HASH SECTION
            self.config['path']["hash"] = os.path.join(self.base_resources_dir, "file_hash.json")  # TODO: To be replace by bucket location
        except (KeyError, TypeError):
            pass

    def create_path(self, pathobj):
        for _, value in pathobj.items():
            if isinstance(value, dict):
                self.create_path(value)
            elif len(value.split('.')) == 1:
                os.makedirs(value, exist_ok=True)
            else:
                pathFromFile = "/".join(value.split("/")[:-1])
                os.makedirs(pathFromFile, exist_ok=True)

    def generate(self):
        with open(os.path.join(self.packagePath, "config/resourcespath.json"), "r") as f: 
            files = json.load(f)
        # SETTING CONFIG SECTIONS
        self.config['path']['file'] = {}
        self.generate_data_path_section(parent=self.config['path']['file'], data=files)
        self.set_file_path(data=files)
        self.logger.info("Generating configurations")
        return self.config
    
if __name__ == "__main__":
    Configurator(workingd='vulnerability_mgmt').generate()
