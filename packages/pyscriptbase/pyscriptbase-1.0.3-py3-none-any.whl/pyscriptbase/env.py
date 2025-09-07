import os
import random


def get(name: str, defValue: str = "") -> str:
    """
    从环境变量获取一个字符串。

    :param name: 环境变量名称。
    """
    value = os.getenv(name)  # 直接使用getenv方法来获取环境变量的值
    if value:
        return value
    else:
        return defValue


def getList(name: str, delimiter: str = "&", default: any = [], count: int = -1, shuffle: bool = False) -> list:
    """
    从环境变量获取一个以特定分隔符分割的字符串列表。

    :param name: 环境变量名称。
    :param delimiter: 用于分割环境变量字符串的分隔符，默认为'&'。
    :param default: 如果环境变量不存在，则返回此默认值，默认为None。
    :param count: 指定返回列表中的元素个数，默认为-1，表示返回所有元素。
    :return: 分割后的字符串列表或默认值。
    """
    value = os.getenv(name)  # 直接使用getenv方法来获取环境变量的值
    if value is not None:
        results = []
        for v in value.split(delimiter):
            if v.strip() != "":
                results.append(v.strip())
        results = results[:count] if count != -1 else results
        if shuffle:
            random.shuffle(results)
        return results
    else:
        return default if default is not None else []


def getInt(name: str, default: int = 0) -> int:
    """
    从环境变量获取一个整数。

    :param name: 环境变量名称。
    :param default: 如果环境变量不存在，则返回此默认值，默认为0。
    :return: 环境变量的值，如果环境变量不存在，则返回默认值。
    """
    value = os.getenv(name)
    try:
        return int(value) if value is not None else default
    except:
        return default


def getFromFile(path: str, delimiter: str = "\n", default: any = [], count: int = -1, create=False) -> list:
    """ """
    if os.path.exists(path):
        file = open(path, "r")
        value = file.read()
        file.close()
        lines = value.split(delimiter)
        lines = [line.strip() for line in lines if line.strip() != ""]
        return lines[:count] if count != -1 else lines
    else:
        if create:
            file = open(path, "w")
            file.close()
        return default


def saveToFile(path: str, values: list, delimiter: str = "\n") -> None:
    """ """
    file = open(path, "w")
    file.write(delimiter.join(values))
    file.close()


def isRelease(key: str = "RELEASE") -> bool:
    """
    检查名为 'key' 的环境变量是否设置为表示“发布”状态的值。

    :param key: 环境变量的名称，默认为'RELEASE'。
    :return: 如果环境变量设置为'true', 'True', 或 '1'，则返回True；否则返回False。
    """
    return os.getenv(key, "").lower() in ["true", "1"]
