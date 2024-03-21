import sys
from src.module.log import Log, err2
from src.module.read_conf import read_conf


class Date_base:

    def __init__(self):
        read_db_conf = read_conf()
        self.db = read_db_conf.database()
        self.print_log = Log()

    def insert(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            self.db.close()
            return True
        except Exception as e:
            if "PRIMARY" in str(e):
                self.print_log.write_log(f"重复数据 {sql}", 'warning')
                return '重复数据'
            elif "timed out" in str(e):
                self.print_log.write_log("连接数据库超时", 'error')
                sys.exit()
            else:
                err2(e)
                self.print_log.write_log(f"错误 {sql}", 'warning')
                return False

    def update(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            err2(e)
            if "timed out" in str(e):
                self.print_log.write_log("连接数据库超时", 'error')
            else:
                self.print_log.write_log(f'{sql}', 'error')
            return False
        finally:
            if hasattr(self, 'db') and self.db:
                self.db.close()

    def select(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return True, result
        except Exception as e:
            err2(e)
            if "timed out" in str(e):
                self.print_log.write_log("连接数据库超时", 'error')
            else:
                self.print_log.write_log(f'{sql}', 'error')
        finally:
            if hasattr(self, 'db') and self.db:
                self.db.close()

    def delete(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            self.db.close()
            return result
        except Exception as e:
            err2(e)
            if "timed out" in str(e):
                self.print_log.write_log(f"连接数据库超时", 'error')
            self.print_log.write_log(sql, 'error')
        finally:
            if hasattr(self, 'db') and self.db:
                self.db.close()

    def system_sql(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            cursor.commit()
            cursor.close()
            self.db.close()
        except Exception as e:
            err2(e)
            if "timed out" in str(e):
                self.print_log.write_log(f"连接数据库超时", 'error')
            self.print_log.write_log(sql, 'error')
        finally:
            if hasattr(self, 'db') and self.db:
                self.db.close()
