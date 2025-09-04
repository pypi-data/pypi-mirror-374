import random
import time

from typing import Literal, Union, Sequence, Optional

from playwright.sync_api import sync_playwright, Page, Locator, TimeoutError, Error, BrowserContext, Browser

from utils import tools
from utils.tools import error_retry
from _DrissionPage import ChromiumPage


class Web:
    """
    浏览器

    error_args:错误处理
    终止：'stop'
    忽略：'ignore'
    重试次数和重试间隔：
    {'retry_num': 0, 'retry_interval': 0}
    """
    browser: Browser = None
    context: BrowserContext = None
    page: Page = None

    @classmethod
    def _chromium_page(cls, path: str = None, port: int = 9222):
        """
        启动chrome
        Args:
            path: 浏览器驱动路径
            port: 端口，默认值为9222端口
        Return:
            RPA能使用的page
        """
        # 尝试连接浏览器
        pw = sync_playwright().start()
        try:
            cls.browser = pw.chromium.connect_over_cdp(f"http://localhost:{port}")
        except TimeoutError:
            raise TimeoutError(f'连接超时，{port}端口被占用，请更改端口再次重试')
        except:
            pass
        # 连接不上浏览器
        if not cls.browser:
            if not tools.check_process('chrome.exe'):  # 检查chrome浏览器是否启动
                if tools.is_port_in_use(port):
                    raise OSError(f'{port}端口被占用，请更换其他端口')

                from subprocess import Popen, PIPE, STDOUT
                if path:
                    args = [path]
                else:
                    args = ['start', 'chrome']
                args.append(f'--remote-debugging-port={port}')
                process = Popen(args, stdout=PIPE, stderr=STDOUT, shell=True)
                if process.poll() is None:
                    pass
                s = time.time()
                while time.time() - s <= 20:
                    try:
                        cls.browser = pw.chromium.connect_over_cdp(f"http://localhost:{port}", timeout=0)
                        if cls.browser:
                            break
                    except:
                        pass
                else:
                    raise Error(f'连接浏览器失败')
            else:
                raise Error(f'连接{port}端口错误，请关闭所有chrome浏览器再次重试')

        #  连接端口浏览器
        cls.context = cls.browser.contexts[0]
        cls.page: Page = cls.context.pages[-1]

        return cls.page

    @classmethod
    def chromium_page(cls, port: int = 9222):
        """
        启动chrome
        Args:
            port: 端口，默认值为9222端口
        Return:
            RPA能使用的page
        """
        try:
            ds_page = ChromiumPage(addr_or_opts=port)
            activate_tab = ds_page.get_tab()
            ds_page.browser.connect_to_page()
            pw = sync_playwright().start()
            cls.browser = pw.chromium.connect_over_cdp(f"http://localhost:{port}")
            for i in cls.browser.contexts:
                cls.context = i
                break
            cls.page = cls.switch_to_page(cls.context, title=activate_tab.title)
        except:
            raise Error(f'连接{port}端口错误，请关闭所有chrome浏览器再次重试')

        return cls.page

    @classmethod
    def connect_page(cls, page: Page = None) -> Page:
        """
        连接page
        Args:
            page: 页面对象
        Returns:
            RPA能使用的page
        """
        cls.page: Page = page
        return cls.page

    @classmethod
    def goto_new_page(cls,
                      context: BrowserContext,
                      locator: Locator,
                      way: Union[Literal['click', 'dbclick']],
                      timeout: float = 20) -> Page:
        """
        跳转新页面
        Args:
            context: 浏览器上下文
            locator: 操作目标
            way: 点击方式，可选：鼠标的点击、双击、中击、右击【默认点击 - 单选】
            timeout: 等待元素存在（s），默认20秒
        Returns:
            返回跳转新页面的page对象
        """
        with context.expect_page() as new_page_info:
            if way == 'click':
                locator.click(timeout=timeout * 1000)
            elif way == 'dbclick':
                locator.click(click_count=2, timeout=timeout * 1000)
        return new_page_info.value

    @classmethod
    def iframe_page(cls, selector_or_index: Union[str, int]):
        """
        生成iframe的page
        Args:
            selector_or_index: iframe标签的选择器 或者 iframe标签的索引
        Returns:
            返回iframe框架的page
        """

        if isinstance(selector_or_index, str):
            frame_page = cls.page.frame_locator(selector_or_index)
        elif isinstance(selector_or_index, int):
            frame_page = cls.page.frames[selector_or_index]
        else:
            raise ValueError('selector_or_index参数错误 -- 无效参数')
        return frame_page

    @classmethod
    def print_iframe_tree(cls, selector=None):
        """
        打印iframe树
        selector: 需要寻找的元素
        """
        index = -1

        def print_tree(frame, indent):
            iframe_texts = []
            if frame.name:
                iframe_texts.append(u'name="{}"'.format(frame.name))
            if frame.url:
                iframe_texts.append(u'src="{}"'.format(frame.url))
            nonlocal index
            index += 1
            print(indent + '<iframe' + ' ' + ' '.join(iframe_texts) + '>' + ' [' + str(index) + ']')
            if selector:
                if frame.is_visible(selector):
                    print(indent + "   | " + '元素')

            for child in frame.child_frames:
                print_tree(child, indent + "   | ")

        print_tree(cls.page.main_frame, "")

    @staticmethod
    def switch_to_page(context, title=None, url=None):
        """切换指定title名称 或 url 的标签页"""
        for item_page in context.pages:
            if title:
                if title in item_page.title():
                    # 激活当前选项卡
                    item_page.bring_to_front()
                    return item_page
            elif url:
                if url in item_page.url:
                    # 激活当前选项卡
                    item_page.bring_to_front()
                    return item_page
        else:
            print("没有找到title或者url")
        return context.pages[0]

    @classmethod
    @error_retry
    def goto(cls,
             url: str,
             wait_until: Union[Literal["commit", "domcontentloaded", "load", "networkidle"], None] = None,
             timeout: float = 20,
             error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        打开网页
        Args:
            url: 网页地址
            wait_until: 直到加载到什么状态为止
            timeout: 等待元素存在（s），默认20秒
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        cls.page.goto(url=url, wait_until=wait_until, timeout=timeout * 1000)
        with open(tools.get_path(r'script/web_automation/stealth.min.js'), 'r') as f:
            js = f.read()
            cls.page.add_init_script(js)
        js = """// 保存原始的console.debug方法
                var originalDebug = console.debug;
                
                // 覆盖console.debug方法
                console.debug = function() {
                  // 这里可以添加你想要执行的代码，或者什么都不做
                  // 这样就不会执行原始的console.debug方法了
                };
                
                // 现在调用console.debug将不会在控制台输出任何内容
                console.debug('This will not appear in the console.');
                """
        cls.page.evaluate(js)

    @staticmethod
    @error_retry
    def input(locator: Locator,
              text: str,
              *,
              interval: float = 0.02,
              is_add_input: bool = False,
              focus_delay: float = 0.5,
              timeout: float = 20,
              delay_after: float = 0.5,
              error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        在网页的输入框中输入内容
        Args:
            locator: 操作目标
            text: 填写要输入的内容
            interval: 输入间隔（s），默认0.02秒
            is_add_input: 是否追加输入
            focus_delay: 获取焦点等待时间（s）， 默认1秒
            delay_after: 执行后延迟（s），默认1秒
            timeout: 等待元素存在（s），默认20秒
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        # 聚焦超时时间
        locator.focus()
        time.sleep(focus_delay)

        # 追加输入
        if is_add_input is False:
            locator.clear()

        # 操作
        locator.type(text, delay=interval * 1000, timeout=timeout * 1000)

        # 执行后延迟
        time.sleep(delay_after)

    @staticmethod
    @error_retry
    def click(locator: Locator,
              way: Union[Literal['click', 'dbclick']] = 'click',
              button: Union[Literal['left', 'right', 'middle']] = 'left',
              *,
              point: Union[Literal['visible', 'centre', 'random'], dict] = 'visible',
              auxiliary_key: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
              timeout: float = 20,
              delay_after: float = 0.5,
              error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        点击网页中的按钮、链接或者其它任何元素
        Args:
            locator: 操作目标
            way: 点击方式，可选：鼠标的点击、双击、中击、右击【默认点击 - 单选】
            button: 鼠标按钮
            point: 目标元素的部位，可选：可见点、随机点、自定义 【默认可见点】
            auxiliary_key: 辅助按键
            timeout: 等待超时时间，默认20秒，单位(s)
            delay_after: 执行后延迟，默认0.5秒，单位(s)
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        Examples:
            web.click(point={locator, point={'ratio_x': 0.5, 'ratio_y': 0.5, 'offset_x': -10, 'offset_y': 0}, auxiliary_key=['Alt', 'Shift'])
        """
        # 目标元素的部位
        if point == 'visible':  # 可见点
            position = None
        elif point == 'centre':  # 中心点
            box = locator.bounding_box()
            x = box['width'] / 2
            y = box['height'] / 2
            position = {'x': x, 'y': y}
        elif point == 'random':  # 随机点
            box = locator.bounding_box()
            width = box['width']
            height = box['height']
            x = round(random.uniform(0, width - 1))
            y = round(random.uniform(0, height - 1))
            position = {'x': x, 'y': y}
        elif isinstance(point, dict):
            box = locator.bounding_box()
            x = box['x'] + int(box['width'] * point['ratio_x']) + point['offset_x']
            y = box['y'] + int(box['height'] * point['ratio_y']) + point['offset_y']
            position = {'x': x, 'y': y}
        else:
            raise ValueError('point参数错误 -- 无效参数')

        if way == 'click':
            locator.click(modifiers=auxiliary_key, button=button, position=position, timeout=timeout * 1000)
        elif way == 'dbclick':
            locator.click(modifiers=auxiliary_key, button=button, click_count=2, position=position,
                          timeout=timeout * 1000)
        else:
            raise ValueError('way参数错误 -- 无效参数')

        # 执行后延迟
        time.sleep(delay_after)

    @classmethod
    @error_retry
    def hover(cls,
              locator: Locator,
              *,
              timeout: float = 20,
              delay_after: float = 0.5,
              error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        悬浮
        Args:
            locator: 操作目标
            timeout: 等待超时时间，默认30秒，单位(s)
            delay_after: 执行后延迟，默认1秒，单位(s)
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        locator.hover(timeout=timeout * 1000)
        # 执行后延迟
        cls.page.wait_for_timeout(delay_after * 1000)

    @classmethod
    @error_retry
    def set_check(cls,
                  locator: Locator,
                  is_check: bool,
                  *,
                  timeout: float = 20,
                  delay_after: float = 0.5,
                  error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        设置复选框，适合type为radio或checkbox

        Args:
            locator: 操作目标
            is_check: 是否勾选复选框
            timeout: 等待超时时间，默认30秒，单位(s)
            delay_after: 执行后延迟，默认1秒，单位(s)
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        locator.set_checked(is_check, timeout=timeout * 1000)

        # 执行后延迟
        cls.page.wait_for_timeout(delay_after * 1000)

    @classmethod
    @error_retry
    def wheel(cls,
              locator: Locator,
              target: Locator,
              way: Union[Literal['up', 'down']],
              *,
              interval: float = 0.5,
              duration: float = 30,
              timeout: float = 20,
              delay_after: float = 0.5,
              error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        滚轮
        Args:
            locator: 定位的元素
            target: 寻找的目标元素
            way: 滚轮滚动方式，可选 - 向下、向上
            interval: 滚动间隔时间（秒）【默认0.5秒滚动一次】
            duration: 滚动持续超时时间（秒）【默认30秒】
            timeout: 等待超时时间（秒）【默认20秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        way_dict = {
            'up': -120,
            'down': 120
        }
        # 操作
        locator.hover(timeout=timeout * 1000)
        if way_dict[way]:  # 滚动滚轮
            s = time.time()
            while time.time() - s <= duration:
                try:
                    rect = target.bounding_box(timeout=interval * 1000)
                    if rect['width'] and rect['height']:
                        target.scroll_into_view_if_needed(timeout=5000)
                        break
                    else:  # 看不见，滚动
                        cls.page.mouse.wheel(0, way_dict[way])
                except TimeoutError:
                    cls.page.mouse.wheel(0, way_dict[way])
            else:
                raise TimeoutError(f'滚动{duration}秒,未找到元素')
        else:
            raise ValueError('way参数错误 -- 无效参数')

        # 执行后延迟
        cls.page.wait_for_timeout(delay_after * 1000)

    @classmethod
    @error_retry
    def upload_file(cls,
                    locator: Locator,
                    file_path: str,
                    *,
                    error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        上传文件
        Args:
            locator: 操作目标
            file_path: 上传文件路径
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        with cls.page.expect_file_chooser() as fc_info:
            locator.click()

        file_chooser = fc_info.value
        file_chooser.set_files(file_path)

    @classmethod
    @error_retry
    def download_file(cls,
                      locator: Locator,
                      save_path: str,
                      *,
                      error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        下载文件
        Args:
            locator: 操作目标（css、xpath、playwright支持）
            save_path: 下载保存路径
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        with cls.page.expect_download() as download_info:
            locator.click()

        download = download_info.value
        download.save_as(save_path)

    @classmethod
    @error_retry
    def drag_and_drop(cls,
                      locator: Locator,
                      target: Locator,
                      *,
                      is_simulate_move: bool = False,
                      timeout: float = 20,
                      delay_after: float = 0.5,
                      error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        拖拽
        Args:
            locator: 操作目标
            target: 拖拽的目标
            is_simulate_move: 是否模拟鼠标移动轨迹【默认模拟】
            timeout: 等待超时时间（秒）【默认20秒】
            delay_after: 执行后延迟时间【默认延迟0.5秒】
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        if is_simulate_move:
            import pytweening
            try:
                box = locator.bounding_box(timeout=timeout * 1000)
                cur_x = box['x'] + (box['width'] / 2)
                cur_y = box['y'] + (box['height'] / 2)
                cls.page.mouse.move(cur_x, cur_y)
                cls.page.mouse.down()

                box = target.bounding_box(timeout=timeout * 1000)
                x = box['x'] + (box['width'] / 2)
                y = box['y'] + (box['height'] / 2)
                for x, y in pytweening.iterEaseOutExpo(cur_x, cur_y, x, y, 0.01):
                    cls.page.mouse.move(int(x), int(y))
            finally:
                cls.page.mouse.up()
        else:
            locator.drag_to(target, timeout=timeout * 1000)

        cls.page.wait_for_timeout(delay_after)

    @staticmethod
    def get_elem_info(locator: Locator,
                      content: Literal['text', 'attribute'] = 'text',
                      attribute_name: str = None,
                      timeout: float = 20):
        """
        获取元素信息
        Parameters:
            locator: 操作目标
            content: 内容选择 -- 获取元素文本（默认值），获取元素属性
            attribute_name: 属性名称 -- 获取元素属性时，必须填写
            timeout: 等待超时时间（ms），默认30秒
        """

        # 获取元素文本内容
        if content == 'text':
            locator.text_content(timeout=timeout * 1000)

        # 获取元素属性
        elif content == 'attribute':
            locator.get_attribute(attribute_name, timeout=timeout * 1000)

    @staticmethod
    @error_retry
    def wait(locator: Locator,
             state: Literal['visible', 'hidden'] = 'visible',
             *,
             timeout: float = 20,
             error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        等待
        Args:
            locator: 操作目标
            state: 状态。visible：等待元素显示, hidden：等待元素隐藏
            timeout: 等待超时时间（s），默认30秒
            error_args: 错误处理，可选，终止、忽略、重试次数和重试间隔【单选】
        """
        locator.wait_for(state=state, timeout=timeout * 1000)
