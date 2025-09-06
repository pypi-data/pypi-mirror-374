import base64
import datetime
import json
import logging
import os
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import allure
import urllib3
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from promium._diag import push_step
from promium.waits import (
    enable_jquery,
    wait_for_animation,
    wait_until_new_window_is_opened,
)


log = logging.getLogger(__name__)

http = urllib3.PoolManager(
    cert_reqs=False,
    timeout=5,
)

SCREENSHOT_SERVER_HOST = os.environ.get("SCREENSHOT_SERVER_HOST")
SCREENSHOT_SERVER_LOGIN = os.environ.get("SCREENSHOT_SERVER_LOGIN")
SCREENSHOT_SERVER_PASSWORD = os.environ.get("SCREENSHOT_SERVER_PASSWORD")

_LABEL_JS = r"""
var el = arguments[0];
if(!el){ return null; }
function esc(s){ return String(s).replace(/'/g, "\\'"); }
var qaid = el.getAttribute('data-qaid') || el.getAttribute('data-qa-id');
if (qaid) return "[data-qaid='" + esc(qaid) + "']";
if (el.id)  return "#" + el.id;
var cls = (el.className || '')
    .toString()
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .join('.');
var tag = (el.tagName || '').toLowerCase();
if (cls) return tag + "." + cls;
return tag || "<element>";
"""


def _label_for_el(driver: Any, element: Any) -> str:
    """Return short label for element used in logs/steps."""
    try:
        label = driver.execute_script(_LABEL_JS, element)
        return str(label) if label else "<element>"
    except Exception:
        return "<element>"


def scroll_to_bottom(driver: Any) -> None:
    """Scroll to the bottom of the page."""
    push_step("scroll_to_bottom()")

    enable_jquery(driver)
    driver.execute_script('jQuery("img.img-ondemand").trigger("appear");')
    driver.execute_script(
        """
        var f = function(old_height) {
            var height = $$(document).height();
            if (height == old_height) return;
            $$('html, body').animate({scrollTop:height}, 'slow', null,
            setTimeout(function() {f(height)}, 1000)
            );
        }
        f();
        """
    )
    wait_for_animation(driver)


def scroll_to_top(driver: Any) -> None:
    """Scroll to the top of the page."""
    push_step("scroll_to_top()")

    enable_jquery(driver)
    driver.execute_script(
        """jQuery('html, body').animate({scrollTop: 0 }, 'slow', null);"""
    )
    wait_for_animation(driver)


def scroll_to_bottom_in_block(driver: Any, element_class: str) -> None:
    """Scroll to the bottom of a specific block."""
    push_step(f"scroll_to_bottom_in_block('.{element_class}')")

    enable_jquery(driver)
    script = """
        var elem = '.'.concat(arguments[0]);
        $(elem).animate({scrollTop: $(elem).prop('scrollHeight')}, 1000);
    """
    driver.execute_script(script, element_class)
    wait_for_animation(driver)


def scroll_to_element(
    driver: Any, element: Any, base_element: Any | None = None
) -> None:
    """Scroll to an element. If base provided, scroll within it."""
    label = _label_for_el(driver, element)
    base_lbl = base_element if base_element is not None else "html, body"
    push_step(f'scroll_to_element("{label}", base="{base_lbl}")')

    enable_jquery(driver)
    if base_element is None:
        base_element = "html, body"
    script = """
        var elem = arguments[0];
        var base = arguments[1];
        var relativeOffset = (
            jQuery(elem).offset().top - jQuery(base).offset().top
        );
        jQuery(base).animate({
            scrollTop: relativeOffset
            }, 'slow', null
        );
    """
    driver.execute_script(script, element, base_element)
    wait_for_animation(driver)


def scroll_with_offset(driver: Any, element: Any, with_offset: int = 0) -> None:
    """Scroll to element with an extra pixel offset."""
    label = _label_for_el(driver, element)
    push_step(f'scroll_with_offset("{label}", {with_offset})')

    enable_jquery(driver)
    script = """
        var elem = arguments[0];
        jQuery('html, body').animate({
            scrollTop: jQuery(elem).offset().top + arguments[1]
            }, 'fast', null
        );
    """
    driver.execute_script(script, element, with_offset)
    wait_for_animation(driver)


def scroll_into_end(driver: Any) -> None:
    """Scroll to the very end of the page."""
    push_step("scroll_into_end()")

    enable_jquery(driver)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    wait_for_animation(driver)


def open_link_in_new_tab(driver: Any, url: str | None = None) -> None:
    """Open URL in a new tab and switch to it."""
    shown = url or "about:blank"
    push_step(f'open_link_in_new_tab("{shown}")')

    main_window = driver.current_window_handle
    driver.execute_script(f"""window.open("{shown}","_blank");""")
    new_window = wait_until_new_window_is_opened(driver, main_window)
    switch_to_window(driver, new_window)


def switch_to_window(driver: Any, window_handle: str) -> None:
    """Switch focus to the given window handle."""
    short = (str(window_handle)[:8] + "…") if window_handle else "<none>"
    push_step(f'switch_to_window("{short}")')

    driver.switch_to.window(window_handle)


def get_screenshot_path(name: str, with_date: bool = True) -> tuple[str, str]:
    """Generate screenshot path and file name."""
    now = datetime.datetime.now().strftime("%d_%H_%M_%S_%f")
    screenshot_name = f"{name}_{now}.png" if with_date else f"{name}.png"
    screenshots_folder = Path("/tmp")
    screenshots_folder.mkdir(parents=True, exist_ok=True)
    screenshot_path = screenshots_folder / screenshot_name
    return str(screenshot_path), screenshot_name


