import logging
import time
from collections.abc import Sequence
from typing import Any

import urllib3
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from promium._diag import push_step
from promium.exceptions import PromiumException, PromiumTimeout
from promium.logger import find_console_browser_errors, repr_console_errors


log = logging.getLogger(__name__)

NORMAL_LOAD_TIME = 10

http = urllib3.PoolManager(
    cert_reqs=False,
    timeout=10,
    headers={
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
    },
)


def enable_jquery(driver: Any) -> None:
    """Inject jQuery into the page if it is not already loaded."""
    driver.execute_script(
        """
        jqueryUrl =
        'https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js';
        if (typeof jQuery == 'undefined') {
            var script = document.createElement('script');
            var head = document.getElementsByTagName('head')[0];
            var done = false;
            script.onload = script.onreadystatechange = (function() {
                if (!done && (!this.readyState || this.readyState == 'loaded'
                        || this.readyState == 'complete')) {
                    done = true;
                    script.onload = script.onreadystatechange = null;
                    head.removeChild(script);

                }
            });
            script.src = jqueryUrl;
            head.appendChild(script);
            console.log("injection Complete by script enable jquery")
        };
        """
    )
    wait_obj = WebDriverWait(driver, timeout=NORMAL_LOAD_TIME)
    wait_obj.until(
        lambda d: d.execute_script("return window.jQuery != undefined") is True,
        message="Jquery script injection - failed ",
    )


def _check_browser_console(driver: Any) -> None:
    """Check browser console errors when exception occurs."""
    if console_errors := find_console_browser_errors(driver):
        log.warning(repr_console_errors(console_errors))


def wait(
    driver: Any,
    seconds: float = NORMAL_LOAD_TIME,
    poll_frequency: float = 0.5,
    ignored_exceptions: Sequence[type[BaseException]] | None = None,
) -> WebDriverWait:
    """Return a configured WebDriverWait object."""
    return WebDriverWait(
        driver=driver,
        timeout=seconds,
        poll_frequency=poll_frequency,
        ignored_exceptions=ignored_exceptions or [WebDriverException],
    )


def wait_until(
    driver: Any,
    expression: Any,
    seconds: float = NORMAL_LOAD_TIME,
    msg: str | None = None,
) -> Any:
    """Wait until expression is True or timeout expires."""
    try:
        try:
            name = getattr(expression, "__name__", "<expr>")
            push_step(f'wait_until("{name}", {seconds}s)')
        except Exception:
            pass
        return wait(driver, seconds).until(expression, msg)
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_until_not(
    driver: Any,
    expression: Any,
    seconds: float = NORMAL_LOAD_TIME,
    msg: str | None = None,
) -> Any:
    """Wait until expression becomes False or timeout expires."""
    try:
        return wait(driver, seconds).until_not(expression, msg)
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_until_with_reload(
    driver: Any,
    expression: Any,
    trying: int = 5,
    seconds: float = 2,
    msg: str = "",
) -> None:
    """Wait until expression is True, refreshing page on each attempt."""
    for t in range(trying):
        try:
            if wait_until(driver, expression, seconds=seconds):
                return
        except PromiumException:
            log.info(f"Waiting `until` attempt number {t + 1}.")
            driver.refresh()
    msg = f"\n{msg}" if msg else ""
    raise PromiumTimeout(
        f"The values in expression not return true after {trying} tries {msg}",
        seconds=trying * seconds,
    )


def wait_until_not_with_reload(
    driver: Any,
    expression: Any,
    trying: int = 5,
    seconds: float = 2,
    msg: str = "",
) -> None:
    """Wait until expression is False, refreshing page on each attempt."""
    for t in range(trying):
        try:
            if not wait_until_not(driver, expression, seconds=seconds):
                return
        except PromiumException:
            log.info(f"Waiting `until not` attempt number {t + 1}.")
            driver.refresh()
    msg = f"\n{msg}" if msg else ""
    raise PromiumTimeout(
        f"The values in expression not return false after {trying} tries {msg}.",
        seconds=trying * seconds,
    )


def wait_for_animation(driver: Any) -> Any:
    """Wait until all jQuery animations are finished."""
    jquery_script = 'return jQuery(":animated").length == 0;'
    return wait_until(
        driver=driver,
        expression=lambda d: d.execute_script(jquery_script),
        seconds=NORMAL_LOAD_TIME,
        msg=f"Animation timeout (waiting time: {NORMAL_LOAD_TIME} sec)",
    )


