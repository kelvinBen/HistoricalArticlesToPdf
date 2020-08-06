# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/HistoricalArticlesToPdf

import os
import yaml
import logging
import libs.core as Core

print(Core.script_root_dir)
log_conf_file = os.path.join(Core.script_root_dir,"log.yml")
with open(log_conf_file,"r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__) 
