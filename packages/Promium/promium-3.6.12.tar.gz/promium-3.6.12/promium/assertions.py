import inspect
import json
import logging
import re
from deepdiff import DeepDiff
from typing import Any, TypeVar

import allure
import urllib3
from json_checker import Checker, CheckerError
from selenium.webdriver.chrome.webdriver import WebDriver

from promium.common import upload_screenshot


CoerceDict = dict[str, type] | None


log = logging.getLogger(__name__)


http = urllib3.PoolManager(
    cert_reqs=False,
    timeout=5,
    headers={
        "Accept-Encoding": "gzip, deflate",
        "Accept": "*/*",
        "Connection": "keep-alive",
    },
)


def base_msg(msg: str) -> str:
    return f"{msg}\n" if msg else ""


T = TypeVar("T")


def _check_namedtuple[T](obj: T) -> dict[str, Any] | T:
    if hasattr(obj, "_asdict"):
        return obj._asdict()
    return obj


def convert_container(container: Any) -> dict | str:
    if not isinstance(container, str):
        return json.dumps(
            obj=container,
            indent=4,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )
    return _check_namedtuple(container)


def get_text_with_ignore_whitespace_symbols(text: str) -> str:
    """Return text excluding spaces and whitespace_symbols"""
    text_without_whitespace_symbols = (
        text.replace("\t", " ")
        .replace("\v", " ")
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("\f", " ")
        .strip()
    )
    text_list = text_without_whitespace_symbols.split(" ")
    text_list_without_space = [word for word in text_list if word]
    return " ".join(text_list_without_space)


