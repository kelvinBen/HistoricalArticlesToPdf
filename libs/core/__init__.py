import os
import time
import logging
import logging.handlers


script_root_dir = ""
db_conf_file = ""
class Bootstrapper(object):
    def __init__(self, path):
        global script_root_dir
        global db_conf_file 
        script_root_dir = os.path.dirname(os.path.abspath(path))
        db_conf_file = os.path.join(script_root_dir,"db.cnf")
        

    def init(self):
        LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(threadName)s] %(name)s %(filename)s: %(lineno)d: %(message)s"
        logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT)