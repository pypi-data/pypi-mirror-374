from concurrent.futures import ThreadPoolExecutor, as_completed
from . import net
from . import database


class ScriptApp:
    _proxies = []
    _cloudProxies = []

    def __init__(self, index: int = 1, useProxy: bool = True, debug: bool = False, useCloud: bool = True) -> None:
        self.index = index
        self.logs = []
        self.debug = debug
        self.net = net.NetRequest()
        self.cloudNet = net.CloudRequest()
        self.cloudNet.net = self.net
        useProxy and self.__setProxy__(index)
        useCloud and self.__setCloudProxy__(index)

    def __setProxy__(self, index: int) -> None:
        config = database.getDataConfig("account", "proxy")
        if not config.user or not config.host or not config.password:
            return
        if len(ScriptApp._proxies) == 0:
            try:
                sql = database.SQLHelper(user=config.user, password=config.password, port=config.port, database=config.database, host=config.host)
                fields = ["host", "port"]
                wheres = [["type", 1], ["state", 1]]
                datas = sql.set_table(config.table).set_wheres(wheres).set_fields(fields).query_dict()
                proxies = [None]
                for data in datas:
                    proxies.append({"http": f"http://{data['host']}:{data['port']}", "https": f"http://{data['host']}:{data['port']}"})
                ScriptApp._proxies = proxies
            except:
                ScriptApp._proxies = [None]
        if len(ScriptApp._proxies):
            self.net.proxies = ScriptApp._proxies[index % len(ScriptApp._proxies)]

    def __setCloudProxy__(self, index: int) -> None:
        config = database.getDataConfig("account", "cloud_proxy")
        if not config.user or not config.host or not config.password:
            return
        if len(ScriptApp._cloudProxies) == 0:
            try:
                sql = database.SQLHelper(user=config.user, password=config.password, port=config.port, database=config.database, host=config.host)
                fields = ["url", "token"]
                wheres = [["state", 1]]
                datas = sql.set_table(config.table).set_wheres(wheres).set_fields(fields).query_dict()
                ScriptApp._cloudProxies = datas
            except:
                ScriptApp._cloudProxies = []
        if len(ScriptApp._cloudProxies):
            self.cloudNet.cloud = ScriptApp._cloudProxies[index % len(ScriptApp._cloudProxies)]

    def __log__(self, msg: str | dict = "", flush: bool = False):
        if flush or self.debug:
            print(msg, flush=True)
        else:
            if isinstance(msg, str):
                self.logs.append(msg)
            else:
                self.logs.append(str(msg))

    def __runFunc__(self, fun: callable, *args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except Exception as e:
            self.__log__(e)


class InviteObj:
    id = ""
    accpet: int = 0
    send: int = 0
    params = {}
    target: list[dict] = []

    def __init__(self):
        pass


def threadPool(func, args, num=5):
    # 启用线程池
    executor = ThreadPoolExecutor(max_workers=num)
    tasks = [executor.submit(func, arg, index + 1) for index, arg in enumerate(args)]
    results = []
    for future in as_completed(tasks):
        data = future.result()
        results.append(data)
    return results