class BaseSoftAssertion:
    # TODO is not cleaned in unit tests need use __init__
    assertion_errors = []

    def get_assert_call_lines(self) -> str:
        caller_frame_info = inspect.stack()[2]
        filename = caller_frame_info.filename
        lineno = caller_frame_info.lineno
        if "/site-packages/" not in filename:  # skip recursive calls
            return f"{filename}:{lineno}\n"
        return ""

    def add_screenshot(self, error_msg: str = "soft_assertion") -> str:
        if hasattr(self, "driver"):
            try:
                allure.attach(
                    self.driver.get_screenshot_as_png(),
                    name=error_msg,
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                log.error(f"[PROMIUM] Can't attach screenshot: {e}")
            return f"\nScreenshot: {upload_screenshot(self.driver)}\n"
        return ""

    def soft_assert_true(
        self, expr: Any, msg: str = None, with_screen: bool = False
    ) -> str | None:
        """Check that the expression is true."""
        if not expr:
            error = msg or "Is not true."
            screen = self.add_screenshot(error) if with_screen else ""
            self.assertion_errors.append(
                f"{self.get_assert_call_lines()}{error}{screen}\n"
            )
            return error

    def soft_assert_false(
        self, expr: Any, msg: str = None, with_screen: bool = False
    ) -> str | None:
        """Check that the expression is false."""
        if expr:
            error = msg or "Is not false."
            screen = self.add_screenshot(error) if with_screen else ""
            self.assertion_errors.append(
                f"{self.get_assert_call_lines()}{error}{screen}\n"
            )
            return error

    def soft_assert_equals(
        self,
        current: Any,
        expected: Any,
        msg: str = None,
        show_diff: bool = False,
        with_screen: bool = False,
    ) -> str | None:
        """Just like self.soft_assert_true(current == expected)"""
        diff = None
        if type(current) is list and type(expected) is list:
            diff = DeepDiff(current, expected, ignore_order=True)
        if show_diff and type(current) is str and type(expected) is str:
            current_splitlines = current.splitlines()
            expected_splitlines = expected.splitlines()
            if len(current_splitlines) > 1 or len(expected_splitlines) > 1:
                diff = DeepDiff(current_splitlines, expected_splitlines)
        difference = f"\nDifference:\n{convert_container(diff)}" if diff else ""

        type_current = type_expected = ""
        if type(current) is not type(expected):
            type_current = f"({type(current)})"
            type_expected = f"({type(expected)})"

        assert_message = (
            f"{self.get_assert_call_lines()}"
            f"{base_msg(msg)}\n"
            f"Current - {convert_container(current)} {type_current}\n"
            f"Expected - {convert_container(expected)} {type_expected}\n"
            f"{difference}"
        )
        return self.soft_assert_true(
            current == expected, assert_message, with_screen
        )

    def soft_assert_not_equals(
        self,
        current: Any,
        expected: Any,
        msg: str = None,
        with_screen: bool = False,
    ) -> str | None:
        """Just like self.soft_assert_true(current != expected)"""
        message = (
            f"{self.get_assert_call_lines()}"
            f"{base_msg(msg)}\n"
            f"Current - {convert_container(current)}\n"
            f"Expected - {convert_container(expected)}\n"
        )
        self.soft_assert_false(current == expected, message, with_screen)

    def soft_assert_in(
        self,
        member: Any,
        container: Any,
        msg: str = None,
        with_screen: bool = False,
    ) -> str | None:
        """Just like self.soft_assert_true(member IN container)"""
        msg = (
            f"{self.get_assert_call_lines()}"
            f"{base_msg(msg)}\n"
            f"Member: '{member}'\n not found in\n"
            f"Container: '{convert_container(container)}'\n"
        )
        return self.soft_assert_true(member in container, msg, with_screen)

    def soft_assert_not_in(
        self,
        member: Any,
        container: Any,
        msg: str = None,
        with_screen: bool = False,
    ) -> str | None:
        """Just like self.soft_assert_true(member NOT IN container)"""
        msg = (
            f"{self.get_assert_call_lines()}"
            f"{base_msg(msg)}\n"
            f"Member: '{member}'\n unexpectedly found in\n"
            f"Container: '{convert_container(container)}'\n"
        )
        return self.soft_assert_true(member not in container, msg, with_screen)

    def soft_assert_less_equal(
        self, a: Any, b: Any, msg: str = None, with_screen: bool = False
    ) -> str | None:
        """Just like self.soft_assert_true(a <= b)"""
        error = (
            f"{self.get_assert_call_lines()}"
            f"{base_msg(msg)}{a} not less than or equal to {b}\n"
        )
        return self.soft_assert_true(a <= b, error, with_screen)

    def soft_assert_less(
        self, a: Any, b: Any, msg: str = None, with_screen: bool = False
    ) -> str | None:
        """Just like self.soft_assert_true(a < b)"""
        error = (
            f"{self.get_assert_call_lines()}"
            f"{base_msg(msg)}{a} not less than {b}\n"
        )
        return self.soft_assert_true(a < b, error, with_screen)

    def soft_assert_greater_equal(
        self, a: Any, b: Any, msg: str = None, with_screen: bool = False
    ) -> str | None:
        """Just like self.soft_assert_true(a >= b)"""
        error = (
            f"{self.get_assert_call_lines()}"
            f"{base_msg(msg)}{a} not greater than or equal to {b}\n"
        )
        return self.soft_assert_true(a >= b, error, with_screen)

    def soft_assert_greater(
        self, a: Any, b: Any, msg: str = None, with_screen: bool = False
    ) -> str | None:
        """Just like self.soft_assert_true(a > b)"""
        error = (
            f"{self.get_assert_call_lines()}"
            f"{base_msg(msg)}{a} not greater than {b}\n"
        )
        return self.soft_assert_true(a > b, error, with_screen)

    def soft_assert_regexp_matches(
        self, text: str, expected_regexp: str, msg: str = None
    ) -> str | None:
        """Fail the test unless the text matches the regular expression."""
        pattern = re.compile(expected_regexp)
        result = pattern.search(text)

        if not result:
            error = (
                f"{self.get_assert_call_lines()}"
                f"{base_msg(msg)}"
                f"Regexp didn't match."
                f"Pattern {str(pattern.pattern)} not found in {str(text)}\n"
            )
            self.assertion_errors.append(error)
            return error

    def soft_assert_disable(
        self, element: Any, msg: str = None, with_screen: bool = False
    ) -> str:
        """Check that the obj hasn't attribute."""
        default_msg = "" if msg else f"Not disabled {element}\n"
        error = f"{self.get_assert_call_lines()}{base_msg(msg)}{default_msg}"
        return self.soft_assert_true(
            element.get_attribute("disabled"), error, with_screen
        )

    def soft_assert_is_none(self, obj: Any, msg: str = None) -> str:
        """Same as self.soft_assert_true(obj is None)."""
        default_msg = "" if msg else f"{obj} is not None.\n"
        error = f"{self.get_assert_call_lines()}{base_msg(msg)}{default_msg}"
        return self.soft_assert_true(obj is None, error)

    def soft_assert_is_not_none(self, obj: Any, msg: str = None) -> str:
        """Included for symmetry with self.soft_assert_is_none."""
        default_msg = "" if msg else "Unexpectedly None.\n"
        error = f"{self.get_assert_call_lines()}{base_msg(msg)}{default_msg}"
        return self.soft_assert_true(obj is not None, error)

    def soft_assert_is_instance(
        self, obj: Any, cls: Any, msg: str = None
    ) -> str:
        """Same as self.soft_assert_true(isinstance(obj, cls))"""
        default_msg = "" if msg else f"{obj} is not an instance of {cls}.\n"
        error = f"{self.get_assert_call_lines()}{base_msg(msg)}{default_msg}"
        return self.soft_assert_true(isinstance(obj, cls), error)

    def soft_assert_equals_text_with_ignore_spaces_and_register(
        self,
        current_text: str,
        expected_text: str,
        msg: str = "Invalid checked text.",
        with_screen: bool = False,
    ) -> None:
        """Checking of text excluding spaces and register"""
        current = get_text_with_ignore_whitespace_symbols(current_text)
        expected = get_text_with_ignore_whitespace_symbols(expected_text)
        if not current:
            msg = "Warning: current text is None!"
        self.soft_assert_equals(
            current.lower(),
            expected.lower(),
            f"{self.get_assert_call_lines()}"
            f"{msg}\nCurrent text without formating: {current_text}"
            f"\nExpected text without formating: {expected_text}",
            with_screen=with_screen,
        )

    def soft_assert_schemas(
        self, current: dict, expected: dict, msg: str = ""
    ) -> str | None:
        """
        Example:
            {'test1': 1} == {'test1: int}

        :param dict current: current response
        :param dict expected: expected dict(key: type)
        :param str msg:
        :return error
        """
        try:
            Checker(expected, soft=True).validate(current)
        except CheckerError as e:
            error = f"{self.get_assert_call_lines()}{msg}\n{e}\n"
            self.assertion_errors.append(error)
            return error

    def assert_keys_and_instances(
        self,
        actual_dict: dict,
        expected_dict: dict,
        can_be_null: list = None,
        msg: str = None,
    ) -> None:
        """
        :param dict actual_dict:
        :param dict expected_dict:
        :param list | None can_be_null: must be if default value None
        :param basestring msg:
        """
        assert actual_dict, "Actual dict is empty, check your data"

        self.soft_assert_equals(
            sorted(iter(actual_dict.keys())),
            sorted(iter(expected_dict.keys())),
            f"{self.get_assert_call_lines()}Wrong keys list.",
        )
        for actual_key, actual_value in actual_dict.items():
            self.soft_assert_in(
                member=actual_key,
                container=expected_dict,
                msg=(
                    f"{self.get_assert_call_lines()}"
                    f'Not expected key "{actual_key}".'
                ),
            )
            if actual_key in expected_dict:
                expected_value = (
                    type(None)
                    if actual_value is None and actual_key in (can_be_null or [])
                    else expected_dict[actual_key]
                )
                message = f"({msg})" if msg else ""
                self.soft_assert_true(
                    expr=isinstance(actual_value, expected_value),
                    msg=(
                        f"{self.get_assert_call_lines()}"
                        f"Wrong object instance class.\n"
                        f'Key "{actual_key}" value is "{type(actual_value)}", '
                        f'expected "{expected_value}". {message}'
                    ),
                )

    def soft_assert_dicts_with_ignore_types(
        self, current: Any, expected: Any, msg: str = ""
    ) -> None:
        """
        Comparison of two dicts with ignoring type of values
        If the dict key was lost, print it in missing list.
        """
        expected_dict = _check_namedtuple(expected)
        current_dict = _check_namedtuple(current)
        errors = ""
        for actual_key, actual_value in current_dict.items():
            if actual_key in expected_dict:
                if str(actual_value) != str(expected_dict[actual_key]):
                    errors += (
                        f"\nKey {actual_key} "
                        f"\nHas not correct value:  {actual_value}  "
                        f"Must be have this:  {expected_dict[actual_key]} \n"
                    )
        if errors:
            self.assertion_errors.append(
                f"{self.get_assert_call_lines()}"
                f"{msg}"
                f"{errors}"
                f"\nExpected dict: {convert_container(expected_dict)}"
                f"\nCurrent dict: {convert_container(current_dict)}"
            )

    def soft_assert_equal_dict_from_clerk_magic(
        self,
        current_dict: dict,
        expected_dict: dict,
        msg: str = None,
        coerce: CoerceDict = None,
    ) -> None:
        """
        Comparison by type, if the types do not match - compares in a string
        If the dict key was lost, print it in missing list.
        """

        def _equal(
            field_name: str, current: str, expected: str, type_coerce: CoerceDict
        ) -> bool:
            if type_coerce is not None and field_name in type_coerce:
                cast = type_coerce[field_name]
                return cast(current) == cast(expected)
            if type(current) is type(expected):
                return current == expected
            return str(current) == str(expected)

        missing = []
        unequal = []
        for key, value in expected_dict.items():
            if key not in current_dict:
                missing.append((key, value))
            elif not _equal(key, value, current_dict[key], coerce):
                unequal.append((
                    key,
                    f"\n\t\tproduct_data - '{value}'"
                    f" != analytic_data - '{current_dict[key]}'",
                ))

        unequal_check = "\n\t".join([":".join(map(str, a)) for a in unequal])
        missing_check = "\n\t".join([":".join(map(str, a)) for a in missing])
        self.soft_assert_true(
            (missing, unequal) == ([], []),
            msg=(
                f"{self.get_assert_call_lines()}"
                f"{base_msg(msg)}\n"
                f"Unequal_keys:\n\t{unequal_check}\n"
                f"\nMissed_keys:\n\t[{missing_check}]"
            ),
        )


class RequestSoftAssertion(BaseSoftAssertion):
    @property
    def url(self) -> str:
        return self.session.url

    def base_msg(self, msg: str = None) -> str:
        url = f"\n{self.url}" if self.url else ""
        exception = f"\n{msg}" if msg else ""
        return f"{url}{exception}"


class WebDriverSoftAssertion(BaseSoftAssertion):
    @property
    def driver(self) -> WebDriver:
        return self.driver

    @property
    def url(self) -> str:
        return self.driver.current_url

    def base_msg(self, default_msg: str = None, extend_msg: str = None) -> str:
        default = f"Default message: {default_msg}\n" if default_msg else ""
        extend = f"Extend message: {extend_msg}\n" if extend_msg else ""
        return f"{default}{extend}\nURL: {self.url}"

    def soft_assert_page_title(
        self, expected_title: str, msg: str = None
    ) -> None:
        """Page title is equals to expected_title"""
        default_msg = "Wrong page title."
        error = (
            f"{self.get_assert_call_lines()}"
            f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}"
        )
        self.soft_assert_equals(self.driver.title, expected_title, error)

    def soft_assert_current_url(
        self, expected_url: str, msg: str = None
    ) -> None:
        """Current url is equals to expected_title"""
        default_msg = "Wrong current url."
        error = (
            f"{self.get_assert_call_lines()}"
            f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}"
        )
        self.soft_assert_equals(self.url, expected_url, error)

    def soft_assert_current_url_contains(
        self, url_mask: str, msg: str = None
    ) -> None:
        """Current url contains ulr mask"""
        default_msg = f"URL {str(self.url)} doesn't contains {str(url_mask)}."
        error = (
            f"{self.get_assert_call_lines()}"
            f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}"
        )
        self.soft_assert_in(url_mask, self.url, error)

    def soft_assert_current_url_not_contains(
        self, url_mask: str, msg: str = None
    ) -> None:
        """Current url does not contain ulr mask"""
        default_msg = f"URL {str(self.url)} contains {str(url_mask)}."
        error = (
            f"{self.get_assert_call_lines()}"
            f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}"
        )
        self.soft_assert_not_in(url_mask, self.url, error)

    def soft_assert_element_is_present(
        self, element: Any, msg: str = None
    ) -> None:
        """Element is present"""
        default_msg = (
            f"Element {element.by}={element.locator} is not present "
            f"on page at current time."
        )
        error = (
            f"{self.get_assert_call_lines()}"
            f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}"
        )
        self.soft_assert_true(element.is_present(), error, with_screen=True)

    def soft_assert_element_is_not_present(
        self, element: Any, msg: str = None
    ) -> None:
        """Element is not present"""
        default_msg = f"Element {element.by}={element.locator} is found on page."
        error = (
            f"{self.get_assert_call_lines()}"
            f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}"
        )
        self.soft_assert_false(element.is_present(), error, with_screen=True)

    def soft_assert_element_is_displayed(
        self, element: Any, msg: str = None
    ) -> None:
        """Element is displayed to user"""
        default_msg = (
            f"Element {element.by}={element.locator} is not visible to a user."
        )
        error = (
            f"{self.get_assert_call_lines()}"
            f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}"
        )
        self.soft_assert_true(element.is_displayed(), error, with_screen=True)

    def soft_assert_element_is_not_displayed(
        self, element: Any, msg: str = None
    ) -> None:
        """Element is not displayed to user"""
        default_msg = (
            f"Element {element.by}={element.locator} is visible to a user."
        )
        error = (
            f"{self.get_assert_call_lines()}"
            f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}"
        )
        self.soft_assert_false(element.is_displayed(), error, with_screen=True)

    def soft_assert_element_displayed_in_viewport(
        self, element: Any, msg: str = None
    ) -> None:
        """This method checks that element is viewable in viewport"""
        element_in_viewport = self.driver.execute_script(
            """
            function elementInViewport(el) {
                var top = el.offsetTop;
                var left = el.offsetLeft;
                var width = el.offsetWidth;
                var height = el.offsetHeight;


                while(el.offsetParent) {
                el = el.offsetParent;
                top += el.offsetTop;
                left += el.offsetLeft;
                }

                return (
                    top >= window.pageYOffset &&
                    left >= window.pageXOffset &&
                    (top + height) <= (window.pageYOffset + window.innerHeight)
                    &&
                    (left + width) <= (window.pageXOffset + window.innerWidth)
                );
            }

            element = arguments[0];
            return elementInViewport(element);
            """,
            element.lookup(),
        )

        if element_in_viewport is not True:
            default_msg = (
                f"Element {element.by}={element.locator} "
                f"not displayed in viewport"
            )
            error = (
                f"{self.get_assert_call_lines()}"
                f"{self.base_msg(default_msg=default_msg, extend_msg=msg)}\n\n"
            )
            self.assertion_errors.append(error)

    def soft_assert_image_status_code(
        self, image: Any, status_code: int = 200, msg: str = None
    ) -> str | None:
        """Compare image url status code with expected status code"""
        if not image.get_attribute("src"):
            return self.assertion_errors.append(
                f"{self.get_assert_call_lines()}"
                f"{base_msg(msg)}"
                "Image does not have attribute 'src'\n\n"
            )

        img_url = image.get_attribute("src")
        response = http.request(url=img_url, method="GET")

        assert_msg = msg if msg else "img status code != 200"
        self.soft_assert_equals(
            response.status,
            status_code,
            msg=f"{self.get_assert_call_lines()}{assert_msg}",
        )
