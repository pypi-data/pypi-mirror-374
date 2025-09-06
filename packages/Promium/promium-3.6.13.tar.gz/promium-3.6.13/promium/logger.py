import ast
import json
import logging
import os
import py
import re
from collections.abc import Callable
from functools import wraps
from typing import Any

import allure
import pytest
from selenium.common.exceptions import WebDriverException


log = logging.getLogger(__name__)

MAX_SYMBOLS = 510
TABS_FORMAT = " " * 20


def repr_console_errors(console_errors: Any, tabs: str = TABS_FORMAT) -> str:
    """Format console errors for logging."""
    return f"\n{tabs}".join(
        f">>> [CONSOLE ERROR] {error}" for error in set(console_errors)
    )


def repr_args(*args: Any, **kwargs: Any) -> str:
    """Format function arguments for logging."""
    return "{args}{mark}{kwargs}".format(
        args=", ".join([str(x) for x in args]) if args else "",
        kwargs=", ".join(f"{k}={v}" for k, v in kwargs.items())
        if kwargs
        else "",
        mark=", " if args and kwargs else "",
    )


def find_console_browser_errors(driver: Any) -> set[str] | None:
    """Return browser console errors, skipping ignored hosts if set."""
    try:
        browser_errors = [
            x["message"]
            for x in list(
                filter(
                    lambda x: x["level"] == "SEVERE",
                    driver.get_log("browser"),
                )
            )
        ]
    except WebDriverException as e:
        log.warning(f"Exception when reading Browser Console log: {str(e)}")
        return None
    else:
        is_skipped_hosts = os.environ.get("SKIPPED_HOSTS")
        if is_skipped_hosts and browser_errors:
            for host in ast.literal_eval(is_skipped_hosts):
                browser_errors = list(
                    filter(lambda x: host not in x, browser_errors)
                )
                if not browser_errors:
                    break
        return set(browser_errors)


