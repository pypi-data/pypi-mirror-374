"""This module contains the ``SeleniumRequest`` class"""
import logging
from shutil import which
from scrapy import Request
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import defaults

logger = logging.getLogger(__name__)


class SeleniumRequest(Request):
    """Scrapy ``Request`` subclass providing additional arguments"""

    def __init__(self, wait_time=None, wait_until=None, screenshot=False, script=None, *args, **kwargs):
        """Initialize a new selenium request

        Parameters
        ----------
        wait_time: int
            The number of seconds to wait.
        wait_until: method
            One of the "selenium.webdriver.support.expected_conditions". The response
            will be returned until the given condition is fulfilled.
        screenshot: bool
            If True, a screenshot of the page will be taken and the data of the screenshot
            will be returned in the response "meta" attribute.
        script: str
            JavaScript code to execute.

        """

        self.wait_time = wait_time
        self.wait_until = wait_until
        self.screenshot = screenshot
        self.script = script

        super().__init__(*args, **kwargs)


def get_response(url,
                 driver_executable_path: str = "",
                 timeout_to_wait: float = 2,
                 user_agent: str = defaults.USER_AGENT,
                 headless: bool = True) -> HtmlResponse:
    """Get a Selenium driven request when using scrapy shell's default response won't work.

    Args:
        url (str): url to fetch
        driver_executable_path (str, optional): chrome driver path. Defaults to "".
        timeout_to_wait (float, optional): timeouts to wait for loading. Defaults to 2.
        user_agent (str, optional): user agent to use. Defaults to defaults.USER_AGENT.
        headless (bool, optional): Use headless mode or not. Defaults to True.

    Returns:
        HtmlResponse: a scrapy HtmlResponse object
    """
    # 配置Chrome选项
    chrome_options = Options()
    # 禁用缓存（避免旧缓存干扰重定向）

    for arg in defaults.get_driver_arguments_with(user_agent, headless):
        chrome_options.add_argument(arg)

    # 开启性能日志
    # chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    executable_path = driver_executable_path or which("chromedriver")
    driver = webdriver.Chrome(
        service=Service(executable_path=executable_path) if executable_path else Service(
            ChromeDriverManager().install()),
        options=chrome_options,
    )

    # 设置页面完全加载完成的超时时间为30s
    driver.set_page_load_timeout(30)

    try:
        driver.get(url)
        # 设置额外的时间等待「动态」内容加载完成
        WebDriverWait(driver, timeout_to_wait).until(
            lambda drv: logger.info(f">>>>> current/redirect url: {drv.current_url}"))
    except TimeoutException:
        pass

    res = HtmlResponse(
        url=driver.current_url,
        # 使用浏览器实际渲染后的结构作为页面主体返回
        body=driver.execute_script(
            "return document.documentElement.outerHTML"),
        encoding="utf-8"
    )
    driver.quit()
    return res
