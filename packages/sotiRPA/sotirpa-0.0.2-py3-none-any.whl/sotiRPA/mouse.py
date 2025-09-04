"""鼠标"""
import ctypes.wintypes
import time
from typing import Union, Literal

import pytweening
import win32api
import win32con
import win32gui

from utils import Action
from utils.tools import error_retry


class Mouse:
    """鼠标"""

    @classmethod
    def get_cursor_pos(cls):
        """获取当前鼠标位置"""
        point = ctypes.wintypes.POINT(0, 0)
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y

    @classmethod
    @error_retry
    def move(cls,
             x: int,
             y: int,
             *,
             relative_to: Union[Literal['screen', 'active_window']] = 'screen',
             is_simulate_move: bool = True,
             delay_after: float = 0.5,
             error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        鼠标移动

        Args:
            x: x坐标
            y: y坐标
            relative_to: 相对于的参照物【默认整个屏幕】
            is_simulate_move: 是否模拟鼠标移动轨迹【默认模拟】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            error_args: 错误处理，终止、忽略、重试次数和重试间隔【默认终止 - 单选】
        """
        # 参照物
        move_x, move_y = None, None
        if relative_to == 'screen':  # 屏幕
            move_x, move_y = x, y
        elif relative_to == 'active_window':  # 当前激活的窗口
            active_window_hwnd = win32gui.GetForegroundWindow()
            left, top, right, bottom = win32gui.GetWindowRect(active_window_hwnd)
            move_x = left + x
            move_y = top + y

        # 操作
        if is_simulate_move:
            cur_x, cur_y = cls.get_cursor_pos()  # 当前鼠标位置
            for x, y in pytweening.iterEaseOutExpo(cur_x, cur_y, move_x, move_y, 0.015):
                win32api.SetCursorPos((int(x), int(y)))
                time.sleep(0.01)
        else:
            win32api.SetCursorPos((move_x, move_y))

        # 执行后延迟（s）
        time.sleep(delay_after)

    @classmethod
    @error_retry
    def wheel(cls,
              scroll_num: int,
              way: Union[Literal["up", "down"]],
              *,
              interval: float = 0.05,
              auxiliary_key: Union[Literal["Alt", "Ctrl", "Shift", "Win"], None] = None,
              delay_after: float = 0.5,
              error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        鼠标滚轮

        Args:
            scroll_num: 滚动次数
            way: 滚动方式
            interval: 滚动间隔时间【默认0.05秒】
            auxiliary_key: 键盘辅助按键【默认不使用】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        vk_dict = {
            'Alt': 18,
            'Ctrl': 17,
            'Shift': 16,
            'Win': 91,
        }  # 辅助按键表
        try:
            # 辅助按键压
            Action.auxiliary_key_press(auxiliary_key, vk_dict)
            # 操作
            for _ in range(scroll_num):
                if way == 'up':
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120, 0)
                elif way == 'down':
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
                else:
                    ValueError('way参数错误 -- 无效参数')
                time.sleep(interval)

            # 执行后延迟（s）
            time.sleep(delay_after)

        finally:
            # 辅助按键释放
            Action.auxiliary_key_release(auxiliary_key, vk_dict)

    @classmethod
    @error_retry
    def click(cls,
              way: Union[Literal['click', 'dbclick', 'press', 'release']] = 'click',
              button: Union[Literal['left', 'right', 'middle']] = 'left',
              *,
              auxiliary_key: Union[Literal["Alt", "Ctrl", "Shift", "Win"], None] = None,
              delay_after: float = 0.5,
              error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """点击"""
        vk_dict = {
            'Alt': 18,
            'Ctrl': 17,
            'Shift': 16,
            'Win': 91,
        }  # 辅助按键表
        try:
            # 辅助按键
            Action.auxiliary_key_press(auxiliary_key, vk_dict)

            button = button.upper()
            press_way = eval(f'win32con.MOUSEEVENTF_{button}DOWN')
            release_way = eval(f'win32con.MOUSEEVENTF_{button}UP')
            if way == 'press':
                win32api.mouse_event(press_way, 0, 0)

            elif way == 'click':
                win32api.mouse_event(press_way, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(release_way, 0, 0)

            elif way == 'dbclick':
                win32api.mouse_event(press_way, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(release_way, 0, 0)
                time.sleep(ctypes.windll.user32.GetDoubleClickTime() * 1.0 / 2000)
                win32api.mouse_event(press_way, 0, 0)
                time.sleep(0.05)
                win32api.mouse_event(release_way, 0, 0)

            elif way == 'release':
                win32api.mouse_event(release_way, 0, 0)

            else:
                raise ValueError('way参数错误 -- 无效参数')

            # 执行后延迟（s）
            time.sleep(delay_after)

        finally:
            # 辅助按键压
            Action.auxiliary_key_release(auxiliary_key, vk_dict)

    @classmethod
    @error_retry
    def move_to_click(cls,
                      x: int,
                      y: int,
                      button: Union[Literal['left', 'right', 'middle']] = 'left',
                      way: Union[Literal['click', 'dbclick', 'press', 'release']] = 'click',
                      *,
                      is_simulate_move: bool = True,
                      auxiliary_key: Union[Literal["Alt", "Ctrl", "Shift", "Win"], None] = None,
                      delay_after: float = 0.5,
                      error_args: Union[Literal['stop', 'ignore'], dict] = 'stop',
                      ):
        """移动去点击"""
        cls.move(x, y, is_simulate_move=is_simulate_move, delay_after=delay_after)
        cls.click(button, way, auxiliary_key=auxiliary_key, delay_after=delay_after)
