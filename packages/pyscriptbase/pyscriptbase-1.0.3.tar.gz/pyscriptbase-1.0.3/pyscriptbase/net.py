import json
from urllib.parse import urljoin
import requests
from copy import deepcopy
from xmltodict import parse as xmlParse
import warnings
from time import sleep


warnings.filterwarnings("ignore")


class NetRequest:
    def __init__(self, headers: dict = {}, debug=False) -> None:
        """
        @headers：基础请求头
        @useLocalProxy：是否使用系统级的代理
        @debug：是否需要输出请求信息
        """
        self.headers = deepcopy(headers)
        self.headersFunc = None
        self.debug = debug
        self.proxies = None
        self.session = requests.session()
        self.session.trust_env = False

    def _debug_(self, text: str) -> None:
        """
        打印输出
        """
        if self.debug:
            print(text, flush=True)

    def addHeaders(self, headers: dict) -> None:
        """
        添加请求头
        """
        if self.headers:
            self.headers.update(headers)
        else:
            self.headers = deepcopy(headers)

    def setHeaders(self, headers: dict) -> None:
        """
        重置请求头
        """
        self.headers = deepcopy(headers)

    def setHeadersFunc(self, func) -> None:
        """
        添加动态请求头函数\n
        每次请求会调用该函数获取请求头
        """
        self.headersFunc = func

    def get(
        self,
        url: str,
        headers: dict = None,
        proxies: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout=5,
        maxTry=3,
        params: dict = {},
    ):
        """
        GET
        """
        return self.__req__(
            method="GET",
            url=url,
            body=None,
            headers=headers,
            isJson=isJson,
            isXml=isXml,
            isCookie=isCookie,
            allow_redirects=allow_redirects,
            timeout=timeout,
            proxies=proxies,
            maxTry=maxTry,
            params=params,
        )

    def post(
        self,
        url: str,
        body: str = None,
        headers: dict = None,
        proxies: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout: int = 5,
        maxTry=3,
        params: dict = {},
    ):
        """
        POST
        """
        return self.__req__(
            method="POST",
            url=url,
            body=body,
            headers=headers,
            proxies=proxies,
            isJson=isJson,
            isXml=isXml,
            isCookie=isCookie,
            allow_redirects=allow_redirects,
            timeout=timeout,
            maxTry=maxTry,
            params=params,
        )

    def put(
        self,
        url: str,
        body: str = None,
        headers: dict = None,
        proxies: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout: int = 5,
        maxTry=3,
        params: dict = {},
    ):
        """
        PUT
        """
        return self.__req__(
            method="PUT",
            url=url,
            body=body,
            headers=headers,
            proxies=proxies,
            isJson=isJson,
            isXml=isXml,
            isCookie=isCookie,
            allow_redirects=allow_redirects,
            timeout=timeout,
            maxTry=maxTry,
            params=params,
        )

    def delete(
        self,
        url: str,
        body: str = None,
        headers: dict = None,
        proxies: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout: int = 5,
        maxTry=3,
    ):
        """
        DELETE
        """
        return self.__req__(
            method="DELETE",
            url=url,
            body=body,
            headers=headers,
            proxies=proxies,
            isJson=isJson,
            isXml=isXml,
            isCookie=isCookie,
            allow_redirects=allow_redirects,
            timeout=timeout,
            maxTry=maxTry,
        )

    def __req__(
        self,
        method: str,
        url: str,
        body: str = None,
        headers: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        proxies: dict = None,
        timeout: int = 5,
        maxTry=3,
        params: dict = {},
    ):
        finalHeaders = deepcopy(self.headers)
        if self.headersFunc:
            finalHeaders.update(self.headersFunc())
        if headers:
            finalHeaders.update(headers)
        if not proxies:  # 优先外部代理
            proxies = self.proxies

        for i in range(0, maxTry):
            try:
                res = self.session.request(
                    method=method,
                    url=url,
                    headers=finalHeaders,
                    data=body,
                    proxies=proxies,
                    verify=False,
                    allow_redirects=allow_redirects,
                    timeout=timeout,
                    params=params,
                )
                self._debug_(f"url: {res.url}")
                self._debug_(f"code: {res.status_code}")
                self._debug_(f"bdoy: {res.text}")

                if isCookie:
                    return res.cookies.get_dict()
                elif isXml:
                    return xmlParse(res.text)
                elif isJson:
                    return res.json()
                else:
                    return res.text
            except Exception as e:
                self._debug_(e)
                if i != maxTry - 1:
                    self._debug_(f"netPost请求失败\t重新请求")
                else:
                    self._debug_(f"netPost请求失败\t结束请求")
                sleep(0.1)


