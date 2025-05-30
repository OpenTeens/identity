from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, override

from rich.logging import RichHandler

if TYPE_CHECKING:
    from logging import LogRecord

    from rich.console import ConsoleRenderable
    from rich.traceback import Traceback


class MyHandler(RichHandler):
    @override
    def render(
        self,
        *,
        record: LogRecord,
        traceback: Traceback | None,
        message_renderable: ConsoleRenderable,
    ) -> ConsoleRenderable:
        """Render log for display.

        Args: record (LogRecord): logging Record. traceback (Optional[Traceback]):
        Traceback instance or None for no Traceback. message_renderable (
        ConsoleRenderable): Renderable (typically Text) containing log message contents.

        Returns:
            ConsoleRenderable: Renderable to display log.

        """
        level = self.get_level_text(record)
        time_format = None if self.formatter is None else self.formatter.datefmt
        log_time = datetime.fromtimestamp(record.created)  # noqa: DTZ006

        return self._log_render(
            self.console,
            [message_renderable] if not traceback else [message_renderable, traceback],
            log_time=log_time,
            time_format=time_format,
            level=level,
            path=record.name,
            line_no=None,
            link_path=record.pathname if self.enable_link_path else None,
        )
