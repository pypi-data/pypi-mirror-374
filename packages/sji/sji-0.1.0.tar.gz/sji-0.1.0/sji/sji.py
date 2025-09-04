"""
Einfache Helper-Funktionen für Job-Initialisierung.
"""

from typing import Dict, Any
from datetime import datetime
import uuid
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import configparser



class SimpleJobInit(object):

    def __init__(self, script_file_path: str):

        self._script_file_path = script_file_path
        self._script_dir = os.path.dirname(script_file_path)
        self._script_basename = os.path.basename(script_file_path).replace(".py", "")
                
        self._log_folder = os.path.join(self._script_dir, "logs")
        if not os.path.exists(self._log_folder):
            os.makedirs(self._log_folder)
        self._log_filepath = os.path.join(self._log_folder, f"{self._script_basename}.log")

        self._config_filepath = os.path.join(self._script_dir, f"{self._script_basename}.config.ini")
        self._config = configparser.ConfigParser()
        if os.path.isfile(self._config_filepath):
            self._config.read(self._config_filepath)
        else:
            raise ValueError("Config file {} missing...".format(self._config_filepath))

        logging.basicConfig(level=logging.INFO, format='[%(asctime)s][%(levelname)s][%(name)s][%(module)s - %(funcName)s] %(message)s')
        self._logger = logging.getLogger(self._script_basename)
        
        if self._config.has_section('logging'):

            logging_config = self._config['logging']
            level = logging_config.get('level', logging.INFO)
            self._logger.setLevel(level)
            self._logger.addHandler(logging.StreamHandler())
            log_rotation_when = logging_config.get('log_rotation_when', 'midnight')
            log_rotation_backup_count = logging_config.get('log_rotation_backup_count', 0)
            log_file_handler = TimedRotatingFileHandler(self._log_filepath, encoding='utf-8', when=log_rotation_when, backupCount=log_rotation_backup_count)
            self._logger.addHandler(log_file_handler)
        
       
        self._tmp_folder = os.path.join(self._script_dir, "tmp")
        if not os.path.exists(self._tmp_folder):
            os.makedirs(self._tmp_folder)
        self._persistent_files_path_stub = os.path.join(self._script_dir, f"{self._script_basename}")

    @property
    def logger(self):
        return self._logger

    @property
    def config(self):
        return self._config

    def get_tmp_file_path(self, file_name: str):
        return os.path.join(self._tmp_folder, file_name)

    def get_persistent_file_path(self, file_ending: str):
        return f"{self._persistent_files_path_stub}.{file_ending}"
