from promium._diag import push_step
from promium.base import Element


class Checkbox(Element):
    def select(self) -> None:
        """Selects checkbox from any default state"""
        css = self._fmt_locator()
        push_step(f'select("{css}")')
        if not self.is_selected():
            self.click()

    def deselect(self) -> None:
        """Deselects checkbox from any default state"""
        css = self._fmt_locator()
        push_step(f'deselect("{css}")')
        if self.is_selected():
            self.click()
