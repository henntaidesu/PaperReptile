import sys
from src.module.execution_db import Date_base
from src.module.log import Log

logger = Log()


def compare_data_index_to_cnki_inf(index_data):

    for i in index_data:
        UUID = i[0]
        sql2 = f"SELECT UUID FROM `index` WHERE `UUID` = '{UUID}' and `from` = 'cnki'"
        flag, index_data = Date_base().select_all(sql2)
        # print(index_data)
        if index_data:
            logger.write_log(f'{UUID}', 'info')
        else:
            sql3 = f"INSERT INTO `Paper`.`test` (`index`) VALUES ('{UUID}')"
            # sql4 = f"UPDATE `Paper`.`cnki_index` SET `start` = '0'  WHERE UUID = '{UUID}';"
            Date_base().insert_all(sql3)
            # Date_base().update_all(sql4)
            logger.write_log(f'{UUID}', 'error')

