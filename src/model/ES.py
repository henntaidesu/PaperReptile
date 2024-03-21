from src.module.log import Log, err1
from src.module.execution_db import Date_base
from src.module.read_conf import read_conf
from src.module.now_time import now_time
from datetime import datetime, timezone, timedelta


class ArxivModel:
    @staticmethod
    def ES_classification():
        sql = f"SELECT * FROM arxiv_classification_type"
        flag, data = Date_base().select(sql)
        classification_dict = {}
        for i in data:
            classification_dict[i[0]] = i[1]

        return classification_dict
