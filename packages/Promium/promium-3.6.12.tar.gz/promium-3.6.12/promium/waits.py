import logging
import urllib3
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException
)

from promium.exceptions import PromiumException, PromiumTimeout
from promium.logger import find_console_browser_errors, repr_console_errors


log = logging.getLogger(__name__)

NORMAL_LOAD_TIME = 10


http = urllib3.PoolManager(
    cert_reqs=False,
    timeout=10,
    headers={
        "Accept-Encoding": 'gzip, deflate',
        "Accept": "*/*",
        "Connection": "keep-alive",
    },
)


def enable_jquery(driver):
    """Enables jquery"""
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
    wait = WebDriverWait(driver, timeout=NORMAL_LOAD_TIME)
    wait.until(
        lambda driver: (driver.execute_script(
            'return window.jQuery != undefined'
        ) is True),
        message="Jquery script injection - failed "
    )


def _check_browser_console(driver):
    """
    for using when exception occurs
    and default check console methods don`t work
    """
    if console_errors := find_console_browser_errors(driver):
        log.warning(repr_console_errors(console_errors))


def wait(
        driver,
        seconds=NORMAL_LOAD_TIME,
        poll_frequency=.5,
        ignored_exceptions=None
):
    """Waits in seconds"""
    return WebDriverWait(
        driver=driver,
        timeout=seconds,
        poll_frequency=poll_frequency,
        ignored_exceptions=ignored_exceptions or [WebDriverException]
    )


def wait_until(driver, expression, seconds=NORMAL_LOAD_TIME, msg=None):
    """Waits until expression execution"""
    try:
        return wait(driver, seconds).until(expression, msg)
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_until_not(driver, expression, seconds=NORMAL_LOAD_TIME, msg=None):
    """Waits until not expression execution"""
    try:
        return wait(driver, seconds).until_not(expression, msg)
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_until_with_reload(driver, expression, trying=5, seconds=2, msg=''):
    """Waits until expression execution with page refreshing"""
    for t in range(trying):
        try:
            if wait_until(driver, expression, seconds=seconds):
                return
        except PromiumException:
            log.info(f"Waiting `until` attempt number {t + 1}.")
            driver.refresh()
    msg = f'\n{msg}' if msg else ""
    raise PromiumTimeout(
        f'The values in expression not return true after {trying} tries {msg}',
        seconds=trying * seconds,
    )


def wait_until_not_with_reload(
        driver, expression, trying=5, seconds=2, msg=''
):
    """Waits until not expression execution with page refreshing"""
    for t in range(trying):
        try:
            if not wait_until_not(driver, expression, seconds=seconds):
                return
        except PromiumException:
            log.info(f"Waiting `until not` attempt number {t + 1}.")
            driver.refresh()
    msg = f'\n{msg}' if msg else ""
    raise PromiumTimeout(
        f'The values in expression not return false after {trying} '
        f'tries {msg}.',
        seconds=trying * seconds,
    )


def wait_for_animation(driver):
    """Waits for execution animation"""
    jquery_script = 'return jQuery(":animated").length == 0;'
    return wait_until(
        driver=driver,
        expression=lambda d: d.execute_script(jquery_script),
        seconds=NORMAL_LOAD_TIME,
        msg=f'Animation timeout (waiting time: {NORMAL_LOAD_TIME} sec)',
    )


def wait_document_status(driver, seconds=NORMAL_LOAD_TIME):
    wait = WebDriverWait(driver, timeout=seconds)
    try:
        wait.until(
            lambda driver: driver.execute_script(
                'return document.readyState'
            ) == 'complete',
            message=(
                "Page don't loaded because of document.readyState did not go "
                "into status 'complete'"
            )
        )
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_websocket_connection_open(driver, seconds=NORMAL_LOAD_TIME):
    """Waiting for websocket connection to be opened"""
    wait = WebDriverWait(driver, timeout=seconds)
    try:
        wait.until(
            lambda driver:
            driver.execute_script('return WebSocket.OPEN') == 1,
            message="ReadyState of WebSocket connection didn't change on OPEN"
        )
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_jquery_status(driver, seconds=NORMAL_LOAD_TIME):
    """Wait for jquery will pass to active status"""
    wait = WebDriverWait(driver, timeout=seconds)
    try:
        wait.until(
            lambda driver: driver.execute_script(
                'return jQuery.active'
            ) == 0,
            message=(
                "Page don't loaded because of jquery script did not go into "
                "'active == 0' status"
            )
        )
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds, e.screen) from e


def wait_for_page_loaded(driver, seconds=NORMAL_LOAD_TIME):
    """Waits for page loaded"""
    wait_document_status(driver, seconds)
    enable_jquery(driver)
    wait_jquery_status(driver, seconds)
    alert_is_present = EC.alert_is_present()
    if alert_is_present(driver):
        alert_text = driver.switch_to_alert().text
        driver.switch_to_alert().dismiss()
        raise alert_text


def wait_for_alert(driver, seconds=NORMAL_LOAD_TIME):
    """Wait fo alert"""
    return WebDriverWait(
        driver, seconds, ignored_exceptions=[WebDriverException]
    ).until(
        EC.alert_is_present(), "Alert is not present."
    )


def wait_for_alert_is_displayed(driver, seconds=NORMAL_LOAD_TIME):
    """Wait for alert to be displayed"""
    try:
        wait_for_alert(driver, seconds=seconds)
    except TimeoutException:
        return False
    return True


def wait_for_status_code(url, status_code=200, tries=10, allow_redirects=True):
    """Waits for status code"""
    current_status = None
    for _ in range(tries):
        response = http.request(
            url=url,
            method='GET',
            redirect=allow_redirects,
        )
        current_status = response.status
        if current_status == status_code:
            return response
        time.sleep(1)
    raise PromiumException(
        f"Url {url} return status code {current_status} after {tries} tries."
    )


def wait_until_new_window_is_opened(driver, original_window, window_num=0):
    """Wait until new window is opened in session"""
    wait_until(
        driver,
        lambda x: len(driver.window_handles) >= 2,
        msg='New window was not opened.'
    )
    window_handles = driver.window_handles
    window_handles.remove(original_window)
    return window_handles[window_num]


def wait_part_appear_in_class(driver, obj, part_class, msg=None):
    """Wait some text in html class of the object"""
    if not msg:
        msg = f'"{part_class}" not present in attribute *class*.'
    wait_until(
        driver,
        lambda driver: (part_class in obj.get_attribute('class')),
        seconds=5,
        msg=msg
    )


def wait_part_disappear_in_class(driver, obj, part_class, msg=None):
    """Wait some text not in html class of the object"""
    if not msg:
        msg = f'"{part_class}" not present in attribute *class*.'
    wait_until(
        driver,
        lambda driver: (part_class not in obj.get_attribute('class')),
        seconds=5,
        msg=msg
    )


def wait_url_contains(driver, text, msg=None, timeout=5):
    """Wait some text is present in current url"""
    if not msg:
        msg = f'"{text}" not present in current url {driver.current_url}.'
    wait_until(driver, EC.url_contains(text), seconds=timeout, msg=msg)


def wait_url_not_contains(driver, text, msg=None, timeout=5):
    """Wait some text is not present in current url"""
    if not msg:
        msg = f'"{text}" not disappear in url.'
    wait_until_not(driver, EC.url_contains(text), seconds=timeout, msg=msg)