def logger_for_element_methods(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for logging element method calls and console errors."""

    @wraps(fn)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        res = fn(self, *args, **kwargs)
        console_errors = find_console_browser_errors(self.driver)
        is_check = os.environ.get("CHECK_CONSOLE")
        if console_errors:
            log.warning(
                "Browser console js error found:\n"
                f"{TABS_FORMAT}{repr_console_errors(console_errors)}\n"
                f"{TABS_FORMAT}Url: {self.driver.current_url}\n"
                f"{TABS_FORMAT}Action: {self.__class__.__name__}"
                f"({self.by}={self.locator})"
                f".{fn.__name__}({repr_args(*args, **kwargs)})"
            )

            with allure.step("[Console Error] ⚠️"):
                for err in console_errors:
                    split_type = "\\n" if "\\n" in err else "\n"
                    allure.attach(
                        name="js error",
                        body=json.dumps(err.strip().split(split_type), indent=4),
                        attachment_type=allure.attachment_type.JSON,
                    )

            error_tmpl = (
                "Url: {url}\n"
                "Action: {class_name}({by}={locator})"
                ".{method}({args})\n"
                "{end_symbol}".format(
                    class_name=self.__class__.__name__,
                    by=self.by,
                    locator=self.locator,
                    method=fn.__name__,
                    args=repr_args(*args, **kwargs),
                    url=self.driver.current_url,
                    end_symbol="-" * 75,
                )
            )
            if is_check and hasattr(self.driver, "console_errors"):
                for err in set(console_errors):
                    self.driver.console_errors.append(
                        f">>> [CONSOLE ERROR] {err}\n {error_tmpl}"
                    )
        return res

    return wrapper


def add_logger_to_base_element_classes(cls: type[Any]) -> type[Any]:
    """Decorate all public methods of a class with console logging."""
    for name, method in cls.__dict__.items():
        log.info(f"{name}, {method}")
        if not name.startswith("_") and callable(method) and name != "lookup":
            setattr(cls, name, logger_for_element_methods(method))
    return cls


def logger_for_loading_page(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for logging page loading with console error checks."""

    @wraps(fn)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        res = fn(self, *args, **kwargs)
        if os.environ.get("CHECK_CONSOLE"):
            console_errors = find_console_browser_errors(self.driver)
            if console_errors:
                log.warning(
                    "Browser console js error found:\n"
                    f"{TABS_FORMAT}{repr_console_errors(console_errors)}\n"
                    f"{TABS_FORMAT}Url: {self.driver.current_url}\n"
                    f"{TABS_FORMAT}Action: wait for page loaded ..."
                )
                if hasattr(self.driver, "console_errors"):
                    for err in set(console_errors):
                        self.driver.console_errors.append(
                            ">>> [CONSOLE ERROR] {err}\n"
                            "Url: {url}\n"
                            "Action: wait for page loaded ...\n"
                            "{end_symbol}".format(
                                url=self.driver.current_url,
                                err=err,
                                end_symbol="-" * 75,
                            )
                        )
        return res

    return wrapper


IGNORE_LOG_MESSAGES = [
    "InsecureRequestWarning: Unverified HTTPS request is being made. "
    "Adding certificate verification is strongly advised.",
    "Starting new HTTP connection",
    "Starting new HTTPS connection",
]


class LoggerFilter(logging.Filter):
    """Filter for ignoring specific log messages."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa A003
        if hasattr(record, "msg"):
            is_ignore = any(
                set(filter(lambda x: x in record.msg, IGNORE_LOG_MESSAGES))
            )
            if is_ignore:
                return False
        return record.levelno > 10


class Logger:
    """Logger integration with pytest runtime."""

    def pytest_runtest_setup(self, item: Any) -> None:
        """Attach custom log handler at test setup."""
        item.capturelog_handler = LoggerHandler()
        item.capturelog_handler.setFormatter(
            logging.Formatter(
                "%(asctime)-12s%(levelname)-8s%(message)s\n", "%H:%M:%S"
            )
        )
        root_logger = logging.getLogger()
        item.capturelog_handler.addFilter(LoggerFilter())
        root_logger.addHandler(item.capturelog_handler)
        root_logger.setLevel(logging.NOTSET)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: Any, call: Any) -> Any:
        """Hook to capture and attach logs to pytest reports."""
        outcome = yield
        report = outcome.get_result()
        if hasattr(item, "capturelog_handler"):
            if call.when == "teardown":
                root_logger = logging.getLogger()
                root_logger.removeHandler(item.capturelog_handler)
            if not report.passed:
                longrepr = getattr(report, "longrepr", None)
                if hasattr(longrepr, "addsection"):
                    captured_log = item.capturelog_handler.stream.getvalue()
                    if captured_log:
                        longrepr.sections.insert(
                            len(longrepr.sections),
                            ("Captured log", f"\n{captured_log}", "-"),
                        )
                        if item.config.getoption("--allure-report"):
                            allure.attach(
                                captured_log,
                                name="CAPTURED LOG",
                                attachment_type=allure.attachment_type.TEXT,
                            )
            if call.when == "teardown":
                item.capturelog_handler.close()
                del item.capturelog_handler


class LoggerHandler(logging.StreamHandler):
    """Custom log handler to capture logs into pytest."""

    def __init__(self) -> None:
        logging.StreamHandler.__init__(self)
        self.stream = py.io.TextIO()
        self.records: list[logging.LogRecord] = []

    def close(self) -> None:
        """Close the handler and underlying stream."""
        logging.StreamHandler.close(self)
        self.stream.close()


def request_logging(request: Any, url: str, method: str, **kwargs: Any) -> None:
    """Log outgoing requests with response details."""
    content = str(request.data)
    warning_message = (
        "[Python request] STATUS CODE: {status_code}, LINK: {link}\n"
        "{tabs}METHOD: {method}\n"
        "{tabs}BODY: {body}\n"
        "{tabs}RESPONSE CONTENT: "
        "{content}{ellipsis} ({length} symbols)\n".format(
            status_code=request.status,
            method=method,
            link=url,
            body=kwargs.get("body"),
            content=re.sub(r"\s+", " ", content)[:MAX_SYMBOLS],
            ellipsis=" ..." if len(content) > MAX_SYMBOLS else "",
            length=len(request.data),
            tabs=" " * 12,
        )
    )
    if 400 <= request.status < 500:
        log.warning(warning_message)
    elif request.status >= 500:
        log.error(warning_message)
    else:
        log.info(f"[Python request] STATUS CODE: {request.status}, LINK: {url}")
