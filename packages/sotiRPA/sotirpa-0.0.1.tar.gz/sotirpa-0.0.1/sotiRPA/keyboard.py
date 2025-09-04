"""键盘"""
import platform
import sys
import time
from typing import Union, Literal

import _pyautogui
from utils.tools import error_retry

if sys.platform.startswith("java"):
    # from . import _pyautogui_java as platformModule
    raise NotImplementedError("Jython is not yet supported by PyAutoGUI.")
elif sys.platform == "darwin":
    from _pyautogui import _pyautogui_osx as platformModule
elif sys.platform == "win32":
    from _pyautogui import _pyautogui_win as platformModule
elif platform.system() == "Linux":
    from _pyautogui import _pyautogui_x11 as platformModule
else:
    raise NotImplementedError("Your platform (%s) is not supported by PyAutoGUI." % (platform.system()))


_pyautogui.FAILSAFE = False
_pyautogui.PAUSE = 0


class Keyboard:
    """键盘"""

    @staticmethod
    def get_keyboard_keys() -> list:
        """键盘按键"""
        return _pyautogui.KEYBOARD_KEYS

    @staticmethod
    @error_retry
    def tap(keys: Union[str, list],
            *,
            interval: float = 0.05,
            delay_after: float = 0.5,
            error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        敲击键盘
        Args:
            keys: 键盘按键
            interval: 输入间隔（秒）【默认0.05秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            error_args: 错误处理，终止、忽略、重试次数和重试间隔【单选】
        """
        if isinstance(keys, list):  # 如果为列表
            for key in keys:
                if key not in _pyautogui.KEY_NAMES:
                    raise ValueError(f'keys参数错误 -- {key}键无效')

            lowerKeys = []
            for s in keys:
                if len(s) > 1:
                    lowerKeys.append(s.lower())
                else:
                    lowerKeys.append(s)
            keys = lowerKeys

        elif isinstance(keys, str):  # 如果为字符串
            if keys not in _pyautogui.KEY_NAMES:
                raise ValueError(f'keys参数错误 -- {keys}键无效')

            elif len(keys) > 1:
                keys = keys.lower()
                keys = [keys]  # If keys is 'enter', convert it to ['enter'].

        else:
            raise ValueError(f'keys参数错误 -- 类型错误')

        # 操作
        for k in keys:
            platformModule._keyDown(k)
            platformModule._keyUp(k)
            time.sleep(float(interval))

        # 执行后延迟（秒）
        time.sleep(delay_after)

    @staticmethod
    @error_retry
    def hotkey(keys: list,
               *,
               delay_after: float = 0.5,
               error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        组合键

        Args:
            keys: 键盘按键
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            error_args: 错误处理，终止、忽略、重试次数和重试间隔【单选】
        """
        # 操作
        for k in keys:
            if len(k) > 1:
                k = k.lower()
            platformModule._keyDown(k)

        for k in reversed(keys):
            if len(k) > 1:
                k = k.lower()
            platformModule._keyUp(k)

        # 执行后延迟（秒）
        time.sleep(delay_after)




