import random
import time
from typing import Tuple, Union

import pytweening
import win32gui

from src.sotiRPA._uiautomation import uiautomation as uia
from src.sotiRPA._uiautomation import OPERATION_WAIT_TIME, Logger, MAX_MOVE_SECOND, SetCursorPos, GetCursorPos


def get_retry_args(error_args):
    if error_args is None or error_args == 'stop':
        retry_args = {'retry_num': 0, 'retry_interval': 0}

    elif error_args == 'ignore':
        retry_args = {'retry_num': 0, 'retry_interval': 0}

    elif isinstance(error_args, dict):
        if 'retry_num' in error_args and 'retry_interval' in error_args:
            retry_args = error_args
        else:
            raise ValueError('error_args参数错误 -- 参数字典中没有retry_num和retry_interval键值对')

    else:
        raise ValueError('error_args参数错误 -- 无效参数')

    return retry_args


def set_point(rect: Tuple[int, int, int, int], point: Union[str, dict], locator=None):
    """
    目标元素的部位

    Args:
        locator: 目标元素
        rect: 元素矩阵
        point: {'ratio_x': 0.5, 'ratio_y': 0.5, 'offset_x': 0, 'offset_y': 0}
    """

    left, top, right, bottom = rect
    width = right - left
    height = bottom - top

    x, y, is_clickable = locator.GetClickablePoint()
    if not is_clickable:
        raise '元素不在屏幕可见范围'

    if point == 'visible':
        x = x
        y = y

    elif point == 'centre':  # 中心点
        x = left + int(width * 0.5)
        y = top + int(height * 0.5)

    elif point == 'random':  # 随机点
        x = round(random.uniform(0, width - 1))
        y = round(random.uniform(0, height - 1))

    elif isinstance(point, dict):  # 自定义点
        x = left + int(width * point['ratio_x']) + point['offset_x']
        y = top + int(height * point['ratio_y']) + point['offset_y']

    else:
        raise ValueError('point参数错误 -- 无效参数')

    return x, y


def move_to(x: int, y: int, wait_time: float = OPERATION_WAIT_TIME) -> None:
    """
    移动
    """
    cur_x, cur_y = GetCursorPos()
    for x, y in pytweening.iterEaseOutExpo(cur_x, cur_y, x, y, 0.015):
        SetCursorPos(int(x), int(y))
        time.sleep(0.01)

    time.sleep(wait_time)


def move_cursor_to_inner_pos(locator: uia.Control, x: int = None, y: int = None, ratioX: float = 0.5,
                             ratioY: float = 0.5,
                             simulateMove: bool = True) -> Tuple[int, int]:
    """
    Move cursor to control's internal position, default to center.
    x: int, if < 0, move to self.BoundingRectangle.right + x, if not None, ignore ratioX.
    y: int, if < 0, move to self.BoundingRectangle.bottom + y, if not None, ignore ratioY.
    ratioX: float.
    ratioY: float.
    simulateMove: bool.
    Return Tuple[int, int], two ints tuple (x, y), the cursor positon relative to screen(0, 0)
        after moving or None if control's width or height is 0.
    """
    rect = locator.BoundingRectangle
    if rect.width() == 0 or rect.height() == 0:
        Logger.ColorfullyLog(
            '<Color=Yellow>Can not move cursor</Color>. {}\'s BoundingRectangle is {}. SearchProperties: {}'.format(
                locator.ControlTypeName, rect, locator.GetColorfulSearchPropertiesStr()))
        return
    if x is None:
        x = rect.left + int(rect.width() * ratioX)
    else:
        x = (rect.left if x >= 0 else rect.right) + x
    if y is None:
        y = rect.top + int(rect.height() * ratioY)
    else:
        y = (rect.top if y >= 0 else rect.bottom) + y
    if simulateMove and MAX_MOVE_SECOND > 0:
        move_to(x, y, wait_time=0)
    else:
        SetCursorPos(x, y)
    return x, y


def drag_and_drop(x1: int,
                  y1: int,
                  x2: int,
                  y2: int,
                  wait_time: float = OPERATION_WAIT_TIME):
    """拖拽"""
    uia.PressMouse(x1, y1, waitTime=0.05)
    move_to(x2, y2, wait_time=0.05)
    uia.ReleaseMouse(wait_time)


def auxiliary_key_press(auxiliary_key, vk_dict):
    """辅助按键压"""
    import win32api

    # 辅助按键
    if auxiliary_key is None:
        pass
    elif auxiliary_key in vk_dict:
        win32api.keybd_event(vk_dict[auxiliary_key], 0, 0, 0)  # 按下
    else:
        raise ValueError('auxiliary_key参数错误 -- 无效参数')


def auxiliary_key_release(auxiliary_key, vk_dict):
    """辅助按键释放"""
    import win32api
    import win32con
    if auxiliary_key is None:
        pass
    elif auxiliary_key in vk_dict:
        win32api.keybd_event(vk_dict[auxiliary_key], 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键


def get_current_window_rect():
    """获取当前窗口矩阵"""
    hwnd = win32gui.GetForegroundWindow()
    rect = win32gui.GetWindowRect(hwnd)
    return rect
