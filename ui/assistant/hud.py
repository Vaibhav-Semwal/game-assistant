from __future__ import annotations

import math
import signal
import sys

from PySide6.QtCore import QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import QApplication, QWidget

WIDTH = 260
BAR_BOX_HEIGHT = 46
RADIUS = 20
BARS = 20
REFRESH_MS = 50

TEXT_BOX_GAP = 8
TEXT_BOX_PADDING = 10
TEXT_FONT = QFont("Helvetica", 9)

BAR_BG_COLOR = QColor(15, 15, 20, 210)
TEXT_BG_COLOR = QColor(25, 25, 32, 210)
COLORS = {"listening": QColor("#00e0ff"), "speaking": QColor("#7CFF6B")}


class StatusOverlay(QWidget):
    _state_changed = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        self._top_y = 14
        self._center_x = screen.width() // 2
        self.resize(WIDTH, BAR_BOX_HEIGHT)
        self.move(self._center_x - WIDTH // 2, self._top_y)

        self.state = "idle"
        self.text = ""
        self.phase = 0
        self._text_box_height = 0

        self._state_changed.connect(self._apply_state)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(REFRESH_MS)

        self.hide()

    def _text_box_height_for(self, text: str) -> int:
        if not text:
            return 0
        metrics = QFontMetrics(TEXT_FONT)
        available_width = WIDTH - 2 * TEXT_BOX_PADDING
        bounds = metrics.boundingRect(
            QRect(0, 0, available_width, 10_000),
            Qt.TextWordWrap | Qt.AlignCenter,
            text,
        )
        return bounds.height() + 2 * TEXT_BOX_PADDING

    def _apply_state(self, state: str, text: str) -> None:
        self.state = state
        self.text = text if (state == "speaking" and text) else ""
        self._text_box_height = self._text_box_height_for(self.text)

        total_height = BAR_BOX_HEIGHT
        if self._text_box_height:
            total_height += TEXT_BOX_GAP + self._text_box_height

        self.resize(WIDTH, total_height)
        self.move(self._center_x - WIDTH // 2, self._top_y)

        self.show() if state != "idle" else self.hide()
        self.update()

    def _tick(self) -> None:
        if self.state != "idle":
            self.phase += 1
            self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        painter.setBrush(BAR_BG_COLOR)
        painter.drawRoundedRect(0, 0, WIDTH, BAR_BOX_HEIGHT, RADIUS, RADIUS)

        color = COLORS.get(self.state)
        if color is not None:
            bar_w = WIDTH / BARS
            mid_y = BAR_BOX_HEIGHT / 2
            painter.setBrush(color)
            for i in range(BARS):
                amp = 20 * abs(math.sin(self.phase * 0.25 + i * 0.4))
                x = i * bar_w + 2
                painter.drawRoundedRect(x, mid_y - amp / 2, bar_w - 4, max(amp, 3), 2, 2)

        if self._text_box_height:
            text_box_top = BAR_BOX_HEIGHT + TEXT_BOX_GAP
            painter.setBrush(TEXT_BG_COLOR)
            painter.drawRoundedRect(0, text_box_top, WIDTH, self._text_box_height, RADIUS, RADIUS)

            painter.setPen(QColor("white"))
            painter.setFont(TEXT_FONT)
            painter.drawText(
                QRect(
                    TEXT_BOX_PADDING,
                    text_box_top + TEXT_BOX_PADDING,
                    WIDTH - 2 * TEXT_BOX_PADDING,
                    self._text_box_height - 2 * TEXT_BOX_PADDING,
                ),
                Qt.AlignCenter | Qt.TextWordWrap,
                self.text,
            )

    def set_state(self, state: str, text: str | None = None) -> None:
        self._state_changed.emit(state, text or "")

    def run(self) -> None:
        QApplication.instance().exec()


_overlay: "StatusOverlay | None" = None
_keepalive_timer: "QTimer | None" = None


def create_overlay() -> StatusOverlay:
    global _overlay, _keepalive_timer

    app = QApplication.instance() or QApplication(sys.argv)

    signal.signal(signal.SIGINT, lambda *_: app.quit())
    _keepalive_timer = QTimer()
    _keepalive_timer.timeout.connect(lambda: None)
    _keepalive_timer.start(200)

    _overlay = StatusOverlay()
    return _overlay


def ui_set_state(state: str, text: str | None = None) -> None:
    if _overlay is not None:
        _overlay.set_state(state, text)


def ui_shutdown() -> None:
    app = QApplication.instance()
    if app is not None:
        app.quit()