import re
import subprocess
from typing import Literal, Union, Tuple
import os

import win32api
import win32con

import _uiautomation as uia
import time

from utils.tools import error_retry
from _uiautomation import PropertyId
from utils import Action, tools



class Window:
    """
    窗口

    retry:错误处理
        终止：'stop'
        忽略：'ignore'
        重试次数和重试间隔：(0, 0)
    """

    @classmethod
    def start(cls, path: str):
        """
        启动

        Args:
            path: 应用程序的路径
        """
        if os.path.splitext(path) == 'exe':
            subprocess.Popen(path)
        else:
            os.startfile(path)

    @classmethod
    def active(cls,
               locator: uia.Control,
               timeout: float = 20):
        """
        激活指定窗口使其在前台运行

        Args:
            locator: 定位的元素
            timeout: 等待超时时间（秒）【默认20秒】
        """
        if not locator.Exists(timeout):
            raise '元素不存在'

        Action.set_active(locator)

    @classmethod
    @error_retry
    def hover(cls,
              locator: uia.Control,
              *,
              is_simulate_move: bool = True,
              point: Union[Literal['visible', 'centre', 'random'], dict] = 'visible',
              timeout: float = 20,
              delay_after: float = 0.5,
              retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        鼠标悬停

         Args:
            locator: 定位的元素
            is_simulate_move: 是否模拟鼠标移动轨迹【默认模拟】
            point: 目标元素的部位，可选：中心点、随机点、自定义 【默认中心点】
            timeout: 等待超时时间（秒）【默认20秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            retry: 错误处理，终止、忽略、重试次数和重试间隔【默认终止 - 单选】
        """
        cls.active(locator, timeout)

        # 目标元素的部位
        rect = locator.BoundingRectangle
        x, y = Action.set_point((rect.left, rect.top, rect.right, rect.bottom), point, locator=locator)

        # 操作
        if is_simulate_move:
            Action.move_to(x, y, delay_after)

        return x, y

    @classmethod
    @error_retry
    def click(cls,
              locator,
              *,
              way: Literal['left', 'dbleft', 'middle', 'right'] = 'left',
              is_simulate_move: bool = False,
              point: Union[Literal['visible', 'centre', 'random'], dict] = 'visible',
              timeout: float = 20,
              delay_after: float = 0.5,
              retry: Union[Literal['stop', 'ignore'], tuple] = 'stop'):
        """
        点击窗口中的元素，如按钮、链接或其他任何元素

        Args:
            locator: 定位的元素
            way: 点击方式，可选：鼠标的左击、双击、中击、右击【默认点击 - 单选】
            is_simulate_move: 是否模拟鼠标移动轨迹【默认模拟】
            point: 目标元素的部位，可选：可见点、中心点、随机点、自定义 【默认可见点】
            timeout: 等待超时时间（秒）【默认20秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            retry: 错误处理，终止、忽略、重试次数和重试间隔【默认终止 - 单选】
        """
        x, y = cls.hover(locator, is_simulate_move=is_simulate_move, point=point, timeout=timeout)

        # 点击方式 和 执行后延迟（s）
        if way == 'left':
            uia.Click(x, y, delay_after)

        elif way == 'dbleft':
            uia.Click(x, y, uia.GetDoubleClickTime() * 1.0 / 2000)
            uia.Click(x, y, delay_after)

        elif way == 'middle':
            uia.MiddleClick(x, y, delay_after)

        elif way == 'right':
            uia.RightClick(x, y, delay_after)


    @classmethod
    @error_retry
    def input(cls,
              locator,
              text: str,
              *,
              interval: float = 0.01,
              is_simulate_move: bool = False,
              is_add_input: bool = False,
              is_input_method: bool = False,
              focus_delay_after: float = 0.5,
              timeout: float = 20,
              delay_after: float = 0.5,
              retry: Union[Literal['stop', 'ignore'], tuple] = 'stop') -> None:
        """
        在窗口的输入框中输入内容

        Args:
            locator: 定位的元素
            text: 输入的内容
            interval: 按键输入间隔（秒）【默认0.01秒】
            is_simulate_move: 是否模拟鼠标移动轨迹【默认模拟】
            is_add_input: 是否追加输入【默认不追加】
            is_input_method: 是否使用输入法【默认否】
            focus_delay_after: 获取焦点后延迟时间（秒）【默认延迟1秒】
            timeout: 等待超时时间（秒）【默认20秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            retry: 错误处理，终止、忽略、重试次数和重试间隔【单选】
        """
        # 输入前点击元素
        cls.click(locator, is_simulate_move=is_simulate_move)

        # 获取焦点延后
        time.sleep(focus_delay_after)

        # 追加输入
        if is_add_input:
            locator.SendKeys('{Ctrl}a')
            locator.SendKeys('{PageDown}')
        else:
            locator.SendKeys('{Ctrl}a')

        # 操作和执行后延迟（s）
        pattern = r'(\{|\})'  # 使用正则表达式匹配花括号，并使用捕获组
        replacement = r'{\1}'  # 替换函数，将匹配到的花括号用花括号括起来
        wrapped_text = re.sub(pattern, replacement, text)  # 使用re.sub进行替换
        locator.SendKeys(wrapped_text, interval=interval, waitTime=delay_after, charMode=not is_input_method)

    @classmethod
    @error_retry
    def get_text(cls,
                 locator: uia.Control,
                 get_method: Literal['auto', 'name', 'value', 'full_description'] = 'auto') -> str:
        """
        获取元素文本

        Args:
            locator: 定位的元素
            get_method: 获取模式，可选：自动识别、元素名称、元素值、元素完整描述【默认自动识别】
        """
        # 获取文本
        def auto(l):
            try:
                l: uia.EditControl
                if value := l.GetValuePattern().Value:
                    return value
            except AttributeError:
                pass

            if value := l.Name:
                return value

            if value := l.GetPropertyValue(PropertyId.FullDescriptionProperty):
                return value

            else:
                return ''

        method = {
            'auto': auto,
            'value': lambda l: l.GetValuePattern().Value,
            'name': lambda l: l.Name,
            'full_description': lambda l: l.GetPropertyValue(PropertyId.FullDescriptionProperty)
        }

        try:
            return method[get_method](locator)
        except AttributeError:
            return ''

    @classmethod
    @error_retry
    def set_window_position(cls,
                     locator: uia.Control,
                     position: Union[Literal['centre'], tuple] = 'centre',
                     *,
                     timeout: float = 20,
                     retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        移动窗口至指定位置

        Args:
            locator: 定位的元素
            position: 移动位置，可选 - 中心、自定义坐标【默认屏幕中心】
            timeout: 等待超时时间（秒）【默认20秒】
            retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        cls.active(locator, timeout)

        # 位置
        x, y = None, None
        if position == 'centre':
            locator: uia.WindowControl
            locator.MoveToCenter()
        elif isinstance(position, tuple):
            x, y = position[0], position[1]
        else:
            raise ValueError('position参数错误 -- 无效参数')

        # 操作
        top_control = locator.GetTopLevelControl()
        rect = top_control.BoundingRectangle
        top_control.MoveWindow(x=x, y=y, width=rect.width(), height=rect.height())

    @classmethod
    @error_retry
    def set_size(cls,
                 locator: uia.Control,
                 size: Union[Literal['normal', 'max', 'min'], Tuple[int, int]] = 'normal',
                 *,
                 timeout: float = 20,
                 retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        设置窗口大小

        Args:
            locator: 定位的元素
            size: 窗口大小，可选 - 还原正常化、最大化、最小化、自定义（width, height）【默认还原正常化】
            timeout: 等待超时时间（秒）【默认20秒】
            retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        cls.active(locator, timeout)

        # 设置大小
        width, height = None, None
        locator: uia.WindowControl
        if size == 'normal':
            locator.Restore()
        elif size == 'max':
            locator.Maximize()
        elif size == 'min':
            locator.Minimize()
        elif isinstance(size, tuple):
            width, height = size[0], size[1]
            top_control = locator.GetTopLevelControl()
            rect = top_control.BoundingRectangle
            top_control.MoveWindow(x=rect.left, y=rect.top, width=width, height=height)
        else:
            raise ValueError('position参数错误 -- 无效参数')



    @classmethod
    @error_retry
    def close(cls,
              locator: uia.Control,
              *,
              timeout: float = 20,
              retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        关闭窗口
        Args:
            locator: 定位的元素
            timeout: 等待超时时间（秒）【默认20秒】
            retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        cls.active(locator, timeout)

        locator: uia.WindowControl
        top_control = locator.GetTopLevelControl()
        top_control.GetWindowPattern().Close()

    @classmethod
    @error_retry
    def set_top_most(cls,
                     locator: uia.WindowControl,
                     is_top_most: bool = True,
                     *,
                     timeout: float = 20,
                     retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        设置窗口置顶

        Args:
            locator: 定位的元素
            is_top_most: 是否置顶窗口【默认置顶】
            timeout: 等待超时时间（秒）【默认20秒】
            retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        cls.active(locator, timeout)

        # 操作
        locator.SetTopmost(isTopmost=is_top_most)

    @classmethod
    @error_retry
    def drag_and_drop(cls,
                      locator: uia.Control,
                      target: Union[uia.Control, Tuple[int, int]],
                      *,
                      timeout: float = 20,
                      delay_after: float = 0.5,
                      retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        元素拖拽
        Args:
            locator: 定位的元素
            target: 拖拽的目标，可选 - 定位的元素、坐标
            timeout: 等待超时时间（秒）【默认20秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            retry: 错误处理，终止、忽略、重试次数和重试间隔【单选】
        """
        cls.active(locator, timeout)

        x1, y1 = locator.GetPosition()
        if isinstance(target, tuple):
            x2, y2 = target
        else:
            Action.set_active(target)
            x2, y2 = target.GetPosition()

        # 操作
        Action.drag_and_drop(x1, y1, x2, y2, wait_time=delay_after)

    @classmethod
    @error_retry
    def set_check(cls,
                  locator: uia.Control,
                  is_check: bool,
                  *,
                  timeout: float = 20,
                  delay_after: float = 0.5,
                  retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        将窗口中的复选框设置成勾选或者不勾选
        Args:
            locator: 定位的元素
            is_check: 是否勾选复选框
            timeout: 等待超时时间（秒）【默认20秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            retry: 错误处理，终止、忽略、重试次数和重试间隔【单选】
        """
        cls.active(locator, timeout)

        # 操作
        if isinstance(locator, uia.CheckBoxControl):  # 多选框
            locator: uia.CheckBoxControl
            check = locator.GetTogglePattern()
            if not check.ToggleState and is_check:
                check.Toggle(waitTime=delay_after)

            elif check.ToggleState and not is_check:
                check.Toggle(waitTime=delay_after)

        elif isinstance(locator, uia.RadioButtonControl):  # 单选框
            locator: uia.RadioButtonControl
            radio = locator.GetSelectionItemPattern()
            if not radio.IsSelected and is_check:
                radio.Select(waitTime=delay_after)

            elif radio.IsSelected and not is_check:
                radio.Select(waitTime=delay_after)

        else:
            raise TypeError('此元素不支持勾选操作')

    @classmethod
    @error_retry
    def set_select(cls,
                   locator: uia.ComboBoxControl,
                   text: str,
                   *,
                   is_simulate_move: bool = True,
                   timeout: float = 20,
                   retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        设置窗口中下拉框的选中项

        Args:
            locator: 定位的元素
            text: 下拉框选择的文本
            is_simulate_move: 是否模拟鼠标移动轨迹【默认模拟】
            timeout: 等待超时时间（秒）【默认20秒】
            retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        cls.active(locator, timeout)
        # 操作
        locator.Select(text, simulateMove=is_simulate_move)

    @classmethod
    @error_retry
    def wheel(cls,
              locator: uia.Control,
              target: uia.Control,
              way: Union[Literal['up', 'down']],
              *,
              interval: float = 0.05,
              auxiliary_key: Union[Literal["Alt", "Ctrl", "Shift", "Win"], None] = None,
              is_simulate_move: bool = True,
              duration: float = 10,
              timeout: float = 20,
              delay_after: float = 0.5,
              retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        滚轮

        Args:
            locator: 定位的元素
            target: 寻找的目标元素
            way: 滚轮滚动方式，可选 - 向下、向上
            interval: 滚动间隔时间（秒）【默认0.05秒滚动一次】
            auxiliary_key: 辅助按键【默认不使用】
            is_simulate_move: 是否模拟鼠标移动轨迹【默认模拟】
            duration: 滚动持续超时时间（秒）【默认10秒】
            timeout: 等待超时时间（秒）【默认20秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        vk_dict = {
            'Alt': 18,
            'Ctrl': 17,
            'Shift': 16,
            'Win': 91,
        }  # 辅助按键表
        try:
            cls.active(locator, timeout)

            # 辅助按键
            if auxiliary_key is None:
                pass
            elif auxiliary_key in vk_dict:
                win32api.keybd_event(vk_dict[auxiliary_key], 0, 0, 0)  # 按下
            else:
                raise ValueError('auxiliary_key参数错误 -- 无效参数')

            # 操作
            Action.move_cursor_to_inner_pos(locator, simulateMove=is_simulate_move)
            sotiRPA._uiautomation.uiautomation.SetGlobalSearchTimeout(0.01)

            locator_rect = locator.BoundingRectangle
            locator_height_half = locator_rect.height() / 2  # 高度的一半
            locator_centre_y = locator_rect.top + locator_height_half  # 元素y轴中心点

            visible_count = 0
            temp = {'current_centre_y': None}
            if way == 'up':  # 向上滚动滚轮
                s = time.time()
                while time.time() - s <= duration:
                    try:
                        rect = target.BoundingRectangle
                        target_centre_y = rect.top + rect.height() / 2  # 目标元素的y轴中心点

                        if (rect.width() or rect.height()) and locator_centre_y <= target_centre_y:  # 向上滚轮后，看见并经过元素中心y轴
                            break

                        elif temp['current_centre_y'] == target_centre_y and visible_count == 3:  # 滚动最顶层，元素位置不变，稳定3次
                            break

                        elif temp['current_centre_y'] == target_centre_y:  # 记录稳定次数
                            visible_count += 1

                        elif rect.width() or rect.height():  # 看见滚动
                            temp['current_centre_y'] = target_centre_y
                            uia.WheelUp(interval=interval, waitTime=0)

                        else:  # 看不见，滚动
                            uia.WheelUp(interval=interval, waitTime=0)

                    except LookupError:
                        uia.WheelUp(interval=interval, waitTime=0)
                        continue
                else:
                    raise LookupError('向上滚动滚轮未找到元素')

            elif way == 'down':  # 向下滚动滚轮
                s = time.time()
                while time.time() - s <= duration:
                    try:
                        rect = target.BoundingRectangle
                        target_centre_y = rect.top + rect.height() / 2  # 目标元素的y轴中心点

                        if (
                                rect.width() or rect.height()) and locator_centre_y >= target_centre_y:  # 向下滚轮后，看见并经过元素中心y轴
                            break

                        elif temp[
                            'current_centre_y'] == target_centre_y and visible_count == 3:  # 滚动最底层，元素位置不变，稳定3次
                            break

                        elif temp['current_centre_y'] == target_centre_y:  # 记录稳定次数
                            visible_count += 1

                        elif rect.width() or rect.height():  # 看见滚动
                            temp['current_centre_y'] = target_centre_y
                            uia.WheelDown(interval=interval, waitTime=0)

                        else:  # 看不见，滚动
                            uia.WheelDown(interval=interval, waitTime=0)

                    except LookupError:
                        uia.WheelDown(interval=interval, waitTime=0)
                        continue
                else:
                    raise LookupError('向下滚动滚轮未找到元素')

            time.sleep(delay_after)
            return

        finally:
            if auxiliary_key is None:
                pass
            elif auxiliary_key in vk_dict:
                win32api.keybd_event(vk_dict[auxiliary_key], 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键

            sotiRPA._uiautomation.uiautomation.SetGlobalSearchTimeout(10)

    @classmethod
    @error_retry
    def screenshot(cls,
                   locator: uia.Control,
                   save_to: Union[Literal['clipboard'], str],
                   *,
                   extend: Tuple[int, int, int, int] = (0, 0, 0, 0),
                   timeout: float = 20,
                   retry: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        元素截图

        Args:
            locator: 定位的元素
            save_to: 图片保存的地方，剪贴板、文件路径
            extend: 截图范围扩展，正数向外扩展，负数向内扩展【默认不扩展】
            timeout: 等待超时时间（秒）【默认20秒】
            retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        from PIL import ImageGrab
        from io import BytesIO
        import win32clipboard
        cls.active(locator, timeout)

        # 操作
        rect = locator.BoundingRectangle
        scope = (rect.left - extend[0], rect.top - extend[1], rect.right + extend[2], rect.bottom + extend[3])
        image = ImageGrab.grab(scope)

        if save_to == 'clipboard':  # 图片保存剪切板
            output = BytesIO()
            image.save(output, 'BMP')
            data = output.getvalue()[14:]
            output.close()
            tools.send_msg_to_clip(win32clipboard.CF_DIB, data)

        else:  # 图片保存路径
            image.save(save_to)


    @classmethod
    @error_retry
    def is_exist(cls,
                 locator: uia.Control,
                 *,
                 timeout: float = 20,
                 retry: Union[Literal['stop', 'ignore'], dict] = 'stop') -> bool:
        """
        等待窗口中元素出现或消失，再执行接下来操作

        Args:
            locator: 定位的元素
            timeout: 等待超时时间（秒）【默认20秒】
            retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        Returns:
            True存在，False不存在
        """
        # 等待元素存在（s）
        if locator.Exists(maxSearchSeconds=timeout):
            return True
        else:
            return False
