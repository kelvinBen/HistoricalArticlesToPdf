# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/HistoricalArticlesToPdf

import os
import time
import logging
import logging.handlers
from libs.tools import db

script_root_dir = ""
db_conf_file = ""
dbpool = None
version_file = ""
version = "1.0.2"
class Bootstrapper(object):
    def __init__(self, path,out_path):
        global script_root_dir
        global db_conf_file 
        global dbpool
        global out_dir
        
        LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(threadName)s] %(name)s %(filename)s: %(lineno)d: %(message)s"
        logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT)

        script_root_dir = os.path.dirname(os.path.abspath(path))
        db_conf_file = os.path.join(script_root_dir,"db.cnf")
        out_dir = os.path.join(out_path,"HistoicalArticles")
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        self.version_file = os.path.join(out_path,"version.txt")
        
        dbpool = db.DataPool("SQLite","HistoicalArticles",out_dir)
        

    def init(self,dir_name):
        out_dir_path =  os.path.join(out_dir,dir_name)
        if not os.path.exists(out_dir_path):
            os.makedirs(out_dir_path)
        return out_dir_path
