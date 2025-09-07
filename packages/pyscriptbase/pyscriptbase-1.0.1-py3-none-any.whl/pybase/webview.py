import platform
from time import sleep
from . import env
from selenium import webdriver
from traceback import format_exc
import os
from pathlib import Path
from selenium.webdriver.common.by import By

ENV_NAME = "remote_selenium"


def buildDriver(options: webdriver.ChromeOptions, rm: bool = True) -> webdriver.Chrome:
    """
    获取一个WebDriver实例
    环境变量: remote_selenium 远程地址
    """
    remote = env.get(ENV_NAME)
    if rm and remote:
        return webdriver.Remote(command_executor=remote, options=options)
    else:
        return webdriver.Chrome(options=options)


def getUserDir(project: str, user: str):
    """
    获取用户数据目录
    """
    if platform.system().lower() == "windows":
        dirs = ["E:", "cache", "selenium", project, user]
    else:
        dirs = [str(Path.home()), "cache", "selenium", project, user]
    return os.sep.join(dirs)


def clearUserData(driver: webdriver.Chrome):
    """
    清除用户数据
    """
    try:
        driver.get("chrome://settings/clearBrowserData")
        sleep(2)
        checkes = driver.find_elements(By.CLASS_NAME, "settings-checkbox")
        for checke in checkes:
            label = checke.text.lower()
            checked = checke.get_attribute("no-set-pref").lower()
            if label.find("cookie") >= 0 and checked == "checked":
                checke.click()
            elif label.find("cookie") <= 0 and checked != "checked":
                checke.click()
        clearButton = driver.find_element(By.ID, "clearButton")
        # clearButton.click()
    except:
        print("clearUserData", format_exc())
