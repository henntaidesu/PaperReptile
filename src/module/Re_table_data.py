import sys
from src.module.execution_db import Date_base
from src.module.log import Log

logger = Log()


def compare_data_index_to_cnki_inf(index_data):
    aa = 1
    for i in index_data:
        UUID = i[0]
        sql2 = f"SELECT UUID FROM `cnki_paper_information` WHERE `UUID` = '{UUID}'"
        flag, index_data = Date_base().select(sql2)

        aa += 1
        # print(index_data)
        if index_data:
            logger.write_log(f'{UUID}', 'info')
        else:
            sql3 = f"INSERT INTO `Paper`.`test` (`index`) VALUES ('{UUID}')"
            sql4 = (f"UPDATE `Paper`.`cnki_index` SET `start` = '0' , receive_time = '2024-03-08 00:00:00'  WHERE UUID "
                    f" = '{UUID}';")
            Date_base().insert(sql3)
            # Date_base().update_all(sql4)
            logger.write_log(f'{UUID} - {aa}', 'error')



