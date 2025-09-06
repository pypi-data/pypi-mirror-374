import contextlib
import logging
import os
import random
import sys
import time
from collections.abc import Callable, Iterator, Sequence
from functools import wraps
from typing import Any, Self

import pytest
import urllib3
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from promium._diag import build_digest, push_step
from promium.common import (
    find_network_log,
    scroll_into_end,
    scroll_to_bottom,
    scroll_to_element,
    scroll_to_top,
    set_local_storage,
    switch_to_window,
)
from promium.exceptions import (
    ElementLocationException,
    LocatorException,
    PromiumException,
)
from promium.expected_conditions import is_present
from promium.logger import (
    add_logger_to_base_element_classes,
    logger_for_loading_page,
)
from promium.waits import (
    wait_document_status,
    wait_for_alert,
    wait_for_alert_is_displayed,
    wait_for_animation,
    wait_for_page_loaded,
    wait_part_appear_in_class,
    wait_part_disappear_in_class,
    wait_until,
    wait_until_new_window_is_opened,
    wait_websocket_connection_open,
)


log = logging.getLogger(__name__)

MAX_TRIES = 20
NORMAL_LOAD_TIME = 10


def with_retries(tries: int, second_to_wait: float) -> Any:
    """
    Decorator that retries a function call until success or attempts
     are exhausted.

    Args:
        tries: Number of retry attempts.
        second_to_wait: Seconds to wait between retries.

    Raises:
        ElementLocationException: If the element cannot be found after retries.

    Returns:
        Result of the wrapped function if successful.
    """

    def callable_func(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for _ in range(tries):
                try:
                    res = func(*args, **kwargs)
                    if res:
                        return res
                except Exception:
                    pass
                time.sleep(second_to_wait)

            element = args[0]
            try:
                css_probe = (
                    element.locator
                    if getattr(element, "by", None) == By.CSS_SELECTOR
                    else None
                )
                locator_str = f"{element.by}={element.locator}"
            except Exception:
                css_probe = None
                locator_str = "<unknown locator>"

            total_wait = tries * second_to_wait
            digest = build_digest(
                element.driver,
                title="Element not found",
                locator=locator_str,
                timeout=total_wait,
                css_for_probe=css_probe,
                **element._digest_ctx(),
            )
            raise ElementLocationException(digest) from None

        return wrapper

    return callable_func


def highlight_element(func: Any) -> Any:
    """
    Decorator for visually highlighting elements during lookup.

    If the environment variable HIGHLIGHT is set to "Enabled",
    the element will be outlined in red for debugging purposes.
    """

    @wraps(func)
    def wrapper(self: Any, *args, **kwargs) -> WebElement:
        element = func(self, *args, **kwargs)
        highlight_status = os.environ.get("HIGHLIGHT")
        if highlight_status == "Enabled":
            self.driver.execute_script(
                """
                element = arguments[0];
                original_style = element.getAttribute('style');
                element.setAttribute(
                    'style',
                    original_style + ";border: 3px solid #D4412B;"
                );
                setTimeout(function() {
                    element.setAttribute('style', original_style);
                }, 300);
                """,
                element,
            )
            time.sleep(0.5)
        return element

    return wrapper


def text_to_be_present_in_element(element: "Element", text_: str) -> Callable:
    """
    Expected condition that checks whether given text is present in element.

    Args:
        element: Target Element wrapper.
        text_: Text to check for.

    Returns:
        Predicate function for WebDriverWait.
    """

    def _predicate(driver: WebDriver) -> bool:
        try:
            return text_ in element.lookup().text
        except StaleElementReferenceException:
            return False

    return _predicate


class Page:
    """
    Base class representing a web page in the Page Object Model.
    Provides navigation, state checking, and utility methods for tests.
    """

    url = None

    def __init__(
        self, driver: WebDriver, monkeypatch: pytest.MonkeyPatch = None
    ) -> None:
        self._driver = driver
        self.previous_window_handle = self.driver.current_window_handle
        self.monkeypatch = monkeypatch

    @property
    def driver(self) -> WebDriver:
        """Return the WebDriver instance."""
        return self._driver

    @property
    def is_mobile(self) -> bool:
        """Return True if the user agent indicates a mobile device."""
        return (
            "mobile"
            in self.driver.execute_script("return navigator.userAgent;").lower()
        )

    @property
    def is_desktop(self) -> bool:
        """Return True if the user agent indicates a desktop device."""
        return not self.is_mobile

    def lookup(self) -> None:
        """Placeholder lookup for Page (always returns None)."""
        return

    @logger_for_loading_page
    def open(self, **kwargs) -> str:  # noqa: A003
        """Open the page using its defined `url` template."""
        if not self.url:
            raise PromiumException("Can't open page without url")
        start = time.time()
        url = self.url.format(**kwargs)
        log.info(f"Open Page: {url}")
        try:
            self.driver.get(url)
        except TimeoutException:
            log.error(f"[PROMIUM] Page load time: {time.time() - start}")
            raise
        return url

    @logger_for_loading_page
    def refresh(self) -> None:
        """Refresh the current page."""
        self.driver.refresh()

    def wait_for_page_loaded(self) -> None:
        """Wait until the page is fully loaded."""
        wait_for_page_loaded(self.driver)

    def wait_for_source_changed(self, action_func: Any, *args, **kwargs) -> None:
        """Wait until the page source changes after executing an action."""
        source = self.driver.page_source
        action_func(*args, **kwargs)
        wait_until(
            self.driver,
            lambda driver: driver.page_source != source,
            msg="Page source didn't change.",
        )

    def get_status_code(self) -> int:
        """Return HTTP status code of the current page."""
        http = urllib3.PoolManager(cert_reqs=False, timeout=5)
        cookies_str = "; ".join([
            f"{cookie['name']}={cookie['value']}"
            for cookie in self.driver.get_cookies()
        ])
        r = http.request(
            url=self.driver.current_url,
            method="GET",
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Cookie": cookies_str,
            },
            redirect=False,
            retries=urllib3.Retry(redirect=0, raise_on_redirect=False),
        )
        return r.status

    def wait_for_animation(self) -> None:
        """Wait until page animations complete."""
        wait_for_animation(self.driver)

    def wait_document_status(self, seconds: float = NORMAL_LOAD_TIME) -> None:
        """Wait until document readyState is complete."""
        wait_document_status(self.driver, seconds=seconds)

    def wait_websocket_connection_open(
        self, seconds: float = NORMAL_LOAD_TIME
    ) -> None:
        """Wait until websocket connection is established."""
        wait_websocket_connection_open(self.driver, seconds=seconds)

    def wait_for_alert(self, seconds: float = NORMAL_LOAD_TIME) -> Alert:
        """Wait until an alert is present and return it."""
        return wait_for_alert(self.driver, seconds=seconds)

    def is_alert_displayed(self, seconds: float = NORMAL_LOAD_TIME) -> bool:
        """Return True if an alert is displayed within timeout."""
        return wait_for_alert_is_displayed(self.driver, seconds=seconds)

    def switch_to_tab(self) -> None:
        """Switch to a newly opened browser tab."""
        new_window = wait_until_new_window_is_opened(
            self.driver, self.previous_window_handle
        )
        switch_to_window(self.driver, new_window)

    def switch_previous_tab(self) -> None:
        """Switch back to the previously active tab."""
        switch_to_window(self.driver, self.previous_window_handle)

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the page."""
        scroll_to_bottom(self.driver)

    def scroll_to_top(self) -> None:
        """Scroll to the top of the page."""
        scroll_to_top(self.driver)

    def scroll_into_end(self) -> None:
        """Scroll until the end of the page is reached."""
        scroll_into_end(self.driver)

    def find_network_log(
        self, find_mask: str, find_status: int = 200, timeout: float = 5
    ) -> list:
        """Find and return network log entries matching given mask and status."""
        return find_network_log(self.driver, find_mask, find_status, timeout)

    def set_local_storage(self, key: str, value: str) -> None:
        """Set a key-value pair in the browser's localStorage."""
        set_local_storage(self.driver, key, value)


