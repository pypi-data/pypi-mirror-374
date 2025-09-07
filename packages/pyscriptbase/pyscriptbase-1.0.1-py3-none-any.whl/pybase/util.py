from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
import random
import string


def generateRandomPhoneUA():
    # 手机设备品牌与型号
    devices = ["Samsung Galaxy S21", "Xiaomi Mi 11", "Google Pixel 6", "Huawei P40", "OPPO Reno5", "Vivo X60", "OnePlus 9"]

    # 操作系统版本
    os_versions = ["Android 11", "Android 12", "Android 13"]

    # 浏览器类型
    browsers = ["Chrome"]

    # 随机选择设备、操作系统和浏览器
    device = random.choice(devices)
    os_version = random.choice(os_versions)
    browser = random.choice(browsers)

    # 构建完整的User-Agent字符串
    ua_base = f"Mozilla/5.0 ({device}; Android {os_version}; Mobile) AppleWebKit"
    ua = f"{ua_base}/537.36 (KHTML, like Gecko) {browser}/{random.randint(80, 99)}.0.{random.randint(0, 99)} Mobile Safari/537.36"

    return ua


def generateRandomStr(len: int):
    return "".join(random.choices(string.ascii_letters + string.digits, k=len))


def getNextHourSeconds() -> float:
    # 获取当前时间
    now = datetime.now()
    # 计算下一小时的时间点
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    # 计算距离下一小时的总秒数
    seconds_until_next_hour = (next_hour - now).total_seconds()
    return seconds_until_next_hour


def formatTimestamp(ts: int | float | str = None) -> str:
    if isinstance(ts, int) or isinstance(ts, float):
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    elif ts == None:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    else:
        return ts


def formatDate(ts: int, split="") -> str:
    return datetime.fromtimestamp(ts).strftime(f"%Y{split}%m{split}%d")


def isLastDayOfMonth():
    today = date.today()
    next_day = today + timedelta(days=1)
    return next_day.month != today.month


def daysDifference(date_str: str) -> int:
    # 尝试将输入的日期字符串转换为datetime对象
    try:
        # 假设输入的日期格式是'yyyy-mm-dd'
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        # 如果日期格式不正确，返回错误信息或处理异常
        return 0

    # 获取今天的日期
    today = datetime.now().date()

    # 计算两个日期之间的天数差
    delta = today - input_date
    days_diff = delta.days

    return days_diff


def threadPool(func, args, num=5):
    # 启用线程池
    executor = ThreadPoolExecutor(max_workers=num)
    tasks = [executor.submit(func, arg, index + 1) for index, arg in enumerate(args)]
    for future in as_completed(tasks):
        data = future.result()