def if_server_have_problem() -> bool | str:
    """Check screenshot server availability."""
    try:
        r = http.request(
            url=f"https://{SCREENSHOT_SERVER_HOST}",
            method="GET",
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Connection": "keep-alive",
            },
        )
        assert r.status <= 400, f"Have problem {r.status}: {r.reason}"
        return False
    except Exception as e:
        return str(e)


def _upload_to_server(screenshot_path: str, screenshot_name: str) -> str | bool:
    """Upload screenshot to the configured server."""
    status_server = if_server_have_problem()
    if status_server:
        return status_server

    def read_in_chunks(
        img: Any, block_size: int = 1024, chunks: int = -1
    ) -> Iterator[bytes]:
        """Yield file bytes in chunks."""
        while chunks:
            data = img.read(block_size)
            if not data:
                break
            yield data
            chunks -= 1

    url = f"https://{SCREENSHOT_SERVER_HOST}/{screenshot_name}"
    path_obj = Path(screenshot_path)

    with path_obj.open("rb") as f:
        r = http.request(
            url=url,
            method="PUT",
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Authorization": "Basic "
                + base64.b64encode(
                    f"{SCREENSHOT_SERVER_LOGIN}:"
                    f"{SCREENSHOT_SERVER_PASSWORD}".encode()
                ).decode(),
            },
            body=read_in_chunks(f),
        )

    path_obj.unlink(missing_ok=True)

    if r.status != 201:
        return (
            "Screenshot not uploaded to server. "
            f"Status code: {r.status}, reason: {getattr(r, 'reason', '')}"
        )
    return url


def upload_screenshot(
    driver: Any, path_name: str = "screenshot", path_with_date: bool = True
) -> str:
    """Capture screenshot and upload. Return URL or file path."""
    try:
        screenshot_path, screenshot_name = get_screenshot_path(
            name=path_name, with_date=path_with_date
        )
        driver.save_screenshot(screenshot_path)

        if SCREENSHOT_SERVER_HOST:
            res = _upload_to_server(screenshot_path, screenshot_name)
            return str(res)
        return f"file://{screenshot_path}"
    except Exception as e:
        return f"No screenshot was captured due to exception {repr(e)}"


def control_plus_key(driver: Any, key: str) -> None:
    """Simulate pressing CTRL + key."""
    push_step(f'control_plus_key("{key}")')

    (
        ActionChains(driver)
        .key_down(Keys.CONTROL)
        .send_keys(key)
        .key_up(Keys.CONTROL)
        .perform()
    )


def set_local_storage(driver: Any, key: str, value: str) -> None:
    """Set a value in browser local storage."""
    push_step(f'set_local_storage("{key}")')
    driver.execute_script(
        "localStorage.setItem(arguments[0], arguments[1])", key, value
    )


def delete_cookie_item(driver: Any, name: str) -> None:
    """Delete a cookie and refresh the page."""
    push_step(f'delete_cookie_item("{name}")')
    driver.delete_cookie(name)
    driver.refresh()


def delete_element_from_dom(driver: Any, element: str) -> None:
    """Remove a DOM element by CSS selector."""
    push_step(f'delete_element_from_dom("{element}")')

    enable_jquery(driver)
    driver.execute_script(
        """
        var element = document.querySelector(arguments[0]);
        if (element) element.parentNode.removeChild(element);
        """,
        element,
    )


def find_network_log(
    driver: Any,
    find_mask: str,
    find_status: int = 200,
    timeout: int = 5,
    find_type: str | None = None,
) -> list[dict[str, Any]]:
    """
    Find XHR response and request data in Performance logs.

    :return: list of dicts [{response, data, body}]
    """
    show_type = f", type={find_type}" if find_type else ""
    push_step(
        f"find_network_log(mask='{find_mask}', status={find_status}{show_type})"
    )

    def get_log(request_mask: str) -> list[dict[str, Any]]:
        found_requests: list[dict[str, Any]] = []
        for performance_log in driver.get_log("performance"):
            msg = performance_log.get("message", "")
            if request_mask in msg and "responsereceived" in msg.lower():
                json_log = json.loads(msg)["message"]
                resp = json_log["params"].get("response")
                if not resp:
                    continue
                if resp.get("status") == find_status and (
                    not find_type or json_log["params"].get("type") == find_type
                ):
                    found_requests.append(json_log)
        return found_requests

    xhr_log: list[dict[str, Any]] = []
    while timeout >= 0:
        xhr_log = get_log(find_mask)
        if xhr_log:
            break
        time.sleep(0.5)
        timeout -= 1

    result_all_logs: list[dict[str, Any]] = []
    for network_log in xhr_log:
        request_id = network_log["params"]["requestId"]
        response = network_log["params"]["response"]
        try:
            req_data = driver.execute_cdp_cmd(
                "Network.getRequestPostData", {"requestId": request_id}
            )
            request_data = json.loads(req_data["postData"])
        except Exception:
            request_data = None

        try:
            resp_body = driver.execute_cdp_cmd(
                "Network.getResponseBody", {"requestId": request_id}
            )
            response_body = json.loads(resp_body["body"])
        except Exception:
            response_body = None

        log.info(
            "[XHR Logs]: find by mask: '%s' -> %s %s - %s",
            find_mask,
            response.get("url"),
            response.get("status"),
            response.get("statusText"),
        )
        result_all_logs.append({
            "response": {
                "url": response.get("url"),
                "status": response.get("status"),
                "statusText": response.get("statusText"),
            },
            "data": request_data,
            "body": response_body,
        })

    allure.attach(
        name=f"[XHR log] '{find_mask}', status:{find_status}, type:{find_type}",
        body=json.dumps(result_all_logs, indent=4, ensure_ascii=False),
        attachment_type=allure.attachment_type.JSON,
    )
    return result_all_logs
