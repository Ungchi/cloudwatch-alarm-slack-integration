import logging
import os

log = logging.getLogger(__name__)
log.handlers.clear()
log.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
log.addHandler(sh)
