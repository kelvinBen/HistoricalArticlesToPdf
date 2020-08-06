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

class Bootstrapper(object):
    def __init__(self, path,out_path):
        global script_root_dir
        global db_conf_file 
        global dbpool

        script_root_dir = os.path.dirname(os.path.abspath(path))
        db_conf_file = os.path.join(script_root_dir,"db.cnf")
        dbpool = db.DataPool("SQLite","HistoicalArticles",out_path)

    def init(self):
        LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(threadName)s] %(name)s %(filename)s: %(lineno)d: %(message)s"
        logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT)