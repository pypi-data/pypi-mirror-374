# encoding=utf8

import requests
import warnings
from json import dumps as jsonDumps
from typing import List

warnings.filterwarnings("ignore")


class Envrionment:
    def __init__(self, id: int, name: str, value: str, remarks: str = "") -> None:
        """
        初始化
        """
        self.id = id
        self.name = name
        self.value = value
        self.remarks = ""

    def toJson(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "remarks": self.remarks,
        }


class PanelClient:
    headers = {"content-type": "application/json", "accept": "application/json"}

    def __init__(self, address: str, id: str, secret: str) -> None:
        """
        初始化
        """
        self.address = self.__validAddress__(address)
        self.clientId = id
        self.clientSecret = secret
        self.valid = False
        self.session = requests.session()
        self.session.headers.update(self.headers)

        self.__login__()

    def __validAddress__(self, address: str) -> str:
        if not address.startswith("http://") and not address.startswith("https://"):
            address = f"http://{address}"
        if address.endswith("/"):
            address = address[0:-1]
        return address

    def __log__(self, content: str, start="", end="\n") -> None:
        """
        日志
        """
        print(content)

    def __login__(self) -> None:
        """
        登录
        """
        url = f"{self.address}/open/auth/token?client_id={self.clientId}&client_secret={self.clientSecret}"
        try:
            rjson = self.session.get(url, verify=False).json()
            if rjson["code"] == 200:
                self.auth = f"{rjson['data']['token_type']} {rjson['data']['token']}"
                self.session.headers.update({"Authorization": self.auth})
                self.valid = True
                self.__log__(f"面板登录成功：{rjson['data']['token']}", start="\n")
            else:
                self.valid = False
                self.__log__(f"面板登录失败：{rjson['message']}", start="\n")
        except Exception as e:
            self.valid = False
            self.__log__(f"面板登录失败：{str(e)}", start="\n")

    def addEnvs(self, envs: List[Envrionment]) -> bool:
        """
        新建环境变量
        """
        url = f"{self.address}/open/envs"
        try:
            body = []
            for env in envs:
                body.append({"name": env.name, "value": env.value, "remarks": env.remarks})
            rjson = self.session.post(url, data=jsonDumps(body), verify=False).json()
            if rjson["code"] == 200:
                self.__log__(f"新建环境变量成功：{len(envs)}")
                return True
            else:
                self.__log__(f"新建环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.__log__(f"新建环境变量失败：{str(e)}")
            return False

    def updateEnvs(self, env: Envrionment) -> bool:
        """
        更新环境变量
        """
        url = f"{self.address}/open/envs"
        try:
            body = jsonDumps(env.toJson())
            rjson = self.session.put(url, verify=False, data=body).json()
            if rjson["code"] == 200:
                self.__log__(f"更新环境变量成功")
            else:
                self.__log__(f"更新环境变量失败：{rjson['message']}")
        except Exception as e:
            self.__log__(f"更新环境变量失败：{str(e)}")

    def addOrUpdateEnv(self, env: Envrionment) -> bool:
        """
        添加或更新环境变量
        """
        envs = self.getEnvs()
        if not envs:
            self.addEnvs([env])
            return True
        for env_ in envs:
            if env_.name == env.name:
                env.id = env_.id
                self.updateEnvs(env)
                return True
        self.addEnvs([env])

    def getEnvs(self, search: str = "") -> list[Envrionment]:
        """
        获取环境变量
        """
        url = f"{self.address}/open/envs?searchValue={search}"
        result: list[Envrionment] = []
        try:
            rjson = self.session.get(url, verify=False).json()
            if rjson["code"] == 200:
                for env in rjson["data"]:
                    result.append(Envrionment(env["id"], env["name"], env["value"], env["remarks"]))
            else:
                self.__log__(f"获取环境变量失败：{rjson['message']}")
        except Exception as e:
            self.__log__(f"获取环境变量失败：{str(e)}")
        return result

    def deleteEnvs(self, ids: list[int]) -> bool:
        """
        删除环境变量
        """
        url = f"{self.address}/open/envs"
        try:
            rjson = self.session.delete(url, data=jsonDumps(ids), verify=False).json()
            if rjson["code"] == 200:
                self.__log__(f"删除环境变量成功：{len(ids)}")
                return True
            else:
                self.__log__(f"删除环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.__log__(f"删除环境变量失败：{str(e)}")
            return False

    def enableEnvs(self, ids: list[int]) -> bool:
        """
        启用环境变量
        """
        url = f"{self.address}/open/envs/enable"
        try:
            rjson = self.session.put(url, data=jsonDumps(ids), verify=False).json()
            if rjson["code"] == 200:
                self.__log__(f"启用环境变量成功：{len(ids)}")
                return True
            else:
                self.__log__(f"启用环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.__log__(f"启用环境变量失败：{str(e)}")
            return False

    def disableEnvs(self, ids: list[int]) -> bool:
        """
        禁用环境变量
        """
        url = f"{self.address}/open/envs/disable"
        try:
            rjson = self.session.put(url, data=jsonDumps(ids), verify=False).json()
            if rjson["code"] == 200:
                self.__log__(f"禁用环境变量成功：{len(ids)}")
                return True
            else:
                self.__log__(f"禁用环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.__log__(f"禁用环境变量失败：{str(e)}")
            return False