def wait_document_status(driver: Any, seconds: float = NORMAL_LOAD_TIME) -> None:
    """Wait until document.readyState becomes 'complete'."""
    wait_obj = WebDriverWait(driver, timeout=seconds)
    try:
        wait_obj.until(
            lambda d: d.execute_script("return document.readyState")
            == "complete",
            message=(
                "Page didn't load because document.readyState did not go "
                "into status 'complete'"
            ),
        )
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_websocket_connection_open(
    driver: Any, seconds: float = NORMAL_LOAD_TIME
) -> None:
    """Wait until WebSocket connection is open."""
    wait_obj = WebDriverWait(driver, timeout=seconds)
    try:
        wait_obj.until(
            lambda d: d.execute_script("return WebSocket.OPEN") == 1,
            message="ReadyState of WebSocket connection didn't change on OPEN",
        )
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_jquery_status(driver: Any, seconds: float = NORMAL_LOAD_TIME) -> None:
    """Wait until jQuery active requests count becomes 0."""
    wait_obj = WebDriverWait(driver, timeout=seconds)
    try:
        wait_obj.until(
            lambda d: d.execute_script("return jQuery.active") == 0,
            message=(
                "Page didn't load because jquery script did not go into "
                "'active == 0' status"
            ),
        )
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_for_page_loaded(driver: Any, seconds: float = NORMAL_LOAD_TIME) -> None:
    """Wait until page is fully loaded with document, jQuery, and no alert."""
    wait_document_status(driver, seconds)
    enable_jquery(driver)
    wait_jquery_status(driver, seconds)
    alert_is_present = EC.alert_is_present()
    if alert_is_present(driver):
        alert_text = driver.switch_to_alert().text
        driver.switch_to_alert().dismiss()
        raise alert_text


def wait_for_alert(driver: Any, seconds: float = NORMAL_LOAD_TIME) -> Any:
    """Wait for alert to be present."""
    return WebDriverWait(
        driver, seconds, ignored_exceptions=[WebDriverException]
    ).until(EC.alert_is_present(), "Alert is not present.")


def wait_for_alert_is_displayed(
    driver: Any, seconds: float = NORMAL_LOAD_TIME
) -> bool:
    """Return True if alert is displayed within timeout, else False."""
    try:
        wait_for_alert(driver, seconds=seconds)
    except TimeoutException:
        return False
    return True


def wait_for_status_code(
    url: str,
    status_code: int = 200,
    tries: int = 10,
    allow_redirects: bool = True,
) -> Any:
    """Wait until given URL returns expected status code."""
    current_status: int | None = None
    for _ in range(tries):
        response = http.request(
            url=url,
            method="GET",
            redirect=allow_redirects,
        )
        current_status = response.status
        if current_status == status_code:
            return response
        time.sleep(1)
    raise PromiumException(
        f"Url {url} return status code {current_status} after {tries} tries."
    )


def wait_until_new_window_is_opened(
    driver: Any, original_window: str, window_num: int = 0
) -> str:
    """Wait until a new browser window is opened and return its handle."""
    wait_until(
        driver,
        lambda x: len(driver.window_handles) >= 2,
        msg="New window was not opened.",
    )
    window_handles = driver.window_handles
    window_handles.remove(original_window)
    return window_handles[window_num]


def wait_part_appear_in_class(
    driver: Any, obj: Any, part_class: str, msg: str | None = None
) -> None:
    """Wait until given substring appears in element's class attribute."""
    if not msg:
        msg = f'"{part_class}" not present in attribute *class*.'
    wait_until(
        driver,
        lambda d: (part_class in obj.get_attribute("class")),
        seconds=5,
        msg=msg,
    )


def wait_part_disappear_in_class(
    driver: Any, obj: Any, part_class: str, msg: str | None = None
) -> None:
    """Wait until given substring disappears from element's class attribute."""
    if not msg:
        msg = f'"{part_class}" not present in attribute *class*.'
    wait_until(
        driver,
        lambda d: (part_class not in obj.get_attribute("class")),
        seconds=5,
        msg=msg,
    )


def wait_url_contains(
    driver: Any, text: str, msg: str | None = None, timeout: int = 5
) -> None:
    """Wait until current URL contains given text."""
    if not msg:
        msg = f'"{text}" not present in current url {driver.current_url}.'
    wait_until(driver, EC.url_contains(text), seconds=timeout, msg=msg)


def wait_url_not_contains(
    driver: Any, text: str, msg: str | None = None, timeout: int = 5
) -> None:
    """Wait until current URL does not contain given text."""
    if not msg:
        msg = f'"{text}" not disappear in url.'
    wait_until_not(driver, EC.url_contains(text), seconds=timeout, msg=msg)
