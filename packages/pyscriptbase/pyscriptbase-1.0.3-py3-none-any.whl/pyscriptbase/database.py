from copy import deepcopy
import pymysql
from . import env as Env


class DataConfig:
    host = "127.0.0.1"
    user = "root"
    password = ""
    database = "account"
    table = ""
    port = 3306


def getDataConfig(database: str = "", table: str = "", port: int = 3306) -> DataConfig:
    config = DataConfig()
    config.host = Env.get("sql_host")
    config.user = Env.get("sql_user")
    config.password = Env.get("sql_password")
    config.database = database
    config.table = table
    config.port = port
    return config


class Key:
    NULL = "NULL"
    NOT_NULL = "NOT NULL"
    IS = "IS"
    EQUAL = "="
    OR = "OR"
    AND = "AND"
    NOT_EQUAL = "!="
    LIKE = "LIKE"


class SQLHelper:
    """
    数据库辅助类，不支持多线程
    """

    def __init__(self, user="root", password="root", port=3306, database="", host="localhost") -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.keywords = ["NULL", "NOT NULL"]
        self.db = pymysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            database=self.database,
            port=port,
        )
        self.__clear__()

    def __clear__(self):
        """
        重置条件变量
        """
        self.table: str = None
        self.wheres: list = None
        self.fields: list = None
        self.orders: list = None
        self.limit: int = None
        self.offset: int = None
        self.values: list = None

    def __join__(self, ds: list, delimiter: str = ","):
        if not ds:
            return ""
        res = ""
        for d in ds:
            if res:
                res += f"{delimiter}{d}"
            else:
                res += f"{d}"
        return res

    def __build_set__(self) -> str:
        """
        构建SET子句
        """
        if self.fields == None or self.values == None or len(self.fields) != len(self.values):
            return None
        kvs = []
        for i in range(len(self.fields)):
            field = self.fields[i]
            value = self.values[i]
            kvs.append(f"{field} = {value}")
        return f"SET {self.__join__(kvs)} "

    def __build_wheres__(self) -> str:
        """
        构建WHERE子句
        """
        if self.wheres == None or len(self.wheres) == 0:
            return None
        isConnect = False
        ws = []
        for where in self.wheres:
            # 自定义连接符
            if isinstance(where, str):
                ws.append(where)
                isConnect = False
            else:
                # 默认AND连接条件
                if isConnect:
                    ws.append("AND")
                ws.append(f"{where[0]} {where[1]} {where[2]}")
                isConnect = not isConnect
        return f"WHERE {self.__join__(ws,' ')} "

    def __build_orders__(self) -> str:
        """
        构建ORDER BY子句
        """
        if self.orders == None or len(self.orders) == 0:
            return None
        ods = []
        for order in self.orders:
            # 默认升序
            if len(order) == 1:
                ods.append(f"{order[0]} ASC")
            # 自定义排序
            else:
                ods.append(f"{order[0]} {order[1]}")
        return f"ORDER BY {self.__join__(ods)} "

    def __build_update__(self) -> str:
        """
        构建UPDATE语句
        """
        if self.table == None:
            return None
        sql = f"UPDATE {self.table} "
        setW = self.__build_set__()
        if setW == None:
            return None
        sql += setW
        where = self.__build_wheres__()
        if where == None:
            return None
        sql += where
        return sql

    def __build_insert__(self) -> str:
        """
        构建SELECT语句
        """
        if self.table == None:
            return None
        sql = f"INSERT INTO {self.table}({self.__join__(self.fields)}) VALUES({self.__join__(self.values)})"
        return sql

    def __build_delete__(self) -> str:
        """
        构建DELETE语句,不允许没有where条件
        """
        if self.table == None:
            return None
        where = self.__build_wheres__()
        if not where:
            return None
        sql = f"DELETE FROM {self.table} {where}"
        return sql

    def __build_query__(self) -> str:
        """
        构建SELECT语句
        """
        # 初步判断
        if self.table == None:
            return None
        # 查询语句
        sql = "SELECT "
        # 选择字段
        if self.fields != None:
            sql += f"{self.__join__(self.fields)} "
        else:
            sql += "* "
        # 选择表
        sql += f"FROM {self.table} "
        # 选择条件
        where = self.__build_wheres__()
        if where:
            sql += where
        # 选择排序
        orders = self.__build_orders__()
        if orders:
            sql += orders
        # 选择数量限制
        if self.limit != None:
            sql += f"LIMIT {self.limit} "
        # 选择偏移
        if self.offset != None:
            sql += f"OFFSET {self.offset} "
        return sql

    def __build_query_count__(self) -> str:
        """
        构建SELECT语句
        """
        # 初步判断
        if self.table == None:
            return None
        # 查询语句
        sql = "SELECT COUNT(*) "
        # 选择表
        sql += f"FROM {self.table} "
        # 选择条件
        where = self.__build_wheres__()
        if where:
            sql += where
        return sql

    def __build_replace__(self) -> str:
        """
        构建REPLACE语句
        """
        if self.table == None:
            return None
        sql = f"INSERT INTO {self.table}({self.__join__(self.fields)}) VALUES({self.__join__(self.values)}) ON DUPLICATE KEY UPDATE "
        update_fields = []
        for i in range(len(self.fields)):
            update_fields.append(f"{self.fields[i]}=VALUES({self.fields[i]})")
        sql += self.__join__(update_fields)
        return sql

    def __execute__(self, sql: str):
        """
        执行SQL语句
        """
        if not sql:
            return None
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            return cursor
        except Exception as e:
            print("======SQL ERROR======")
            print(sql)
            print(e)
            return None

    def set_database(self, db: str):
        """
        (可选)设置数据库,不设置则使用上次操作的数据库
        """
        self.db.select_db(db)
        return self

    def set_table(self, table: str):
        """
        (必选)设置要操作的表
        """
        self.__clear__()  # 清除上次的值
        self.table = table
        return self

    def set_fields(self, fields: list):
        """
        (可选)设置insert、query或update字段,对于insert不设置则默认选择全部字段
        """
        self.fields = list(fields)
        return self

    def set_values(self, values: list):
        """
        (必选)设置insert或update字段的值
        """
        self.values = list(values)
        # 字符串类型值用''包括
        for i in range(len(self.values)):
            if isinstance(self.values[i], str):
                newValue = self.values[i].replace("'", "\\'").replace('"', '\\"')
                self.values[i] = f"'{newValue}'"
        return self

    def set_dict(self, obj: dict):
        """
        （可选）设置insert或update的字典
        """
        self.set_fields(obj.keys())
        self.set_values(obj.values())
        return self

    def set_wheres(self, wheres: list):
        """
        （可选）设置update或query的条件
        """
        # 多层对象必须需要深拷贝
        self.wheres = deepcopy(wheres)
        for i in range(len(self.wheres)):
            # 连接符
            if isinstance(self.wheres[i], str):
                continue
            # kv默认用=号连接
            if len(self.wheres[i]) == 2:
                self.wheres[i].insert(1, "=")
            # 非关键字字符串类型值用''包括
            if len(self.wheres[i]) == 3 and isinstance(self.wheres[i][2], str):
                if self.wheres[i][2].upper() not in self.keywords:
                    self.wheres[i][2] = f"'{self.wheres[i][2]}'"
        return self

    def set_limit(self, limit: int):
        """
        （可选）设置query的数量
        """
        self.limit = limit
        return self

    def set_offset(self, offset: int):
        """
        （可选）设置query的偏移量
        """
        self.offset = offset
        return self

    def set_orders(self, orders: list):
        """
        （可选）设置query排序字段和排序方式(默认升序)
        - [["id","DESC"]]
        - ["id"]
        """
        self.orders = deepcopy(orders)
        return self

    def update(self) -> bool:
        """
        执行update操作,不允许没有where条件
        """
        sql = self.__build_update__()
        self.__clear__()
        cursor = self.__execute__(sql)
        if cursor != None:
            return True
        else:
            return False

    def insert(self) -> bool:
        """
        执行insert操作
        """
        sql = self.__build_insert__()
        self.__clear__()
        cursor = self.__execute__(sql)
        if cursor != None:
            return True
        else:
            return False

    def delete(self) -> bool:
        """
        执行delete操作
        """
        sql = self.__build_delete__()
        self.__clear__()
        cursor = self.__execute__(sql)
        if cursor != None:
            return True
        else:
            return False

    def query_dict(self) -> list:
        """
        当指定了字段集时，将以字典的形式返回查询结果
        """
        if not self.fields:
            return self.query()

        sql = self.__build_query__()
        fields = self.fields
        self.__clear__()
        cursor = self.__execute__(sql)
        if cursor != None:
            datas = cursor.fetchall()
            res = []
            for data in datas:
                index = 0
                dic = {}
                for field in fields:
                    dic[field] = data[index]
                    index += 1
                res.append(dic)
            return res
        else:
            return None

    def query(self) -> tuple:
        """
        执行query操作
        """
        sql = self.__build_query__()
        self.__clear__()
        cursor = self.__execute__(sql)
        if cursor != None:
            return cursor.fetchall()
        else:
            return None

    def query_count(self) -> int:
        """
        执行query操作
        """
        sql = self.__build_query_count__()
        self.__clear__()
        cursor = self.__execute__(sql)
        if cursor != None:
            return cursor.fetchone()[0]
        else:
            return None

    def replace(self) -> bool:
        """
        执行replace操作
        """
        sql = self.__build_replace__()
        self.__clear__()
        cursor = self.__execute__(sql)
        if cursor != None:
            return True
        else:
            return False

    def close(self):
        """
        关闭数据库
        """
        try:
            self.db.close()
        except:
            pass