class Bindable:
    """
    Base class that allows binding a driver and parent context
    to an element instance when accessed as a descriptor.
    """

    def bind(self, parent: Any, driver: Any, parent_cls: Any = None) -> Any:
        """
        Bind the current instance to a parent element and driver.

        Args:
            parent: Parent element.
            driver: WebDriver instance.
            parent_cls: Optional parent class reference.

        Returns:
            A new bound instance of the class.
        """
        c = self.__class__.__new__(self.__class__)
        c.__dict__ = self.__dict__.copy()
        c.parent = parent
        c.parent_cls = parent_cls
        c.driver = driver
        return c

    def __get__(self, instance: Any, owner: Any) -> Any:
        """Return a bound instance when accessed as a descriptor."""
        return self.bind(instance.lookup(), instance.driver, instance)


class Base(Bindable):
    """
    Base class for elements with locators.
    Provides core logic for finding elements, caching,
    and contextual debugging.
    """

    index = 0
    parent = None
    driver = None
    parent_cls = None
    _cached_elements = None

    def __init__(self, by: str, locator: str) -> None:
        """
        Initialize an element with a locator.

        Args:
            by: Locator strategy (e.g., By.CSS_SELECTOR, By.XPATH).
            locator: Locator string.
        """
        self.by = by
        self.locator = locator

        if (
            getattr(self, "_origin_file", None) is not None
            and getattr(self, "_origin_line", None) is not None
        ):
            return

        try:
            fr = sys._getframe(1)
            self._origin_file = fr.f_code.co_filename
            self._origin_line = fr.f_lineno
        except Exception:
            self._origin_file = None
            self._origin_line = None

    def _context_chain_list(self, include_self: bool = False) -> list[str]:
        """
        Build a chain of container locators from root to current element.

        Args:
            include_self: Whether to include the current element.

        Returns:
            List of locators in top-to-bottom order.
        """
        chain: list[str] = []
        cur = self
        while True:
            by = getattr(cur, "by", None)
            loc = getattr(cur, "locator", None)
            if by and loc:
                chain.append(f"{by}={loc}")
            parent = getattr(cur, "parent_cls", None)
            if not parent or parent is cur:
                break
            cur = parent
        chain.reverse()

        if (
            not include_self
            and chain
            and chain[-1] == f"{self.by}={self.locator}"
        ):
            chain.pop()

        return chain

    def _digest_ctx(self) -> dict:
        """
        Build context dictionary for error reporting.

        Returns:
            Dict with origin file/line and context chain.
        """
        return {
            "origin": (
                getattr(self, "_origin_file", None),
                getattr(self, "_origin_line", None),
            ),
            "context_prefix": self._context_chain_list(include_self=False),
        }

    def _fmt_locator(self) -> str:
        """Return locator string in formatted form."""
        by = getattr(self, "by", "?")
        loc = getattr(self, "locator", "?")
        return f"{by}={loc}"

    @property
    def is_mobile(self) -> bool:
        """Return True if the driver indicates a mobile user agent."""
        return (
            "mobile"
            in self.driver.execute_script("return navigator.userAgent;").lower()
        )

    @property
    def is_desktop(self) -> bool:
        """Return True if the driver indicates a desktop user agent."""
        return not self.is_mobile

    def _refresh_parent(self) -> None:
        """Refresh driver and parent from parent_cls if available."""
        if self.parent_cls:
            self.driver = self.parent_cls.driver
            self.parent = self.parent_cls.lookup()

    def _get_current_driver(self) -> WebDriver | WebElement:
        """
        Return current driver or WebElement depending on context.

        Returns:
            WebDriver or WebElement.
        """
        return self.parent if self.parent is not None else self.driver

    def _validate_locator(self) -> tuple[str, str]:
        """
        Validate locator for correctness.

        Ensures XPath locators start with "." if used relative
        to a WebElement.

        Returns:
            Tuple (by, locator).
        """
        if isinstance(self._get_current_driver(), WebElement):
            if self.by == By.XPATH and not self.locator.startswith("."):
                raise LocatorException(
                    f'Xpath locator must start with "." (dot). '
                    f'Please check this locator "{self.locator}"'
                )
        return self.by, self.locator

    def _find_elements(self) -> list[WebElement]:
        """
        Find all elements for this locator.

        Returns:
            List of WebElement objects.
        """
        driver = self._get_current_driver()
        by, loc = self._validate_locator()
        with contextlib.suppress(Exception):
            push_step(f'find_elements("{by}={loc}")')
        try:
            self._cached_elements = driver.find_elements(by, loc)
        except StaleElementReferenceException:
            self._refresh_parent()
            driver = self._get_current_driver()
            self._cached_elements = driver.find_elements(by, loc)
        return self._cached_elements

    @with_retries(MAX_TRIES, 0.5)
    def _finder(self, force: bool = False) -> list[WebElement]:
        """
        Retrieve cached elements or perform a fresh search.

        Args:
            force: Whether to ignore cache and search again.

        Returns:
            List of WebElement objects.
        """
        if force or not self._cached_elements:
            self._find_elements()
        return self._cached_elements


