import hashlib
import logging
import mimetypes
import os
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import cast
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import defaults

logger = logging.getLogger(__name__)

# DEFAULT_FILE_DOWNLOAD_MAX_RETRIES = 5
TEMP_DIR = tempfile.mkdtemp()
PDF_FILE_PATTERN = re.compile(r"(?i).*\.(pdf)$")


def cleanup(driver: WebDriver = None):  # type: ignore
    _cleanup_temp_dir(include_itself=True)
    if driver:
        driver.quit()


def create_webdriver(enable_performance_logs: bool = False,
                     enable_pdf_viewer: bool = True,
                     headless: bool = True):
    """创建 selenium Chrome web driver 实例

    Args:
        user_agent (str): 自定义 User Agent，通常来自 Settings
        enable_performance_logs (bool): 是否启用性能日志，启用后可以获取响应头等信息，默认禁用
        enable_pdf_viewer (bool): 是否启用pdf预览功能，默认启用
        headless (bool): 以无头模式启动浏览器
    Returns:
        WebDriver: 返回新建的 web driver
    Examples:
        >>> from scrapy_selenium_enhanced import downloader
        >>> driver = downloader.create_webdriver(enable_performance_logs=False, enable_pdf_viewer=False)
        >>> # get some urls...or using download() function
        >>> file_path = downloader.get("https://quotes.toscrape.com/author/Albert-Einstein/", driver=driver)
        >>> driver.quit()
    """
    # 初始化WebDriver
    executable_path = shutil.which("chromedriver")
    return webdriver.Chrome(
        service=Service(executable_path=executable_path) if executable_path else Service(
            ChromeDriverManager().install()),
        options=_chrome_options(enable_performance_logs,
                                enable_pdf_viewer, headless),
    )


def get(from_url: str,
        timeout: float = 30,
        # max_retries: int = DEFAULT_FILE_DOWNLOAD_MAX_RETRIES,
        driver: WebDriver = None):
    """ 下载目标 url，无论是网页还是附件

    Args:
        from_url (str): 下载地址
        timeout (float): 文件下载超时时间，单位: 秒
        # max_retries (int): 文件下载失败或超时后重试的最大次数
        driver (WebDriver): 传入则用提供的 web driver，否则会临时新建一个
    Returns:
        str: 下载后保存在本地的地址
    Examples:
        >>> from scrapy_selenium_enhanced import downloader
        >>> file_path = downloader.get("https://quotes.toscrape.com/author/Albert-Einstein/")
    """
    one_time_init = False

    logger.debug(f">>>>> Temporary download directory: {TEMP_DIR}")

    if driver is None:
        driver = create_webdriver(
            enable_performance_logs=False, enable_pdf_viewer=False)
        one_time_init = True

    # 清理临时下载目录
    _cleanup_temp_dir(include_itself=False)
    # 解析下载链接
    driver.get(from_url)

    try:
        # 处理下载文件
        # 1. pdf文件：浏览器会自动执行下载
        # 2. htm文档：需要使用js动态读取完整的文档内容
        if _target_is_pdf(from_url):
            logger.debug(f">>>>> Detecting downloading folder: {TEMP_DIR}")
            WebDriverWait(driver, timeout).until(
                lambda _: _is_file_ready())
            # 必须要等待浏览器将全部内容写入文件，否则部分文件会有一定概率读取不全
            time.sleep(1)
        else:
            WebDriverWait(driver, timeout, ignored_exceptions=[TimeoutException]).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.loading-bar.done")))
            Path(os.path.join(TEMP_DIR, _md5sum(from_url)) + '.html').write_bytes(
                driver.execute_script("return document.documentElement.outerHTML").encode('utf-8'))
    except TimeoutException:
        logger.warning(">>>>> Download failed with timeout exception.")

    if one_time_init:
        driver.quit()

    fetched_file_path = _most_recent_updated_file()
    logger.debug(f">>>>> Final download file path: {fetched_file_path}")
    return fetched_file_path


def _cleanup_temp_dir(include_itself: bool = True):
    """ 清理临时下载文件夹

    Args:
        include_itself (bool): True: 删除文件夹本身及其子文件；False: 删除所有子文件
    Examples:
        >>> _cleanup_temp_dir()
        >>> _cleanup_temp_dir(include_itself=False)
    """
    if include_itself:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    else:
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))


def _chrome_options(enable_performance_logs=False, enable_pdf_viewer=True, headless: bool = True):
    opt = Options()
    for arg in defaults.get_driver_arguments_with(defaults.USER_AGENT, headless):
        opt.add_argument(arg)

    # 启用性能日志，捕获网络请求和响应头
    if enable_performance_logs:
        opt.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # 禁用pdf预览插件
    # https://www.cnblogs.com/shandianchengzi/p/18155299
    logger.debug(f">>>>> enable_pdf_viewer: {enable_pdf_viewer}")
    if not enable_pdf_viewer:
        opt.add_experimental_option("prefs", {
            "plugins.plugins_disabled": ["Chrome PDF Viewer"],
            "plugins.always_open_pdf_externally": True,
            "download.prompt_for_download": False,
            "download.overwrite": True,
            "download.directory_upgrade": True,
            "download.default_directory": TEMP_DIR,
        })

    return opt


def _md5sum(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def _target_is_pdf(url):
    """
    判断给定的 url 是否为 pdf 文件

    测试用例：
    >>> _target_is_pdf("/path/to/xxx.pdf")
    True
    >>> _target_is_pdf("/path/to/xxx.Pdf")
    True
    >>> _target_is_pdf("/path/to/xxx.PDF")
    True
    >>> _target_is_pdf("/path/to/xxx.PDF?foo=bar")
    True
    >>> _target_is_pdf("https://example.com/xxx.PDF?foo=bar")
    True
    >>> _target_is_pdf("https://example.com/xxx.docx?foo=bar")
    False

    :param url: Pdf URL
    :type url: str
    :return: True or False
    :rtype: bool
    """
    return bool(PDF_FILE_PATTERN.match(urlparse(url).path))


def _most_recent_updated_file():
    items = [os.path.join(TEMP_DIR, item) for item in os.listdir(TEMP_DIR)]
    items.sort(key=lambda x: os.path.getctime(x), reverse=True)
    return items[0] if len(items) > 0 else None


def _is_file_ready():
    """对于pdf等文件类的地址，浏览器会触发下载机制，此时需要到下载目录监控文件的下载情况，以确认文件是否已下载完成。"""

    # 列出目录中所有非临时文件
    files = [f for f in os.listdir(TEMP_DIR)]
    logger.debug(f">>>>> Listing files: {files}")
    # 若存在文件且无临时文件，视为下载完成
    return len(files) > 0 and not any(f.endswith(".crdownload") for f in files)


def _guess_media_ext(url: str) -> str:
    media_ext = Path(url).suffix

    if media_ext not in mimetypes.types_map:
        media_ext = ""
        media_type = mimetypes.guess_type(url)[0]
        if media_type:
            media_ext = cast(str, mimetypes.guess_extension(media_type))

    return media_ext if media_ext else ".html"