if __name__ == "__main__":
    pass
    # # 插入-字典形式
    # proxy = {"ip": "127.0.0.1", "port": 10002}
    # db.setTable("proxies").setObj(proxy).insert()

    # # 插入-普通形式
    # fileds = ["ip", "port"]
    # values = ["127.0.0.1", 10002]
    # db.setTable("proxies").setFields(fileds).setValues(values).insert()

    # # 更新-字典形式
    # proxy = {"ip": "127.0.0.1", "port": 8080}
    # wheres = [['ip', "=", "127.0.0.1"]]
    # db.setTable("proxies").setObj(proxy).setWheres(wheres).update()

    # # 更新-普通形式
    # fileds = ["ip", "port"]
    # values = ["127.0.0.1", 8080]
    # wheres = [['ip', "=", "127.0.0.1"]]
    # db.setTable("proxies").setFields(fileds).setValues(
    #     values).setWheres(wheres).update()

    # # 查询
    # orders = ["ip", ("port", "DESC")]
    # wheres = [["port", ">", 1000]]
    # proxies = db.setTable("proxies").query()
    # proxies = db.setTable("proxies").setLimit(10).query()
    # proxies = db.setTable("proxies").setOrders(
    #     orders).setWheres(wheres).query()

    # # 复杂SQL语句，可以直接调用execute()
    # cursor = db.setTable("proxies").execute("your sql")
