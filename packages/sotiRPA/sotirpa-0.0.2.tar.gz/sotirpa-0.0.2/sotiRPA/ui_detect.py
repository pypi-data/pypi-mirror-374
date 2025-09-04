"""ui识别"""
from typing import Union, Literal

import pyscreeze
from PIL.Image import Image

from rpa.utils import Action
from rpa.utils.tools import error_retry


class UiDetect:

    @staticmethod
    @error_retry
    def get_image_point(image: Union[str, Image],
                        *,
                        region: Union[Literal['full_screen', 'active_window']] = 'full_screen',
                        grayscale: bool = False,
                        confidence: float = 0.999,
                        point: Union[Literal['centre', 'random'], dict] = 'centre',
                        error_args: Union[Literal['stop', 'ignore'], dict] = 'stop'):
        """
        获取图片坐标点
        Args:
            image: 图片路径
            region: 搜索范围
            grayscale: 灰度模式
            confidence: 图片识别精准度
            point: 图片的坐标点
            error_args: 错误处理，终止、忽略、重试次数和重试间隔【单选】
        """
        # 搜索区域
        search_region = None
        if region == 'full_screen':
            search_region = None
        elif region == 'active_window':
            search_region = Action.get_current_window_rect()
        else:
            ValueError(f'region参数错误 -- 非规定参数')

        # 识别图片矩阵
        rect = pyscreeze.locateOnScreen(image, region=search_region, grayscale=grayscale, confidence=confidence)
        left, top, right, bottom = rect.left, rect.top, rect.left + rect.width, rect.top + rect.height
        # 目标元素的部位
        x, y = Action.set_point((left, top, right, bottom), point)
        return x, y

    @staticmethod
    def ocr_code(image):
        """ocr验证码识别"""
        import ddddocr

        ocr = ddddocr.DdddOcr(show_ad=False)
        with open(image, 'rb') as f:
            img_bytes = f.read()
        code = ocr.classification(img_bytes)
        return code