class CloudRequest:
    def __init__(self, headers: dict = {}, debug=False) -> None:
        """
        @headers：基础请求头
        @debug：是否需要输出请求信息
        """
        self.cloud: dict = None
        self.headers: dict = deepcopy(headers)
        self.headersFunc: function = None
        self.debug: bool = debug
        self.net: NetRequest = None
        self.session = requests.session()
        self.session.trust_env = False

    def _debug_(self, text: str) -> None:
        """
        打印输出
        """
        if self.debug:
            print(text, flush=True)

    def addHeaders(self, headers: dict) -> None:
        """
        添加请求头
        """
        if self.headers:
            self.headers.update(headers)
        else:
            self.headers = deepcopy(headers)

    def setHeaders(self, headers: dict) -> None:
        """
        重置请求头
        """
        self.headers = deepcopy(headers)

    def setHeadersFunc(self, func) -> None:
        """
        添加动态请求头函数\n
        每次请求会调用该函数获取请求头
        """
        self.headersFunc = func

    def post(
        self,
        url: str,
        body: str = None,
        headers: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout: int = 5,
        maxTry=3,
        params: dict = {},
    ):
        return self.__req__(
            method="POST",
            url=url,
            body=body,
            headers=headers,
            isJson=isJson,
            isXml=isXml,
            isCookie=isCookie,
            allow_redirects=allow_redirects,
            timeout=timeout,
            maxTry=maxTry,
            params=params,
        )

    def get(
        self,
        url: str,
        headers: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout=5,
        maxTry=3,
        params: dict = {},
    ):
        return self.__req__(
            method="GET",
            url=url,
            body=None,
            headers=headers,
            isJson=isJson,
            isXml=isXml,
            isCookie=isCookie,
            allow_redirects=allow_redirects,
            timeout=timeout,
            maxTry=maxTry,
            params=params,
        )

    def put(
        self,
        url: str,
        body: str = None,
        headers: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout: int = 5,
        maxTry=3,
        params: dict = {},
    ):
        return self.__req__(
            method="PUT",
            url=url,
            body=body,
            headers=headers,
            isJson=isJson,
            isXml=isXml,
            isCookie=isCookie,
            allow_redirects=allow_redirects,
            timeout=timeout,
            maxTry=maxTry,
            params=params,
        )

    def delete(
        self,
        url: str,
        body: str = None,
        headers: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout: int = 5,
        maxTry=3,
        params: dict = {},
    ):
        return self.__req__(
            method="DELETE",
            url=url,
            body=body,
            headers=headers,
            isJson=isJson,
            isXml=isXml,
            isCookie=isCookie,
            allow_redirects=allow_redirects,
            timeout=timeout,
            maxTry=maxTry,
            params=params,
        )


    def __req__(
        self,
        method: str,
        url: str,
        body: str = None,
        headers: dict = None,
        isJson=True,
        isXml=False,
        isCookie=False,
        allow_redirects=True,
        timeout: int = 5,
        maxTry=3,
        params: dict = {},
    ):
        if self.cloud is None:
            self._debug_("cloud未设置")
            return

        # cloud共享使用net的请求头
        if self.net and self.net.headers:
            finalHeaders = deepcopy(self.net.headers)
        else:
            finalHeaders = deepcopy(self.headers)
        if self.headersFunc:
            finalHeaders.update(self.headersFunc())
        if headers:
            finalHeaders.update(headers)

        ReqBody = {
            "method": method,
            "url": urljoin(url, params),
            "body": body,
            "headers": finalHeaders,
            "timeout": timeout,
        }
        ReqHeaders = {
            "Content-Type": "application/json",
            "token": self.cloud["token"],
        }

        for i in range(0, maxTry):
            try:
                res = self.session.post(
                    url=self.cloud["url"],
                    headers=ReqHeaders,
                    data=json.dumps(ReqBody),
                    verify=False,
                    allow_redirects=allow_redirects,
                    timeout=timeout,
                )
                rjson = res.json()

                if isCookie:
                    return self.__parseCookie__(rjson["headers"])
                elif isXml:
                    return xmlParse(rjson["data"])
                elif isJson:
                    return json.loads(rjson["data"])
                else:
                    return rjson["data"]
            except Exception as e:
                if i != maxTry - 1:
                    self._debug_(f"netPost请求失败\t重新请求")
                else:
                    self._debug_(f"netPost请求失败\t结束请求")
                sleep(0.1)

    def __parseCookie__(self, headers: dict) -> dict:
        """
        解析cookie字符串为字典
        """
        cookieStr: str = headers.get("Set-Cookie", "")
        if not cookieStr:
            return {}
        cookie_dict = {}
        for item in cookieStr.split(";"):
            if "=" in item:
                key, value = item.split("=", 1)
                cookie_dict[key.strip()] = value.strip()
        return cookie_dict
