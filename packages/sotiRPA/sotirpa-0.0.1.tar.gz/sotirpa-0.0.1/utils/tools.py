import logging
import time
import traceback
from pathlib import Path
from functools import wraps

import psutil


def get_path(path):
    return str(Path(__file__).parent.parent / path)


def cwd_path(path):
    return str(Path.cwd() / path)


def error_log(func):
    """错误处理"""

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger()
            file_handler = logging.FileHandler('error.log', encoding="utf-8")
            file_handler.setLevel(logging.ERROR)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \n %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            error_msg = traceback.format_exc()
            logger.error(error_msg)

    return wrapper


def send_msg_to_clip(type_data, msg):
    """
    操作剪贴板分四步：
    1. 打开剪贴板：OpenClipboard()
    2. 清空剪贴板，新的数据才好写进去：EmptyClipboard()
    3. 往剪贴板写入数据：SetClipboardData()
    4. 关闭剪贴板：CloseClipboard()

    :param type_data: 数据的格式，
    unicode字符通常是传 win32con.CF_UNICODETEXT
    :param msg: 要写入剪贴板的数据
    """
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(type_data, msg)
    win32clipboard.CloseClipboard()


def check_process(process_name):
    """判断程序是否在运行"""
    # 遍历所有正在运行的进程
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # 检查进程名是否匹配
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except:
            return True


def _get_retry_args(error_args):
    if error_args is None or error_args == 'stop':
        retry_args = (0, 0)

    elif error_args == 'ignore':
        retry_args = (0, 0)

    elif isinstance(error_args, tuple):
        retry_args = error_args

    else:
        raise ValueError('error_args参数错误 -- 无效参数')

    return retry_args


def error_retry(func):
    """装饰器 - 错误处理"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        retry = kwargs.get('retry')
        retry_args = _get_retry_args(retry)
        retry_num = retry_args[0]
        retry_interval = retry_args[1]
        for i in range(retry_num + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if retry == 'ignore':
                    pass
                elif retry == 'stop':
                    raise e
                elif i < retry_num:  # 重试
                    time.sleep(retry_interval)
                    continue
                else:
                    raise e

    return wrapper


def get_webtime(host):
    import http.client
    import time, datetime
    conn = http.client.HTTPConnection(host)
    conn.request("GET", "/")
    r = conn.getresponse()
    ts = r.getheader('date')
    ltime = time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
    ttime = time.localtime(time.mktime(ltime) + 8 * 60 * 60)
    date = datetime.datetime(int(ttime.tm_year), int(ttime.tm_mon), int(ttime.tm_mday), int(ttime.tm_hour),
                             int(ttime.tm_min), int(ttime.tm_sec))

    return date