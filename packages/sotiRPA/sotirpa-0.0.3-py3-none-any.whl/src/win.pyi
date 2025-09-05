from ._uiautomation import uiautomation as uia
from ._uiautomation.uiautomation import PropertyId as PropertyId
from .utils import Action as Action, tools as tools
from typing import Literal

def start(path: str):
    """
    启动

    Args:
        path: 应用程序的路径
    """
def active(locator, timeout: float = 20):
    """
    激活指定窗口使其在前台运行

    Args:
        locator: 定位的元素
        timeout: 等待超时时间（秒）【默认20秒】
    """
def hover(locator, *, is_simulate_move: bool = True, point: Literal['visible', 'centre', 'random'] | dict = 'visible', timeout: float = 20, delay_after: float = 0.5, retry: Literal['stop', 'ignore'] | dict = 'stop'):
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
def click(locator, *, way: Literal['left', 'dbleft', 'middle', 'right'] = 'left', is_simulate_move: bool = False, point: Literal['visible', 'centre', 'random'] | dict = 'visible', timeout: float = 20, delay_after: float = 0.5, retry: Literal['stop', 'ignore'] | tuple = 'stop'):
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
def input(locator, text: str, *, interval: float = 0.01, is_simulate_move: bool = False, is_add_input: bool = False, is_input_method: bool = False, focus_delay_after: float = 0.5, timeout: float = 20, delay_after: float = 0.5, retry: Literal['stop', 'ignore'] | tuple = 'stop') -> None:
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
def get_text(locator, get_method: Literal['auto', 'name', 'value', 'full_description'] = 'auto') -> str:
    """
    获取元素文本

    Args:
        locator: 定位的元素
        get_method: 获取模式，可选：自动识别、元素名称、元素值、元素完整描述【默认自动识别】
    """
def set_window_position(locator, position: Literal['centre'] | tuple = 'centre', *, timeout: float = 20, retry: Literal['stop', 'ignore'] | dict = 'stop'):
    """
    移动窗口至指定位置

    Args:
        locator: 定位的元素
        position: 移动位置，可选 - 中心、自定义坐标【默认屏幕中心】
        timeout: 等待超时时间（秒）【默认20秒】
        retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
    """
def set_size(locator, size: Literal['normal', 'max', 'min'] | tuple[int, int] = 'normal', *, timeout: float = 20, retry: Literal['stop', 'ignore'] | dict = 'stop'):
    """
    设置窗口大小

    Args:
        locator: 定位的元素
        size: 窗口大小，可选 - 还原正常化、最大化、最小化、自定义（width, height）【默认还原正常化】
        timeout: 等待超时时间（秒）【默认20秒】
        retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
    """
def close(locator, *, timeout: float = 20, retry: Literal['stop', 'ignore'] | dict = 'stop'):
    """
    关闭窗口
    Args:
        locator: 定位的元素
        timeout: 等待超时时间（秒）【默认20秒】
        retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
    """
def set_top_most(locator, is_top_most: bool = True, *, timeout: float = 20, retry: Literal['stop', 'ignore'] | dict = 'stop'):
    """
    设置窗口置顶

    Args:
        locator: 定位的元素
        is_top_most: 是否置顶窗口【默认置顶】
        timeout: 等待超时时间（秒）【默认20秒】
        retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
    """
def drag_and_drop(locator, target: uia.Control | tuple[int, int], *, timeout: float = 20, delay_after: float = 0.5, retry: Literal['stop', 'ignore'] | dict = 'stop'):
    """
    元素拖拽
    Args:
        locator: 定位的元素
        target: 拖拽的目标，可选 - 定位的元素、坐标
        timeout: 等待超时时间（秒）【默认20秒】
        delay_after: 执行后延迟时间【默认延迟0.5秒】
        retry: 错误处理，终止、忽略、重试次数和重试间隔【单选】
    """
def set_check(locator, is_check: bool, *, timeout: float = 20, delay_after: float = 0.5, retry: Literal['stop', 'ignore'] | dict = 'stop'):
    """
    将窗口中的复选框设置成勾选或者不勾选
    Args:
        locator: 定位的元素
        is_check: 是否勾选复选框
        timeout: 等待超时时间（秒）【默认20秒】
        delay_after: 执行后延迟时间【默认延迟0.5秒】
        retry: 错误处理，终止、忽略、重试次数和重试间隔【单选】
    """
def set_select(locator: uia.ComboBoxControl, text: str, *, is_simulate_move: bool = True, timeout: float = 20, retry: Literal['stop', 'ignore'] | dict = 'stop'):
    """
    设置窗口中下拉框的选中项

    Args:
        locator: 定位的元素
        text: 下拉框选择的文本
        is_simulate_move: 是否模拟鼠标移动轨迹【默认模拟】
        timeout: 等待超时时间（秒）【默认20秒】
        retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
    """
def wheel(locator, target, way: Literal['up', 'down'], *, interval: float = 0.05, auxiliary_key: Literal['Alt', 'Ctrl', 'Shift', 'Win'] | None = None, is_simulate_move: bool = True, duration: float = 10, timeout: float = 20, delay_after: float = 0.5, retry: Literal['stop', 'ignore'] | dict = 'stop'):
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
def screenshot(locator, save_to: Literal['clipboard'] | str, *, extend: tuple[int, int, int, int] = (0, 0, 0, 0), timeout: float = 20, retry: Literal['stop', 'ignore'] | dict = 'stop'):
    """
    元素截图

    Args:
        locator: 定位的元素
        save_to: 图片保存的地方，剪贴板、文件路径
        extend: 截图范围扩展，正数向外扩展，负数向内扩展【默认不扩展】
        timeout: 等待超时时间（秒）【默认20秒】
        retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
    """
def is_exist(locator, *, timeout: float = 20, retry: Literal['stop', 'ignore'] | dict = 'stop') -> bool:
    """
    等待窗口中元素出现或消失，再执行接下来操作

    Args:
        locator: 定位的元素
        timeout: 等待超时时间（秒）【默认20秒】
        retry: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
    Returns:
        True存在，False不存在
    """
