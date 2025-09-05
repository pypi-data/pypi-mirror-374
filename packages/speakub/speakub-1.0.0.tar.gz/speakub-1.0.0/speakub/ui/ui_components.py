"""
Common UI components for the EPUB reader.
"""

from rich.text import Text
from textual.widgets import Static

from speakub.utils.text_utils import str_display_width


class PanelTitle(Static):
    """A custom Static widget that renders a main title and a right-aligned secondary title."""

    def __init__(self, main_title: str, **kwargs):
        super().__init__(main_title, **kwargs)
        self.main_title = main_title
        self.right_title = ""

    def update_texts(
        self, main_title: str | None = None, right_title: str | None = None
    ) -> None:
        """Update the titles and refresh the widget."""
        if main_title is not None:
            self.main_title = main_title
        if right_title is not None:
            self.right_title = right_title
        self.refresh()

    def render(self) -> Text:
        """Render the title with right-aligned secondary text."""
        panel_width = self.size.width

        if panel_width == 0:
            return Text(self.main_title)

        main_width = str_display_width(self.main_title)
        right_width = str_display_width(self.right_title)

        padding = panel_width - main_width - right_width - 2
        if padding < 1:
            padding = 1

        full_title_str = f"{self.main_title}{' ' * padding}{self.right_title}"

        return Text(full_title_str, no_wrap=True, overflow="ellipsis")