class Collection(Base, Sequence):
    """
    Represents a collection of elements found by the same locator.
    Provides iteration, indexing, waiting, filtering, and random selection.
    """

    def __iter__(self) -> Iterator:
        """Iterate over elements in the collection."""
        for i in range(len(self)):
            yield self[i]

    def get_item(self, index: int) -> Any:
        """
        Get an item from the collection by index.

        Args:
            index: Index of the element.

        Returns:
            Instance of the element at the given index.
        """
        with contextlib.suppress(Exception):
            push_step(
                f'collection_get_item("{self._fmt_locator()}", index={index})'
            )

        item_name = f"{self.base.__name__}Item"
        params = {
            "parent": self.parent,
            "driver": self.driver,
            "parent_cls": self.base.parent_cls,
            "_cached_elements": self._cached_elements,
            "index": index,
            "_origin_file": getattr(self, "_origin_file", None),
            "_origin_line": getattr(self, "_origin_line", None),
        }
        return type(item_name, (self.base,), params)(self.by, self.locator)

    def __getitem__(self, val: Any) -> Any | list[Any]:
        """Support indexing and slicing of collection items."""
        if isinstance(val, slice):
            start, stop, step = val.indices(len(self))
            return [self.get_item(i) for i in range(start, stop, step)]
        return self.get_item(val)

    def __len__(self) -> int:
        """Return number of elements in the collection."""
        return len(self._find_elements())

    def is_empty(self) -> bool:
        """Return True if collection is empty."""
        return len(self) < 1

    def is_not_empty(self) -> bool:
        """Return True if collection is not empty."""
        return not self.is_empty()

    def random_choice(self) -> Any:
        """
        Select a random item from the collection.

        Returns:
            Randomly chosen element from the collection.
        """
        elements = self.wait_not_empty()
        index = random.randint(0, len(elements) - 1)
        return self.get_item(index)

    def wait_empty(self, timeout: float = 10) -> Self:
        """
        Wait until the collection becomes empty.

        Args:
            timeout: Maximum time to wait.

        Raises:
            ElementLocationException: If collection is not empty after timeout.

        Returns:
            Self reference.
        """
        css = self._fmt_locator()
        with contextlib.suppress(Exception):
            push_step(f'wait_empty("{css}", {timeout}s)')

        msg = (
            f"Collection with {self.by}={self.locator} is not empty"
            f" after {timeout}"
        )
        try:
            wait_until(self.driver, lambda e: self.is_empty(), timeout, msg)
            return self
        except Exception as e:
            digest = build_digest(
                self.driver,
                title="Collection is not empty",
                locator=css,
                wait_seconds=timeout,
                css_for_probe=self.locator
                if self.by == By.CSS_SELECTOR
                else None,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def wait_not_empty(self, timeout: float = 10) -> Self:
        """
        Wait until the collection becomes non-empty.

        Args:
            timeout: Maximum time to wait.

        Raises:
            ElementLocationException: If collection is empty after timeout.

        Returns:
            Self reference.
        """
        css = self._fmt_locator()
        with contextlib.suppress(Exception):
            push_step(f'wait_not_empty("{css}", {timeout}s)')

        msg = (
            f"Collection with {self.by}={self.locator} is empty after {timeout}"
        )
        try:
            wait_until(self.driver, lambda e: self.is_not_empty(), timeout, msg)
            return self
        except Exception as e:
            digest = build_digest(
                self.driver,
                title="Collection is empty",
                locator=css,
                wait_seconds=timeout,
                css_for_probe=self.locator
                if self.by == By.CSS_SELECTOR
                else None,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def filter_by(self, child_locator: str) -> Self:
        """
        Filter collection by requiring a child CSS locator.

        Args:
            child_locator: CSS selector for child element.

        Raises:
            ElementLocationException: If no elements match.

        Returns:
            Filtered collection.
        """
        script = f"return $('{self.locator}:has({child_locator})');"
        results = self.driver.execute_script(script)
        if not results:
            css_probe = self.locator if self.by == By.CSS_SELECTOR else None
            digest = build_digest(
                self.driver,
                title="No elements matched filter",
                locator=f"{self.by}={self.locator} has({child_locator})",
                condition="jQuery :has(...) result -> 0",
                css_for_probe=css_probe,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from None
        self._cached_elements = results
        return self

    def find_all(self, by: str, locator: str) -> Any:
        """
        Create a new collection with a different locator.

        Args:
            by: Locator strategy.
            locator: Locator string.

        Returns:
            Collection bound to the new locator.
        """
        c = self.bind(self.parent, self.driver, self)
        c.by = by
        c.locator = locator
        return c

    def find(self, by: str, locator: str) -> Any:
        """
        Find the first element by locator.

        Args:
            by: Locator strategy.
            locator: Locator string.

        Returns:
            Element instance.
        """
        return self.find_all(by, locator).get_item(0)

    def find_by_text(
        self,
        text: str,
        check_negative: bool = False,
        partial_text: bool = True,
    ) -> "Element":
        """
        Find element by its visible text.

        Args:
            text: Text to search for.
            check_negative: If True, return False instead of raising exception.
            partial_text: If True, check substring instead of exact match.

        Raises:
            PromiumException: If element not found.

        Returns:
            Matching element or False if negative check is enabled.
        """
        if partial_text:
            script = """
                var el = arguments[0]; var text = arguments[1];
                return (el.innerText||"").includes(text);
            """
        else:
            script = """
                var el = arguments[0]; var text = arguments[1];
                return (el.innerText||"") === text;
            """
        found_elements_by_test = [
            element
            for element in self
            if self.driver.execute_script(script, element.lookup(), text)
        ]
        if len(found_elements_by_test) == 0:
            if check_negative:
                return False
            css_probe = self.locator if self.by == By.CSS_SELECTOR else None
            digest = build_digest(
                self.driver,
                title="Element with given text not found",
                locator=f"{self.by}={self.locator}",
                condition=f"text {'contains' if partial_text else 'equals'}"
                f' "{text}"',
                css_for_probe=css_probe,
                **self._digest_ctx(),
            )
            raise PromiumException(digest) from None
        return found_elements_by_test[0]

    @property
    def first_item(self) -> Any:
        """Return the first element in the collection (after waiting)."""
        return self.wait_not_empty().get_item(0)

    @property
    def last_item(self) -> Any:
        """Return the last element in the collection (after waiting)."""
        return self.wait_not_empty().get_item(-1)


@add_logger_to_base_element_classes
class ElementBase(Base):
    """
    Base class for single elements.
    Provides lookup, wait conditions, scrolling, clicking,
    attribute access, and interaction helpers.
    """

    def _fmt_locator(self) -> str:
        """Return formatted locator string."""
        return f"{self.by}={self.locator}"

    def _get_element(self) -> WebElement:
        """
        Return the WebElement at the current index.

        Raises:
            PromiumException: If index is out of range.
        """
        if self.index >= len(self._cached_elements):
            css_probe = self.locator if self.by == By.CSS_SELECTOR else None
            digest = build_digest(
                self.driver,
                title="Collection changed / index out of range",
                locator=f"{self.by}={self.locator}",
                condition=f"index={self.index}, "
                f"length={len(self._cached_elements)}",
                css_for_probe=css_probe,
                **self._digest_ctx(),
            )
            raise PromiumException(digest) from None
        return self._cached_elements[self.index]

    @highlight_element
    def lookup(self) -> WebElement:
        """
        Return the WebElement instance.

        Raises:
            ElementLocationException: If element is stale or cannot be found.
        """
        try:
            with contextlib.suppress(Exception):
                push_step(f'lookup("{self._fmt_locator()}")')

            self._cached_elements = self._finder()
            element = self._get_element()
            element.is_displayed()
        except StaleElementReferenceException:
            self._refresh_parent()
            self._cached_elements = self._finder(force=True)
            element = self._get_element()
        return element

    @classmethod
    def as_list(cls, by: str, locator: str) -> Any:
        """
        Create a Collection of this element type.

        Args:
            by: Locator strategy.
            locator: Locator string.

        Returns:
            Collection of elements of this type.
        """
        try:
            fr = sys._getframe(1)
            _of, _ol = fr.f_code.co_filename, fr.f_lineno
        except Exception:
            _of, _ol = None, None

        params = {
            "parent": cls.parent,
            "driver": cls.driver,
            "base": cls,
            "_origin_file": _of,
            "_origin_line": _ol,
        }
        return type(f"{cls.__name__}List", (Collection,), params)(by, locator)

    def wait_to_display(self, timeout: int = 10, msg: str = "") -> Self:
        """
        Wait until the element is visible.

        Args:
            timeout: Maximum wait time in seconds.
            msg: Optional extra message for error context.

        Raises:
            ElementLocationException: If element is not displayed.
        """
        obj = self._get_current_driver()
        css = self._fmt_locator()
        css_probe = self.locator if self.by == By.CSS_SELECTOR else None
        push_step(f'wait_to_display("{css}", {timeout}s)')
        try:
            WebDriverWait(
                obj,
                timeout,
                ignored_exceptions=[
                    WebDriverException,
                    ElementLocationException,
                ],
            ).until(lambda driver: self.is_displayed())
            return self
        except TimeoutException:
            title = (
                "Element was found but not displayed"
                if self.is_present()
                else "Element was not found"
            )
            digest = build_digest(
                self.driver,
                title=title,
                locator=css,
                wait_seconds=timeout,
                css_for_probe=css_probe,
                **self._digest_ctx(),
            )
            if msg:
                digest = f"{digest}\n{msg}"
            raise ElementLocationException(digest) from None

    def wait_to_present(self, timeout: int = 10, msg: str = "") -> Self:
        """
        Wait until the element is present in DOM.

        Args:
            timeout: Maximum wait time in seconds.
            msg: Optional extra message for error context.

        Raises:
            ElementLocationException: If element is not present.
        """
        css = self._fmt_locator()
        css_probe = self.locator if self.by == By.CSS_SELECTOR else None
        push_step(f'wait_to_present("{css}", {timeout}s)')
        try:
            wait_until(self.driver, is_present(self), timeout, "")
            return self
        except TimeoutException:
            digest = build_digest(
                self.driver,
                title="Element not present in DOM",
                locator=css,
                wait_seconds=timeout,
                css_for_probe=css_probe,
                **self._digest_ctx(),
            )
            if msg:
                digest = f"{digest}\n{msg}"
            raise ElementLocationException(digest) from None

    def wait_to_disappear(self, time: int = 10, msg: str = "") -> bool | None:
        """
        Wait until element disappears from DOM or is hidden.

        Args:
            time: Maximum wait time in seconds.
            msg: Optional extra message for error context.

        Raises:
            ElementLocationException: If element did not disappear.

        Returns:
            True if element disappeared, otherwise raises exception.
        """
        css = self._fmt_locator()
        css_probe = self.locator if self.by == By.CSS_SELECTOR else None
        push_step(f'wait_to_disappear("{css}", {time}s)')

        def _gone(_self: Self) -> bool:
            obj = _self._get_current_driver()
            try:
                return not obj.find_element(
                    _self.by, _self.locator
                ).is_displayed()
            except (
                NoSuchElementException,
                StaleElementReferenceException,
                WebDriverException,
            ):
                return True

        try:
            return WebDriverWait(self.driver, time).until(
                lambda driver: _gone(self)
            )
        except TimeoutException:
            digest = build_digest(
                self.driver,
                title="Element(s) did not disappear",
                locator=css,
                wait_seconds=time,
                css_for_probe=css_probe,
                **self._digest_ctx(),
            )
            if msg:
                digest = f"{digest}\n{msg}"
            raise ElementLocationException(digest) from None

    def wait_in_viewport(self, time: int = 5) -> Self:
        """
        Wait until the element is in the viewport.

        Args:
            time: Maximum wait time in seconds.

        Raises:
            ElementLocationException: If element is not in viewport.
        """
        jquery_script = """
            var elem = arguments[0],
            box = elem.getBoundingClientRect(),
            cx = box.left + box.width / 2,
            cy = box.top + box.height / 2,
            e = document.elementFromPoint(cx, cy);
            for (; e; e = e.parentElement) {
                if (e === elem)
                    return true;
            }
            return false;
        """
        css = self._fmt_locator()
        push_step(f'wait_in_viewport("{css}", {time}s)')
        try:
            wait_until(
                driver=self.driver,
                expression=lambda driver: driver.execute_script(
                    jquery_script, self.lookup()
                ),
                seconds=time,
                msg="",
            )
            return self
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Element is not in viewport",
                locator=css,
                condition="inViewport == true",
                timeout=time,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def wait_part_appear_in_class(
        self, part_class: str, msg: str = None
    ) -> None:
        """
        Wait until a specific part of class name appears on the element.

        Args:
            part_class: Substring of class to wait for.
            msg: Optional extra message for error context.

        Raises:
            ElementLocationException: If class part did not appear.
        """
        css = self._fmt_locator()
        push_step(f'wait_part_appear_in_class("{part_class}") on {css}')
        try:
            wait_part_appear_in_class(
                driver=self.driver,
                obj=self.lookup(),
                part_class=part_class,
                msg=msg,
            )
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Class part did not appear",
                locator=css,
                condition=f'class contains "{part_class}"',
                **self._digest_ctx(),
            )
            if msg:
                digest = f"{digest}\n{msg}"
            raise ElementLocationException(digest) from e

    def wait_part_disappear_in_class(
        self, part_class: str, msg: str = None
    ) -> None:
        """
        Wait until a specific part of class name disappears from the element.

        Args:
            part_class: Substring of class to wait for removal.
            msg: Optional extra message for error context.

        Raises:
            ElementLocationException: If class part did not disappear.
        """
        css = self._fmt_locator()
        push_step(f'wait_part_disappear_in_class("{part_class}") on {css}')
        try:
            wait_part_disappear_in_class(
                driver=self.driver,
                obj=self.lookup(),
                part_class=part_class,
                msg=msg,
            )
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Class part did not disappear",
                locator=css,
                condition=f'class does not contain "{part_class}"',
                **self._digest_ctx(),
            )
            if msg:
                digest = f"{digest}\n{msg}"
            raise ElementLocationException(digest) from e

    def scroll(self, base_element: Any = None) -> None:
        """Scroll the element into view relative to a base element."""
        scroll_to_element(self.driver, self.lookup(), base_element)

    def get_attribute(self, name: str) -> str | None:
        """Return the value of an attribute from the element."""
        return self.lookup().get_attribute(name)

    def check_class_part_presence(self, class_name: str) -> bool:
        """Return True if the element's class attribute contains given text."""
        return class_name in self.lookup().get_attribute("class")

    @property
    def location(self) -> dict:
        """Return the location of the element as a dictionary."""
        return self.lookup().location

    def is_present(self) -> bool:
        """Return True if element exists in DOM."""
        try:
            return bool(self._find_elements())
        except WebDriverException as e:
            log.error(f"[PROMIUM] Original webdriver exception: {e}")
            return False

    @property
    def text(self) -> str:
        """Return the visible text of the element."""
        return self.lookup().text

    def click(self) -> None:
        """
        Click the element.

        Raises:
            ElementLocationException: If click action fails.
        """
        css = self._fmt_locator()
        css_probe = self.locator if self.by == By.CSS_SELECTOR else None
        push_step(f'click("{css}")')
        try:
            self.scroll_into_view()
            self.lookup().click()
        except Exception:
            digest = build_digest(
                self.driver,
                title="Click failed",
                locator=css,
                condition="webelement.click()",
                css_for_probe=css_probe,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from None

    def js_click(self) -> None:
        """Perform click using JavaScript executor."""
        css = self._fmt_locator()
        push_step(f'js_click("{css}")')
        self.driver.execute_script("arguments[0].click()", self.lookup())

    def is_displayed(self) -> bool:
        """Return True if element is displayed."""
        if not self.is_present():
            return False
        return self.lookup().is_displayed()

    def hover_over(self) -> None:
        """Hover the mouse over the element."""
        css = self._fmt_locator()
        push_step(f'hover_over("{css}")')
        ActionChains(self.driver).move_to_element(self.lookup()).perform()

    def hover_over_with_offset(self, xoffset: int = 1, yoffset: int = 1) -> None:
        """Hover mouse over element with offset coordinates."""
        css = self._fmt_locator()
        push_step(f'hover_over_with_offset("{css}", {xoffset}, {yoffset})')
        ActionChains(self.driver).move_to_element_with_offset(
            self.lookup(), xoffset, yoffset
        ).perform()

    def click_with_offset(self, xoffset: int = 1, yoffset: int = 1) -> None:
        """Click element at offset coordinates."""
        css = self._fmt_locator()
        push_step(f'click_with_offset("{css}", {xoffset}, {yoffset})')
        ActionChains(self.driver).move_to_element_with_offset(
            self.lookup(), xoffset, yoffset
        ).click().perform()

    def move_to_element_and_click(self) -> None:
        """Move to element and click on it."""
        css = self._fmt_locator()
        push_step(f'move_to_element_and_click("{css}")')
        ActionChains(self.driver).move_to_element(
            self.lookup()
        ).click().perform()

    @property
    def element_title(self) -> str | None:
        """Return value of the element's 'title' attribute."""
        return self.get_attribute("title")

    @property
    def element_id(self) -> str | None:
        """Return value of the element's 'id' attribute."""
        return self.get_attribute("id")

    def value_of_css_property(self, property_name: str) -> str:
        """Return value of a CSS property."""
        return self.lookup().value_of_css_property(property_name)

    def scroll_into_view(
        self,
        behavior: str = "instant",
        block: str = "center",
        inline: str = "center",
    ) -> Self:
        """
        Scroll element into view using JavaScript.

        Args:
            behavior: Scrolling behavior.
            block: Vertical alignment.
            inline: Horizontal alignment.

        Returns:
            Self reference.
        """
        css = self._fmt_locator()
        push_step(
            f'scroll_into_view("{css}", behavior={behavior},'
            f" block={block}, inline={inline})"
        )
        options = {"behavior": behavior, "block": block, "inline": inline}
        self.driver.execute_script(
            "arguments[0].scrollIntoView(arguments[1]);", self.lookup(), options
        )
        return self

    def drag_and_drop(self, target: Any) -> None:
        """
        Drag element and drop it onto another element.

        Args:
            target: Target element.
        """
        src = self._fmt_locator()
        dst = (
            target._fmt_locator()
            if hasattr(target, "_fmt_locator")
            else "<unknown>"
        )
        push_step(f'drag_and_drop("{src}" -> "{dst}")')
        ActionChains(self.driver).drag_and_drop(
            self.lookup(), target.lookup()
        ).perform()


class Block(ElementBase):
    """
    Represents a block-level element (container).
    Inherits all behavior from ElementBase.
    """


class Element(ElementBase):
    """
    Represents a single element in the DOM.
    Extends ElementBase with additional Selenium-like APIs.
    """

    @property
    def tag_name(self) -> str:
        """Return the element's tag name."""
        return self.lookup().tag_name

    def submit(self) -> None:
        """Submit a form element."""
        return self.lookup().submit()

    def is_selected(self) -> bool:
        """Return True if checkbox or radio button is selected."""
        return self.lookup().is_selected()

    def is_enabled(self) -> bool:
        """Return True if the element is enabled."""
        return self.lookup().is_enabled()

    @property
    def location_once_scrolled_into_view(self) -> dict:
        """
        Return location of element once scrolled into view.

        Warning:
            May change without notice. Intended for internal Selenium usage.
        """
        return self.lookup().location_once_scrolled_into_view

    @property
    def size(self) -> dict:
        """Return the size of the element."""
        return self.lookup().size

    @property
    def id(self) -> str:  # noqa: A003
        """
        Return internal Selenium ID of the element.

        Mainly for internal use (e.g., element comparison).
        """
        return self.lookup().id

    def wait_to_staleness(self) -> Self:
        """Wait until element becomes stale (detached from DOM)."""
        css = self._fmt_locator()
        push_step(f'wait_to_staleness("{css}")')
        try:
            return wait_until(
                driver=self.driver,
                expression=EC.staleness_of(self.lookup()),
                seconds=10,
            )
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Element did not become stale",
                locator=css,
                condition="staleness_of == True",
                timeout=10,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def wait_frame_and_switch_to_it(self) -> Self:
        """Wait for a frame to be available and switch to it."""
        css = self._fmt_locator()
        push_step(f'wait_frame_and_switch_to_it("{css}")')
        try:
            return wait_until(
                driver=self.driver,
                expression=EC.frame_to_be_available_and_switch_to_it(
                    self.lookup()
                ),
                seconds=10,
            )
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Frame is not available / switch failed",
                locator=css,
                condition="frame_to_be_available_and_switch_to_it == True",
                timeout=10,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def wait_for_text_present(self, text: str) -> Self:
        """
        Wait until given text is present in element.

        Args:
            text: Expected text value.
        """
        css = self._fmt_locator()
        push_step(f'wait_for_text_present("{css}", text="{text}")')
        try:
            return wait_until(
                driver=self.driver,
                seconds=10,
                expression=text_to_be_present_in_element(self, text),
                msg="",
            )
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Text not present in element",
                locator=css,
                condition=f'text contains "{text}"',
                timeout=10,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def set_inner_html(self, value: str) -> None:
        """Set innerHTML of element via JavaScript."""
        self.driver.execute_script(
            f'arguments[0].innerHTML = "{value}"', self.lookup()
        )

    def hover_over_and_click(self, on_element: Any = None) -> None:
        """
        Hover over this element and click on another element.

        Args:
            on_element: Target element to click.
        """
        css = self._fmt_locator()
        target_css = (
            on_element._fmt_locator()
            if hasattr(on_element, "_fmt_locator")
            else "<unknown>"
        )
        push_step(f'hover_over_and_click("{css}" -> "{target_css}")')
        try:
            ActionChains(self.driver).move_to_element(self.lookup()).click(
                on_element.lookup()
            ).perform()
        except Exception as e:
            digest = build_digest(
                self.driver,
                title="hover_over_and_click failed",
                locator=f"{css} -> {target_css}",
                condition="ActionChains.move_to_element(...).click(...).perform()",
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def drag_and_drop_by_offset(self, xoffset: int, yoffset: int) -> None:
        """
        Drag element by specified offsets.

        Args:
            xoffset: Horizontal offset.
            yoffset: Vertical offset.
        """
        css = self._fmt_locator()
        push_step(f'drag_and_drop_by_offset("{css}", {xoffset}, {yoffset})')
        ActionChains(self.driver).drag_and_drop_by_offset(
            self.lookup(), xoffset, yoffset
        ).perform()

    def wait_for_changes_text_attribute(self, name_attr: str, text: str) -> Self:
        """
        Wait until an attribute's text value changes.

        Args:
            name_attr: Attribute name.
            text: Current value to compare against.
        """
        css = self._fmt_locator()
        push_step(
            f'wait_for_changes_text_attribute("{css}", attr="{name_attr}")'
        )
        try:
            return wait_until(
                driver=self.driver,
                expression=lambda driver: text != self.get_attribute(name_attr),
                seconds=10,
                msg="",
            )
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Attribute text has not changed",
                locator=css,
                condition=f'{name_attr} != "{text}"',
                timeout=10,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def wait_for_text_change(self, text: str = None) -> Self:
        """
        Wait until the element's text changes.

        Args:
            text: Optional initial text. If None, current text is used.
        """
        css = self._fmt_locator()
        element_text = text if isinstance(text, str) else self.text
        push_step(f'wait_for_text_change("{css}", from="{element_text}")')
        try:
            return wait_until(
                driver=self.driver,
                expression=lambda driver: element_text != self.text,
                seconds=5,
                msg="",
            )
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Text did not change",
                locator=css,
                condition=f'text != "{element_text}"',
                timeout=5,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e

    def wait_to_enabled(self, time: int = 10) -> Self:
        """
        Wait until element is enabled (not disabled).

        Args:
            time: Maximum wait time in seconds.
        """
        css = self._fmt_locator()
        push_step(f'wait_to_enabled("{css}", {time}s)')
        try:
            wait = WebDriverWait(
                self.driver, time, ignored_exceptions=[WebDriverException]
            )
            return wait.until(
                lambda driver: self
                if self.get_attribute("disabled") != "true"
                else False
            )
        except TimeoutException as e:
            digest = build_digest(
                self.driver,
                title="Element is not enabled",
                locator=css,
                condition='attribute "disabled" != "true"',
                timeout=time,
                **self._digest_ctx(),
            )
            raise ElementLocationException(digest) from e
