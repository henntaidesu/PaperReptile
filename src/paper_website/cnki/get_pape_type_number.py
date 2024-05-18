from src.paper_website.cnki.cnki_components import *
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from src.module.execution_db import DB
from src.module.UUID import UUID
from src.model.cnki import Crawl, positioned_element, paper_DB_flag, paper_DB_DT
from src.module.log import Log, err2, err3
from src.module.read_conf import ReadConf


def get_number():
    pass

