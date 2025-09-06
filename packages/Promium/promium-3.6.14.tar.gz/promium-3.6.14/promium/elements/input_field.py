import contextlib

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from promium.base import Element
from promium.logger import log


try:
    from promium._diag import push_step
except Exception:  # pragma: no cover

    def push_step(_: str) -> None:  # type: ignore
        pass


class InputField(Element):
    """Represents an input field element with helper methods."""

    @property
    def value(self) -> str | None:
        """Return the current value of the input field."""
        return self.get_attribute("value")

    @property
    def placeholder(self) -> str | None:
        """Return the placeholder text of the input field."""
        return self.get_attribute("placeholder")

    def clear(self) -> None:
        """Clear the input field using the default clear method."""
        with contextlib.suppress(Exception):
            push_step(f'clear("{self._fmt_locator()}")')
        self.lookup().clear()

    def set_value(self, value: str) -> None:
        """Set the input field value directly via JavaScript."""
        with contextlib.suppress(Exception):
            push_step(f'set_value("{self._fmt_locator()}")')
        self.driver.execute_script(
            "arguments[0].value = arguments[1];", self.lookup(), value
        )

    def send_keys(self, *keys) -> None:
        """Send key presses to the input field."""
        with contextlib.suppress(Exception):
            push_step(f'send_keys("{self._fmt_locator()}")')
        self.lookup().send_keys(*keys)

    def _clear_field_with_keyboard(self) -> None:
        """Clear the field using only WebElement/ActionChains to avoid
        overridden send_keys."""
        with contextlib.suppress(Exception):
            push_step(f'clear_with_keyboard("{self._fmt_locator()}")')
        el = self.lookup()
        with contextlib.suppress(Exception):
            el.click()
        for mod in (Keys.CONTROL, Keys.COMMAND):
            try:
                el.send_keys(mod, "a")
                break
            except TypeError:
                try:
                    ActionChains(self.driver).key_down(mod).send_keys(
                        "a"
                    ).key_up(mod).perform()
                    break
                except Exception:
                    pass
            except Exception:
                continue
        cleared = False
        for key in (Keys.DELETE, Keys.BACKSPACE):
            try:
                el.send_keys(key)
                cleared = True
                break
            except TypeError:
                with contextlib.suppress(Exception):
                    ActionChains(self.driver).send_keys(key).perform()
                    cleared = True
                    break
            except Exception:
                continue
        if not cleared:
            with contextlib.suppress(Exception):
                el.clear()

    def clear_and_fill(self, text: str) -> str | None:
        """Clear the field using keyboard and fill it with the given text."""
        with contextlib.suppress(Exception):
            push_step(f'clear_and_fill("{self._fmt_locator()}")')

        expected_text = str(text).lower()
        self._clear_field_with_keyboard()
        self.send_keys(text)
        if (self.value or "").lower() == expected_text:
            return expected_text
        log.warning(
            "Different text input value after clear with keyboard and fill. "
            f"Expected - {expected_text}, current - {self.value}"
        )

    def fill_field(self, text: str) -> str | None:
        """Clear existing value (if any) and fill the input field with text."""
        with contextlib.suppress(Exception):
            push_step(f'fill_field("{self._fmt_locator()}")')

        expected_text = str(text).lower()
        if self.value:
            self.clear()
        self.send_keys(text)
        if (self.value or "").lower() == expected_text:
            return expected_text
        log.warning(
            "Different text input value after fill. "
            f"Expected - {expected_text}, current - {self.value}"
        )
