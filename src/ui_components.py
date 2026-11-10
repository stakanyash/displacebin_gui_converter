import os
import sys
import subprocess
import logging
import time
from PyQt6.QtCore import Qt, QSize, QRect, QRectF, QPoint, QUrl, QByteArray, QTimer, pyqtSignal, pyqtProperty, QPropertyAnimation, QEasingCurve, QThread
from PyQt6.QtGui import (
    QColor, QPainter, QPainterPath, QPen, QPixmap, QImage, QIcon, QDesktopServices, QFont, QRegion
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QWidget, QLabel, QToolButton, QPushButton, QHBoxLayout, QVBoxLayout, QFrame,
    QLineEdit, QComboBox, QSizePolicy, QScrollArea, QProgressBar, QTextEdit,
    QButtonGroup, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QAbstractButton
)
from resources import get_asset_path
from config import VERSION, BUILD


def asset_path(filename):
    return os.fspath(get_asset_path(filename))


def tint_pixmap(src: QPixmap, color: str) -> QPixmap:
    if src.isNull():
        return src
    result = QPixmap(src.size())
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawPixmap(0, 0, src)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), QColor(color))
    painter.end()
    return result


def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


_ICON_PATHS = {
    "remove": "M19 13H5v-2h14v2z",
    "close": "M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
    "help_outline": (
        "M11 18h2v-2h-2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 "
        "0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 "
        "2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z"
    ),
    "help": (
        "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75-.9.92C13.45 "
        "12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 "
        ".9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"
    ),
    "public": (
        "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 "
        "0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 "
        "0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"
    ),
    "language": (
        "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zm6.93 6h-2.95a15.65 "
        "15.65 0 0 0-1.38-3.56A8.03 8.03 0 0 1 18.92 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 "
        "1.08-2.76 1.91-3.96zM4.26 14C4.1 13.36 4 12.69 4 12s.1-1.36.26-2h3.38c-.08.66-.14 1.32-.14 2s.06 "
        "1.34.14 2H4.26zm.82 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.987 7.987 0 0 1 5.08 16zm2.95-8H5.08A7.987 "
        "7.987 0 0 1 8.41 4.44 15.65 15.65 0 0 0 7.03 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82c-.43 "
        "1.43-1.08 2.76-1.91 3.96zM14.34 14H9.66c-.09-.66-.16-1.32-.16-2s.07-1.35.16-2h4.68c.09.65.16 1.32.16 "
        "2s-.07 1.34-.16 2zm.25 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95a8.03 8.03 0 0 1-4.33 3.56zM16.36 "
        "14c.08-.66.14-1.32.14-2s-.06-1.34-.14-2h3.38c.16.64.26 1.31.26 2s-.1 1.36-.26 2h-3.38z"
    ),
    "brightness_medium": (
        "M20 15.31 23.31 12 20 8.69V4h-4.69L12 .69 8.69 4H4v4.69L.69 12 4 15.31V20h4.69L12 23.31 15.31 20H20v-4.69zM12 18c-3.31 "
        "0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6z"
    ),
    "brightness_3": (
        "M9 2c-1.05 0-2.05.16-3 .46 4.06 1.27 7 5.06 7 9.54 0 4.48-2.94 8.27-7 9.54.95.3 1.95.46 3 .46 5.52 "
        "0 10-4.48 10-10S14.52 2 9 2z"
    ),
    "swap_horiz": "M6.99 11 3 15l3.99 4v-3H14v-2H6.99v-3zM21 9l-3.99-4v3H10v2h7.01v3L21 9z",
    "swap_vert": "M16 17.01V10h-2v7.01h-3L15 21l4-3.99h-3zM9 3 5 6.99h3V14h2V6.99h3L9 3z",
    "warning": "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z",
    "error": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z",
    "check": "M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
    "info_outline": (
        "M11 17h2v-6h-2v6zm1-15C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 "
        "0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zM11 9h2V7h-2v2z"
    ),
    "download": "M5 20h14v-2H5v2zM19 9h-4V3H9v6H5l7 7 7-7z",
    "system_update": "M17 1.01 7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14zm-1-6h-3V8h-2v5H8l4 4 4-4z",
    "check_circle": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z",
}


def material_icon(name: str, color: str, size: int) -> QIcon:
    path = _ICON_PATHS.get(name, _ICON_PATHS["help_outline"])
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        f'<path fill="{color}" d="{path}"/></svg>'
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class ThemeManager:
    @staticmethod
    def get_theme_colors(theme_mode: str):
        if theme_mode == "dark":
            return {
                "icon_color": "#9ecaff",
                "logo_src": asset_path("logo.png"),
                "topbar_logo": asset_path("icon.ico"),
                "text_color": "#FFFFFF",
                "theme_icon": "brightness_3",
                "theme_icon_hover": "brightness_medium",
                "border_color": "#46678F",
                "version_color": "#9E9E9E",
                "button_color": "#9ecaff",
                "bg": "#1C1B1F",
                "surface": "#1C1B1F",
                "field_bg": "#1C1B1F",
                "button_bg": "#2B2930",
                "button_text": "#9ecaff",
                "fg": "#E6E1E5",
                "muted": "#CAC4D0",
                "radio": "#9ecaff",
                "dropdown_bg": "#2B2930",
                "scrim": "rgba(0, 0, 0, 80)",
                "dialog_bg": "#2B2930",
                "titlebar_btn": "#CAC4D0",
            }
        return {
            "icon_color": "#000000",
            "logo_src": asset_path("logo_white.png"),
            "topbar_logo": asset_path("iconblack.ico"),
            "text_color": "#000000",
            "theme_icon": "brightness_medium",
            "theme_icon_hover": "brightness_3",
            "border_color": "#000000",
            "version_color": "#000000",
            "button_color": "#1976D2",
            "bg": "#FFFBFE",
            "surface": "#FFFBFE",
            "field_bg": "#FFFBFE",
            "button_bg": "#E7E0EC",
            "button_text": "#000000",
            "fg": "#1C1B1F",
            "muted": "#49454F",
            "radio": "#000000",
            "dropdown_bg": "#E7E0EC",
            "scrim": "rgba(0, 0, 0, 90)",
            "dialog_bg": "#FFFBFE",
            "titlebar_btn": "#49454F",
        }


class IconButton(QAbstractButton):
    def __init__(self, icon_name, color, tooltip="", size=24, btn_size=40, hover_icon_name=None, parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._hover_icon_name = hover_icon_name
        self._color = color
        self._icon_px = size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(btn_size, btn_size)

        self._pix_normal = material_icon(icon_name, color, size).pixmap(size, size)
        self._pix_hover = material_icon(hover_icon_name or icon_name, color, size).pixmap(size, size)

        self._hover_progress = 0.0
        self._bg_opacity = 0.0

        self._icon_anim = QPropertyAnimation(self, b"hover_progress")
        self._icon_anim.setDuration(250)
        self._icon_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._bg_anim = QPropertyAnimation(self, b"bg_opacity")
        self._bg_anim.setDuration(150)
        self._bg_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_hover_progress(self):
        return self._hover_progress

    def set_hover_progress(self, v):
        self._hover_progress = v
        self.update()

    hover_progress = pyqtProperty(float, get_hover_progress, set_hover_progress)

    def get_bg_opacity(self):
        return self._bg_opacity

    def set_bg_opacity(self, v):
        self._bg_opacity = v
        self.update()

    bg_opacity = pyqtProperty(float, get_bg_opacity, set_bg_opacity)

    def _update_pixmaps(self):
        self._pix_normal = material_icon(self._icon_name, self._color, self._icon_px).pixmap(self._icon_px, self._icon_px)
        self._pix_hover = material_icon(self._hover_icon_name or self._icon_name, self._color, self._icon_px).pixmap(self._icon_px, self._icon_px)
        self.update()

    def set_color(self, color):
        self._color = color
        self._update_pixmaps()

    def set_icon_name(self, name):
        self._icon_name = name
        self._update_pixmaps()

    def set_hover_icon_name(self, name):
        self._hover_icon_name = name
        self._update_pixmaps()

    def enterEvent(self, event):
        if self._hover_icon_name:
            self._icon_anim.stop()
            self._icon_anim.setStartValue(self._hover_progress)
            self._icon_anim.setEndValue(1.0)
            self._icon_anim.start()

        self._bg_anim.stop()
        self._bg_anim.setStartValue(self._bg_opacity)
        self._bg_anim.setEndValue(1.0)
        self._bg_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._hover_icon_name:
            self._icon_anim.stop()
            self._icon_anim.setStartValue(self._hover_progress)
            self._icon_anim.setEndValue(0.0)
            self._icon_anim.start()

        self._bg_anim.stop()
        self._bg_anim.setStartValue(self._bg_opacity)
        self._bg_anim.setEndValue(0.0)
        self._bg_anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._bg_opacity > 0:
            bg_color = QColor(self._color)
            bg_color.setAlphaF(self._bg_opacity * 0.12)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            radius = self.width() / 2
            painter.drawRoundedRect(QRectF(self.rect()), radius, radius)

        target_rect = QRectF(
            (self.width() - self._icon_px) / 2,
            (self.height() - self._icon_px) / 2,
            self._icon_px,
            self._icon_px
        )
        center = target_rect.center()

        if self._hover_progress < 1.0:
            painter.save()
            painter.translate(center)
            painter.rotate(self._hover_progress * 90)
            painter.translate(-center)
            painter.setOpacity(1.0 - self._hover_progress)
            painter.drawPixmap(target_rect.toRect(), self._pix_normal)
            painter.restore()

        if self._hover_progress > 0.0:
            painter.save()
            painter.translate(center)
            painter.rotate((self._hover_progress - 1.0) * 90)
            painter.translate(-center)
            painter.setOpacity(self._hover_progress)
            painter.drawPixmap(target_rect.toRect(), self._pix_hover)
            painter.restore()


class SocialButton(QToolButton):
    def __init__(self, image_path, color, tooltip, url, size=24, parent=None):
        super().__init__(parent)
        self._src = QPixmap(image_path)
        self._url = url
        self._size = size
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(size + 16, size + 16)
        self.setIconSize(QSize(size, size))
        self.set_color(color)
        self.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self._url)))
        self.setStyleSheet("QToolButton { border: none; background: transparent; } QToolButton:hover { background: rgba(158, 202, 255, 0.12); border-radius: 20px; }")

    def set_color(self, color):
        pix = self._src.scaled(self._size, self._size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setIcon(QIcon(tint_pixmap(pix, color)))


class PillButton(QPushButton):
    def __init__(self, text, parent=None, hpad=20, vpad=10, font_size=14):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._hpad = hpad
        self._vpad = vpad
        self._font_size = font_size

        font = QFont("Inter")
        font.setPointSize(max(8, font_size - 2))
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

    def apply_theme(self, colors):
        bg = colors["button_bg"]
        fg = colors["button_text"]
        r, g, b = _hex_to_rgb(colors["icon_color"])
        fg_r, fg_g, fg_b = _hex_to_rgb(fg)

        btn_height = max(36, self._font_size + self._vpad * 2 + 8)
        self.setFixedHeight(btn_height)
        radius = btn_height // 2

        self.setStyleSheet(
            f"""
            QPushButton {{
                color: {fg};
                background-color: {bg};
                border: none;
                border-radius: {radius}px;
                padding: 0 {self._hpad}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: rgba({r}, {g}, {b}, 0.14);
            }}
            QPushButton:pressed {{
                background-color: rgba({r}, {g}, {b}, 0.28);
            }}
            QPushButton:disabled {{
                background-color: rgba({r}, {g}, {b}, 0.05);
                color: rgba({fg_r}, {fg_g}, {fg_b}, 0.5);
            }}
            """
        )


class AnimatedTextButton(QPushButton):
    def __init__(self, text, color="#FFFFFF", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFlat(True)
        self.setStyleSheet("background: transparent; border: none;")

        self._color = QColor(color)
        self._hover_opacity = 0.0
        self._is_hovered = False
        self._is_pressed = False

        font = QFont("Inter")
        font.setPixelSize(13)
        font.setWeight(QFont.Weight.DemiBold)
        self.setFont(font)

        self._anim = QPropertyAnimation(self, b"hover_opacity")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_hover_opacity(self):
        return self._hover_opacity

    def set_hover_opacity(self, v):
        self._hover_opacity = v
        self.update()

    hover_opacity = pyqtProperty(float, get_hover_opacity, set_hover_opacity)

    def _animate_to(self, target):
        self._anim.stop()
        self._anim.setStartValue(self._hover_opacity)
        self._anim.setEndValue(target)
        self._anim.start()

    def enterEvent(self, event):
        self._is_hovered = True
        if not self._is_pressed:
            self._animate_to(0.08)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self._is_pressed = False
        self._animate_to(0.0)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self._animate_to(0.16)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            if self._is_hovered:
                self._animate_to(0.08)
            else:
                self._animate_to(0.0)
        super().mouseReleaseEvent(event)

    def sizeHint(self):
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self.text())
        width = text_width + 48
        height = max(fm.height() + 16, 38)
        return QSize(width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._hover_opacity > 0:
            bg_color = QColor(self._color)
            bg_color.setAlphaF(self._hover_opacity)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            radius = self.height() / 2
            painter.drawRoundedRect(QRectF(self.rect()), radius, radius)

        painter.setPen(self._color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class AnimatedRadioButton(QAbstractButton):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        font = QFont("Inter")
        font.setPixelSize(14)
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

        self._radius = 0.0
        self._max_radius = 5.5
        self._radio_color = QColor("#9ecaff")
        self._text_color = QColor("#E6E1E5")

        self._anim = QPropertyAnimation(self, b"radius")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutBack)

        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked):
        self._anim.stop()
        if checked:
            self._anim.setStartValue(0.0)
            self._anim.setEndValue(self._max_radius)
        else:
            self._anim.setStartValue(self._max_radius)
            self._anim.setEndValue(0.0)
        self._anim.start()

    def apply_theme(self, colors):
        self._radio_color = QColor(colors["radio"])
        self._text_color = QColor(colors["fg"])
        self.update()

    def get_radius(self):
        return self._radius

    def set_radius(self, r):
        self._radius = r
        self.update()

    radius = pyqtProperty(float, get_radius, set_radius)

    def sizeHint(self):
        fm = self.fontMetrics()
        w = fm.horizontalAdvance(self.text()) + 34
        h = max(fm.height(), 20)
        return QSize(w, h + 4)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ind_y = (self.height() - 18) / 2
        ind_rect = QRectF(2, ind_y, 18, 18)

        painter.setPen(QPen(self._radio_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(ind_rect)

        if self._radius > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._radio_color)
            cx, cy = ind_rect.center().x(), ind_rect.center().y()
            inner_rect = QRectF(cx - self._radius, cy - self._radius, self._radius * 2, self._radius * 2)
            painter.drawEllipse(inner_rect)

        painter.setPen(self._text_color)
        text_rect = QRectF(28, 0, self.width() - 28, self.height())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())


class UpdateSnackbar(QWidget):
    def __init__(self, window, lang):
        super().__init__(window)
        self._window = window
        self._lang = lang
        self._update_info = None
        self._download_thread = None

        self._bg_color = QColor(45, 40, 50, 245)
        self._border_color = QColor(70, 103, 143)
        self._text_color = QColor(230, 225, 229)
        self._muted_color = QColor(202, 196, 208)
        self._accent_color = QColor(158, 202, 255)

        self.setFixedHeight(120)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 14, 20, 14)
        self._layout.setSpacing(8)

        self._fade_anim = None
        self._pos_anim = None
        self.hide()

    def update_theme(self, colors):
        self._bg_color = QColor(colors["dialog_bg"])
        self._border_color = QColor(colors["border_color"])
        self._text_color = QColor(colors["text_color"])
        self._muted_color = QColor(colors["muted"])
        self._accent_color = QColor(colors["icon_color"])
        self.update()

    def _clear_content(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.layout():
                self._clear_layout(item.layout())
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.layout():
                self._clear_layout(item.layout())
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def _positions(self):
        w = self._window.width()
        sw = w - 40
        x = 20
        y_hidden = self._window.height() + 10
        y_visible = self._window.height() - self.height() - 20
        return x, y_hidden, y_visible, sw

    def _animate_in(self):
        self.setFixedWidth(self._window.width() - 40)
        x, y_hidden, y_visible, sw = self._positions()
        self.move(x, y_visible + 20)
        self.show()
        self.raise_()

        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        self._fade_anim = QPropertyAnimation(effect, b"opacity", self)
        self._fade_anim.setDuration(300)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._pos_anim = QPropertyAnimation(self, b"pos", self)
        self._pos_anim.setDuration(300)
        self._pos_anim.setStartValue(QPoint(x, y_visible + 20))
        self._pos_anim.setEndValue(QPoint(x, y_visible))
        self._pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_anim.start()
        self._pos_anim.start()

    def hide_snackbar(self):
        x, y_hidden, y_visible, sw = self._positions()
        effect = self.graphicsEffect()
        if not effect:
            effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(effect)

        self._fade_anim = QPropertyAnimation(effect, b"opacity", self)
        self._fade_anim.setDuration(250)
        self._fade_anim.setStartValue(effect.opacity())
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        self._pos_anim = QPropertyAnimation(self, b"pos", self)
        self._pos_anim.setDuration(250)
        self._pos_anim.setStartValue(self.pos())
        self._pos_anim.setEndValue(QPoint(x, y_visible + 20))
        self._pos_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        def _finish():
            self.hide()
            self.setGraphicsEffect(None)

        self._fade_anim.finished.connect(_finish)
        self._fade_anim.start()
        self._pos_anim.start()

    def show_available(self, update_info):
        self._update_info = update_info
        self._clear_content()
        self.setFixedHeight(120)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        icon_label = QLabel()
        pix = material_icon("system_update", self._accent_color.name(), 22).pixmap(22, 22)
        icon_label.setPixmap(pix)
        icon_label.setFixedSize(22, 22)
        row1.addWidget(icon_label)

        size_mb = update_info.file_size / (1024 * 1024) if update_info.file_size else 0
        size_str = f" · {size_mb:.1f} MB" if size_mb > 0 else ""
        title = QLabel(f"{self._lang['update_available']}: {update_info.version}{size_str}")
        title.setStyleSheet(
            f"color: {self._text_color.name()}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 600; background: transparent;"
        )
        row1.addWidget(title)
        row1.addStretch()
        self._layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(4)
        row2.addStretch()

        details_btn = AnimatedTextButton(self._lang.get("update_details", "Подробнее"), self._muted_color.name())
        details_btn.clicked.connect(self._on_details_click)
        row2.addWidget(details_btn)

        update_btn = AnimatedTextButton(self._lang["update_now"], self._accent_color.name())
        update_btn.clicked.connect(self._on_update_click)
        row2.addWidget(update_btn)

        later_btn = AnimatedTextButton(self._lang["cancel"], self._muted_color.name())
        later_btn.clicked.connect(self.hide_snackbar)
        row2.addWidget(later_btn)

        self._layout.addLayout(row2)
        self._animate_in()

    def _on_details_click(self):
        self._show_changelog_dialog()

    def _show_changelog_dialog(self):
        from ui_components import UIComponents
        ui = UIComponents(self._window, self._lang)

        colors = ThemeManager.get_theme_colors(self._window.theme_mode)
        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(0, 0, 0, 0)
        body_l.setSpacing(10)

        size_mb = self._update_info.file_size / (1024 * 1024) if self._update_info.file_size else 0
        size_str = f" ({size_mb:.1f} MB)" if size_mb > 0 else ""
        title = QLabel(f"{self._lang.get('version_for_download', 'Доступна версия:')} <b>{self._update_info.version}</b>{size_str}")
        title.setStyleSheet(f"color: {colors['text_color']}; font-size: 14px; background: transparent;")
        title.setWordWrap(True)
        body_l.addWidget(title)

        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {colors['border_color']};")
        body_l.addWidget(line)

        changelog_text = self._update_info.description or ""
        changelog_text = changelog_text.replace("###", "").replace("##", "").replace("#", "").replace("*", "").replace("`", "").replace(">", "")
        changelog_text = changelog_text.replace("-", "•")
        changelog_text = "\n".join(line.strip() for line in changelog_text.split("\n") if line.strip())

        notes = QTextEdit()
        notes.setReadOnly(True)
        notes.setPlainText(changelog_text)
        notes.setFixedHeight(180)

        scrollbar_qss = f"""
            QTextEdit {{
                background: transparent;
                color: {colors['text_color']};
                border: none;
                font-size: 13px;
                padding-right: 15px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['muted']};
                min-height: 30px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['icon_color']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                height: 0px;
            }}
        """
        notes.setStyleSheet(scrollbar_qss)
        body_l.addWidget(notes)

        body.setFixedWidth(400)

        ui.show_themed_dialog(
            "system_update",
            self._lang["update_available"],
            body,
            [
                (self._lang.get("close", "Закрыть"), None, colors["button_color"]),
            ],
            width=460,
        )

    def _on_update_click(self):
        if self._download_thread is not None and self._download_thread.isRunning():
            logging.info("Snackbar: update download already in progress, ignoring click")
            return
        logging.info("Snackbar: user clicked Update")
        self._show_downloading()

    def _show_downloading(self):
        self._clear_content()
        self.setFixedHeight(140)
        self.setFixedWidth(self._window.width() - 40)
        x, y_hidden, y_visible, sw = self._positions()
        self.move(x, y_visible)

        row1 = QHBoxLayout()
        title = QLabel(self._lang["downloading"])
        title.setStyleSheet(
            f"color: {self._text_color.name()}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 600; background: transparent;"
        )
        row1.addWidget(title)
        row1.addStretch()
        self._layout.addLayout(row1)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(6)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: rgba({self._border_color.red()}, {self._border_color.green()}, {self._border_color.blue()}, 60);
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {self._accent_color.name()};
                border-radius: 3px;
            }}
        """)
        self._layout.addWidget(progress_bar)

        status = QLabel("0.0 MB / 0.0 MB")
        status.setStyleSheet(
            f"color: {self._muted_color.name()}; font-family: 'Inter'; "
            f"font-size: 11px; background: transparent;"
        )
        self._layout.addWidget(status)

        from updater import UpdateDownloader, download_update, DownloadCancelled

        frozen = getattr(sys, "frozen", False)
        if frozen:
            target_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            target_dir = os.getcwd()

        version = self._update_info.version or "unknown"
        new_filename = f"DisplaceBox_{version}.exe"

        if frozen:
            current_exe = os.path.abspath(sys.executable)
            new_abs = os.path.abspath(os.path.join(target_dir, new_filename))
            try:
                for entry in os.listdir(target_dir):
                    entry_abs = os.path.abspath(os.path.join(target_dir, entry))
                    if entry_abs in (current_exe, new_abs):
                        continue
                    if entry == "update.exe" or (entry.startswith("DisplaceBox_") and entry.endswith(".exe")):
                        try:
                            os.remove(entry_abs)
                            logging.info(f"Cleaned up old update file: {entry_abs}")
                        except Exception as e:
                            logging.warning(f"Failed to remove {entry_abs}: {e}")
            except Exception as e:
                logging.warning(f"Failed to scan target dir for cleanup: {e}")

        def on_progress(value, current, total):
            progress_bar.setValue(int(value))
            status.setText(f"{current:.1f} MB / {total:.1f} MB")

        def on_done(success, result):
            if success and result:
                self._show_completed(result)
            elif result:
                self._show_error(str(result))

        class DownloadWorker(QThread):
            done = pyqtSignal(bool, object)
            progress = pyqtSignal(float, float, float)

            def __init__(self, url, downloader, checksum, target_dir, target_filename):
                super().__init__()
                self.url = url
                self.downloader = downloader
                self.checksum = checksum
                self.target_dir = target_dir
                self.target_filename = target_filename

            def run(self):
                try:
                    save_path = download_update(
                        self.url, self.downloader,
                        lambda v, c, t, _: self.progress.emit(v, c, t),
                        self.checksum,
                        target_dir=self.target_dir,
                        target_filename=self.target_filename,
                    )
                    self.done.emit(True, save_path)
                except DownloadCancelled:
                    self.done.emit(False, None)
                except Exception as e:
                    self.done.emit(False, e)

        downloader = UpdateDownloader()
        worker = DownloadWorker(
            self._update_info.download_url,
            downloader,
            self._update_info.checksum,
            target_dir,
            new_filename,
        )
        worker.progress.connect(on_progress)
        worker.done.connect(on_done)
        worker.start()
        self._download_thread = worker

        def _clear_thread_ref():
            if self._download_thread is worker:
                self._download_thread = None
        worker.finished.connect(_clear_thread_ref)

        if not self.isVisible():
            self._animate_in()

    def _show_completed(self, save_path):
        self._clear_content()
        self.setFixedHeight(110)
        self.setFixedWidth(self._window.width() - 40)
        x, y_hidden, y_visible, sw = self._positions()
        self.move(x, y_visible)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        icon_label = QLabel()
        pix = material_icon("check_circle", "#4CAF50", 22).pixmap(22, 22)
        icon_label.setPixmap(pix)
        icon_label.setFixedSize(22, 22)
        row1.addWidget(icon_label)

        title = QLabel(self._lang["update_downloaded"])
        title.setStyleSheet(
            f"color: {self._text_color.name()}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 600; background: transparent;"
        )
        row1.addWidget(title)
        row1.addStretch()
        self._layout.addLayout(row1)

        restart_lbl = QLabel(self._lang["restart"])
        restart_lbl.setStyleSheet(
            f"color: {self._muted_color.name()}; font-family: 'Inter'; "
            f"font-size: 11px; background: transparent;"
        )
        restart_lbl.setWordWrap(True)
        self._layout.addWidget(restart_lbl)

        QTimer.singleShot(2000, lambda: self._restart(save_path))

    def _restart(self, save_path):
        frozen = getattr(sys, "frozen", False)
        try:
            if frozen:
                old_exe = os.path.abspath(sys.executable)
                subprocess.Popen([save_path, "--cleanup-old", old_exe, "--updated"])
                logging.info(f"Restarting: {save_path}, will delete old: {old_exe}")
            else:
                subprocess.Popen([save_path, "--updated"])
                logging.info(f"Restarting from source: {save_path}")
        except Exception as e:
            logging.error(f"Restart failed: {e}")
            error_msg = self._lang.get(
                "restart_failed",
                "Failed to restart the application. The update file may have been moved or blocked."
            )
            error_title = self._lang.get("restart_error", "Restart Error")
            self._show_error(error_msg, title=error_title)
            return

        try:
            self._window.close()
        except Exception as e:
            logging.error(f"Window close failed after restart: {e}")

    def _show_error(self, msg, title=None):
        self._clear_content()
        self.setFixedHeight(150)
        self.setFixedWidth(self._window.width() - 40)
        x, y_hidden, y_visible, sw = self._positions()
        self.move(x, y_visible)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        icon_label = QLabel()
        pix = material_icon("error", "#FF5252", 22).pixmap(22, 22)
        icon_label.setPixmap(pix)
        icon_label.setFixedSize(22, 22)
        row1.addWidget(icon_label)

        title_text = title or self._lang.get("update_error", "Update Error")
        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet(
            f"color: {self._text_color.name()}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 600; background: transparent;"
        )
        row1.addWidget(title_lbl)
        row1.addStretch()
        self._layout.addLayout(row1)

        msg_lbl = QLabel(msg)
        msg_lbl.setStyleSheet(
            f"color: {self._muted_color.name()}; font-family: 'Inter'; "
            f"font-size: 11px; background: transparent;"
        )
        msg_lbl.setWordWrap(True)
        self._layout.addWidget(msg_lbl)

        row2 = QHBoxLayout()
        row2.addStretch()

        github_btn = AnimatedTextButton(
            self._lang.get("open_github", "GitHub"),
            self._muted_color.name()
        )
        github_btn.clicked.connect(lambda: self._window.launch_url(
            "https://github.com/stakanyash/displacebin_gui_converter/releases"
        ))
        row2.addWidget(github_btn)

        close_btn = AnimatedTextButton(
            self._lang.get("close", "Закрыть"),
            self._accent_color.name()
        )
        close_btn.clicked.connect(self.hide_snackbar)
        row2.addWidget(close_btn)

        self._layout.addLayout(row2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self._border_color, 1.5))
        painter.setBrush(self._bg_color)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(0.75, 0.75, -0.75, -0.75), 16, 16)

class SpinnerWidget(QWidget):
    def __init__(self, color="#9ecaff", size=22, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._angle = 0
        self._size = size
        self.setFixedSize(size + 6, size + 6)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def _tick(self):
        self._angle = (self._angle + 12) % 360
        self.update()

    def start(self):
        if not self._timer.isActive():
            self._timer.start(30)

    def stop(self):
        self._timer.stop()

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(3, 3, self._size, self._size)

        track = QColor(self._color)
        track.setAlpha(60)
        track_pen = QPen(track, 3)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)

        arc_pen = QPen(self._color, 3)
        arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(arc_pen)
        painter.drawArc(rect, int(-self._angle * 16), int(-270 * 16))


class LoadingSnackbar(QWidget):
    def __init__(self, window):
        super().__init__(window)
        self._window = window

        self._bg_color = QColor(45, 40, 50, 245)
        self._border_color = QColor(70, 103, 143)
        self._text_color = QColor(230, 225, 229)
        self._accent_color = QColor(158, 202, 255)

        self.setFixedHeight(64)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(24, 0, 24, 0)
        self._layout.setSpacing(16)

        self._spinner = SpinnerWidget(self._accent_color.name(), size=20)
        self._layout.addWidget(self._spinner)

        self._msg = QLabel("")
        self._msg.setStyleSheet(
            f"color: {self._text_color.name()}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 600; background: transparent;"
        )
        self._layout.addWidget(self._msg)
        self._layout.addStretch()

        self._fade_anim = None
        self._pos_anim = None
        self.hide()

    def update_theme(self, colors):
        self._bg_color = QColor(colors["dialog_bg"])
        self._border_color = QColor(colors["border_color"])
        self._text_color = QColor(colors["text_color"])
        self._accent_color = QColor(colors["icon_color"])
        self._spinner.set_color(self._accent_color.name())
        self._msg.setStyleSheet(
            f"color: {self._text_color.name()}; font-family: 'Inter'; "
            f"font-size: 13px; font-weight: 600; background: transparent;"
        )
        self.update()

    def _positions(self):
        x = 20
        y_visible = self._window.height() - self.height() - 20
        return x, y_visible

    def show_message(self, message):
        self._msg.setText(message)
        self.setFixedWidth(self._window.width() - 40)
        x, y_visible = self._positions()
        self.move(x, y_visible + 20)
        self.show()
        self.raise_()

        self._spinner.start()

        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        self._fade_anim = QPropertyAnimation(effect, b"opacity", self)
        self._fade_anim.setDuration(250)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._pos_anim = QPropertyAnimation(self, b"pos", self)
        self._pos_anim.setDuration(250)
        self._pos_anim.setStartValue(QPoint(x, y_visible + 20))
        self._pos_anim.setEndValue(QPoint(x, y_visible))
        self._pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_anim.start()
        self._pos_anim.start()

    def hide_snackbar(self, on_finished=None):
        if not self.isVisible():
            if on_finished:
                on_finished()
            return

        x, y_visible = self._positions()
        effect = self.graphicsEffect()
        if not effect:
            effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(effect)

        self._fade_anim = QPropertyAnimation(effect, b"opacity", self)
        self._fade_anim.setDuration(200)
        self._fade_anim.setStartValue(effect.opacity())
        self._fade_anim.setEndValue(0.0)

        self._pos_anim = QPropertyAnimation(self, b"pos", self)
        self._pos_anim.setDuration(200)
        self._pos_anim.setStartValue(self.pos())
        self._pos_anim.setEndValue(QPoint(x, y_visible + 20))

        def _finish():
            self._spinner.stop()
            self.hide()
            self.setGraphicsEffect(None)
            if on_finished:
                on_finished()

        self._fade_anim.finished.connect(_finish)
        self._fade_anim.start()
        self._pos_anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(self._border_color, 1.5))
        painter.setBrush(self._bg_color)
        painter.drawRoundedRect(
            QRectF(self.rect()).adjusted(0.75, 0.75, -0.75, -0.75), 16, 16
        )


class ConversionThread(QThread):
    finished = pyqtSignal(object)
    failed = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._func(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.failed.emit(e)


class OutlinedLineEdit(QWidget):
    def __init__(self, label, width=400, read_only=True, parent=None):
        super().__init__(parent)
        self._label = label
        self._border = "#46678F"
        self._fg = "#E6E1E5"
        self._bg = "#1C1B1F"
        self.setFixedWidth(width)
        self.setFixedHeight(52)
        self.edit = QLineEdit(self)
        self.edit.setReadOnly(read_only)
        self.edit.setFrame(False)
        self.edit.setGeometry(14, 16, width - 28, 28)

        edit_font = QFont("Inter")
        edit_font.setPixelSize(13)
        self.edit.setFont(edit_font)
        self.edit.setStyleSheet(f"background: transparent; border: none; color: {self._fg};")

    def set_label(self, text):
        self._label = text
        self.update()

    def set_value(self, text):
        self.edit.setText(text or "")

    def value(self):
        return self.edit.text()

    def apply_theme(self, colors):
        self._border = colors["border_color"]
        self._fg = colors["fg"]
        self._bg = colors["field_bg"]
        self.edit.setStyleSheet(f"background: transparent; border: none; color: {self._fg};")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1.5, 8, self.width() - 3, self.height() - 10)
        painter.setBrush(QColor(self._bg))
        painter.setPen(QPen(QColor(self._border), 1.4))
        painter.drawRoundedRect(rect, 4, 4)

        if self._label:
            font = QFont("Inter")
            font.setPixelSize(11)
            painter.setFont(font)

            metrics = painter.fontMetrics()
            text_w = metrics.horizontalAdvance(self._label) + 8
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self._bg))
            painter.drawRect(QRectF(12, 0, text_w, 16))
            painter.setPen(QColor(self._border))
            painter.drawText(QRect(16, 0, text_w, 16), Qt.AlignmentFlag.AlignVCenter, self._label)

        painter.end()


class OutlinedComboBox(QWidget):
    def __init__(self, label, options, width=350, parent=None):
        super().__init__(parent)
        self._label = label
        self._border = "#46678F"
        self._fg = "#E6E1E5"
        self._bg = "#1C1B1F"
        self._drop = "#2B2930"
        self.setFixedWidth(width)
        self.setFixedHeight(48)
        self.combo = QComboBox(self)
        self.combo.setGeometry(10, 14, width - 20, 28)
        self.combo.setFrame(False)
        self.combo.setCursor(Qt.CursorShape.PointingHandCursor)

        combo_font = QFont("Inter")
        combo_font.setPixelSize(12)
        self.combo.setFont(combo_font)

        for key, text in options:
            self.combo.addItem(text, key)
        self.combo.setCurrentIndex(-1)

    def set_label(self, text):
        self._label = text
        self.update()

    def current_key(self):
        if self.combo.currentIndex() < 0:
            return None
        return self.combo.currentData()

    def set_current_key(self, key):
        if not key:
            return
        index = self.combo.findData(key)
        if index >= 0:
            self.combo.setCurrentIndex(index)

    def apply_theme(self, colors):
        self._border = colors["border_color"]
        self._fg = colors["fg"]
        self._bg = colors["field_bg"]
        self._drop = colors["dropdown_bg"]

        r, g, b = _hex_to_rgb(colors["icon_color"])
        muted_color = colors["muted"]

        self.combo.view().window().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.combo.view().window().setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.combo.view().window().setWindowFlag(Qt.WindowType.NoDropShadowWindowHint)

        self.combo.setStyleSheet(
            f"""
            QComboBox {{
                background: transparent;
                color: {self._fg};
                border: none;
                padding-left: 4px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background: {self._drop};
                color: {self._fg};
                border: 1px solid {self._border};
                border-radius: 8px;
                padding: 6px;
                outline: none;
                selection-background-color: transparent;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 34px;
                padding-left: 12px;
                padding-right: 12px;
                border-radius: 6px;
                color: {self._fg};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: rgba({r}, {g}, {b}, 0.12);
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: rgba({r}, {g}, {b}, 0.20);
                color: {self._fg};
            }}
            QComboBox QAbstractItemView QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 2px;
            }}
            QComboBox QAbstractItemView QScrollBar::handle:vertical {{
                background: {muted_color};
                min-height: 20px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {{
                background: {colors['icon_color']};
            }}
            QComboBox QAbstractItemView QScrollBar::add-line:vertical,
            QComboBox QAbstractItemView QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QComboBox QAbstractItemView QScrollBar::add-page:vertical,
            QComboBox QAbstractItemView QScrollBar::sub-page:vertical {{
                background: none;
            }}
            """
        )
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(1.5, 8, self.width() - 3, self.height() - 10)
        painter.setBrush(QColor(self._bg))
        painter.setPen(QPen(QColor(self._border), 1.4))
        painter.drawRoundedRect(rect, 4, 4)

        if self._label:
            font = QFont("Inter")
            font.setPixelSize(11)
            painter.setFont(font)

            metrics = painter.fontMetrics()
            text_w = min(metrics.horizontalAdvance(self._label) + 8, self.width() - 28)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self._bg))
            painter.drawRect(QRectF(12, 0, text_w, 16))
            painter.setPen(QColor(self._border))
            painter.drawText(QRect(16, 0, int(text_w), 16), Qt.AlignmentFlag.AlignVCenter, self._label)

        painter.end()


class TitleBar(QWidget):
    def __init__(self, window, lang, scale_factor=1.0):
        super().__init__(window)
        self._window = window
        self._drag_origin = None
        self._win_origin = None
        self.setFixedHeight(int(27 * scale_factor))
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(8)

        self.logo = QLabel()
        self.logo.setFixedSize(16, 16)
        self.logo.setScaledContents(True)

        self.title_label = QLabel(f"{window.window_title_text} {VERSION}")
        font = QFont("Inter")
        font.setPointSize(9)
        font.setWeight(QFont.Weight.DemiBold)
        self.title_label.setFont(font)

        layout.addWidget(self.logo)
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.minimize_btn = IconButton("remove", "#CAC4D0", lang["min"], size=14, btn_size=28)
        self.close_btn = IconButton("close", "#CAC4D0", lang["exit"], size=14, btn_size=28)
        self.minimize_btn.clicked.connect(window.showMinimized)
        self.close_btn.clicked.connect(window.close)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.close_btn)

    def apply_theme(self, colors):
        self.logo.setPixmap(QPixmap(colors["topbar_logo"]).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.title_label.setStyleSheet(f"color: {colors['fg']};")
        self.minimize_btn.set_color(colors["titlebar_btn"])
        self.close_btn.set_color(colors["titlebar_btn"])
        self.setStyleSheet(f"background: {colors['surface']};")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint()
            self._win_origin = self._window.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_origin
            self._window.move(self._win_origin + delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_origin = None
        super().mouseReleaseEvent(event)


class OverlayLayer(QWidget):
    dismissed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self._modal = False
        self.hide()
        self._card_wrapper = QWidget(self)
        self._card = None
        self._scrim = QColor(0, 0, 0, 80)
        self._scrim_opacity = 0.0
        self._closing = False

        self._scrim_anim = QPropertyAnimation(self, b"scrim_opacity", self)
        self._scrim_anim.setDuration(220)
        self._scrim_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._slide_anim = QPropertyAnimation(self)
        self._slide_anim.setDuration(260)
        self._slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_scrim_opacity(self):
        return self._scrim_opacity

    def set_scrim_opacity(self, v):
        self._scrim_opacity = v
        self.update()

    scrim_opacity = pyqtProperty(float, get_scrim_opacity, set_scrim_opacity)

    def set_scrim(self, color: QColor):
        self._scrim = color
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._card_wrapper.setGeometry(self.rect())
        if self._card is not None and not self._closing:
            cw = self._card_wrapper.width()
            ch = self._card_wrapper.height()
            x = max(0, (cw - self._card.width()) // 2)
            y = max(20, (ch - self._card.height()) // 2)
            self._card.move(x, y)

    def clear(self):
        self._scrim_anim.stop()
        self._slide_anim.stop()
        try:
            self._slide_anim.finished.disconnect()
        except TypeError:
            pass
        if self._card is not None:
            self._card.setParent(None)
            self._card.deleteLater()
            self._card = None

    def show_card(self, card: QWidget, modal=False):
        self.clear()
        self._closing = False
        self._modal = modal
        self._card = card
        card.setParent(self._card_wrapper)

        self.show()
        self.raise_()
        self.setGeometry(self.parentWidget().rect())
        self._card_wrapper.setGeometry(self.rect())

        card.adjustSize()
        cw = self._card_wrapper.width()
        ch = self._card_wrapper.height()
        x = max(0, (cw - card.width()) // 2)
        y_end = max(20, (ch - card.height()) // 2)

        start_pos = QPoint(x, y_end + 18)
        card.move(start_pos)
        card.setVisible(True)
        card.raise_()

        self._scrim_opacity = 0.0
        self.update()
        self._scrim_anim.stop()
        self._scrim_anim.setStartValue(0.0)
        self._scrim_anim.setEndValue(1.0)
        self._scrim_anim.start()

        self._slide_anim.stop()
        self._slide_anim.setTargetObject(card)
        self._slide_anim.setPropertyName(b"pos")
        self._slide_anim.setStartValue(start_pos)
        self._slide_anim.setEndValue(QPoint(x, y_end))
        self._slide_anim.setDuration(260)
        self._slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._slide_anim.start()

    def close_overlay(self):
        if self._card is None or self._closing:
            if self._card is None:
                self.hide()
                self.dismissed.emit()
            return

        self._closing = True

        end_pos = QPoint(self._card.x(), self._card.y() + 40)

        self._slide_anim.stop()
        self._slide_anim.setTargetObject(self._card)
        self._slide_anim.setPropertyName(b"pos")
        self._slide_anim.setStartValue(self._card.pos())
        self._slide_anim.setEndValue(end_pos)

        self._slide_anim.setDuration(200)
        self._slide_anim.setEasingCurve(QEasingCurve.Type.InCubic)

        self._scrim_anim.stop()
        self._scrim_anim.setStartValue(self._scrim_opacity)
        self._scrim_anim.setEndValue(0.0)

        def _finish():
            try:
                self._slide_anim.finished.disconnect(_finish)
            except TypeError:
                pass
            if not self._closing:
                return
            self._closing = False
            self.hide()
            self.clear()
            self.dismissed.emit()

        self._slide_anim.finished.connect(_finish)
        self._slide_anim.start()
        self._scrim_anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        scrim = QColor(self._scrim)
        scrim.setAlpha(int(self._scrim.alpha() * self._scrim_opacity))
        painter.fillRect(self.rect(), scrim)
        painter.end()

    def mousePressEvent(self, event):
        if self._modal or self._card is None or self._closing:
            return
        card_rect = self._card.geometry().translated(
            self._card.parentWidget().mapTo(self, QPoint(0, 0))
        )
        if not card_rect.contains(event.pos()):
            self.close_overlay()


def _wrap_text(text, color, size=13, bold=False, selectable=False):
    label = QLabel(text)
    label.setWordWrap(True)
    label.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByMouse if selectable else Qt.TextInteractionFlag.NoTextInteraction
    )

    font = QFont("Inter")
    font.setPixelSize(size)
    if bold:
        font.setWeight(QFont.Weight.Bold)
    label.setFont(font)

    label.setStyleSheet(f"color: {color}; background: transparent;")
    return label


def dialog_title_row(icon_name, title, color="#FFFFFF"):
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(10)
    icon = QLabel()
    pix = material_icon(icon_name, color, 30).pixmap(30, 30)
    icon.setPixmap(pix)

    text = QLabel(title)
    title_font = QFont("Inter")
    title_font.setPixelSize(16)
    title_font.setWeight(QFont.Weight.Bold)
    text.setFont(title_font)
    text.setStyleSheet(f"color: {color}; background: transparent;")

    layout.addWidget(icon)
    layout.addWidget(text)
    layout.addStretch()
    return row


def make_card(bgcolor, width=460):
    card = QFrame()
    card.setObjectName("dialogCard")
    card.setFixedWidth(width)
    shadow = QGraphicsDropShadowEffect(card)
    shadow.setBlurRadius(24)
    shadow.setOffset(0, 6)
    shadow.setColor(QColor(0, 0, 0, 120))
    card.setGraphicsEffect(shadow)
    card.setStyleSheet(
        f"""
        QFrame#dialogCard {{
            background-color: {bgcolor};
            border-radius: 28px;
        }}
        """
    )
    return card


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.theme_mode = "dark"
        self.window_title_text = "DisplaceBox"
        self.setWindowTitle("DisplaceBox")
        self.setWindowIcon(QIcon(asset_path("icon.ico")))
        self.setFixedSize(580, 680)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)
        self.ui_root = QWidget()
        self.ui_layout = QVBoxLayout(self.ui_root)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)
        self.ui_layout.setSpacing(0)
        self._root.addWidget(self.ui_root)

        self.overlay = OverlayLayer(self)
        self._extra_overlays = []
        self._update_snackbar = None
        self._loading_snackbar = None
        self._loading_start_time = 0.0

        self.version_label = QLabel(f"{VERSION} {BUILD}", self)
        self.version_label.setStyleSheet("color: #9E9E9E; font-size: 10px; background: transparent; font-family: 'Inter';")
        self.version_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.version_clicked = None
        self.version_label.mousePressEvent = self._on_version_clicked

        self._transition_anim = None
        self._transition_anim2 = None
        self._dynamic_widget = None
        self._update_mask()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(self.rect())
        for ov in self._extra_overlays:
            ov.setGeometry(self.rect())
        if self._update_snackbar and self._update_snackbar.isVisible():
            x, y_hidden, y_visible, sw = self._update_snackbar._positions()
            self._update_snackbar.move(x, y_visible)
        if self._loading_snackbar and self._loading_snackbar.isVisible():
            x, y_visible = self._loading_snackbar._positions()
            self._loading_snackbar.move(x, y_visible)
        self.place_version()
        self._update_mask()

    def place_version(self):
        self.version_label.adjustSize()
        self.version_label.move(
            self.width() - self.version_label.width() - 14,
            self.height() - self.version_label.height() - 12,
        )
        self.version_label.raise_()

    def _update_mask(self):
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 12, 12)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def paintEvent(self, event):
        colors = ThemeManager.get_theme_colors(self.theme_mode)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(colors["bg"]))
        painter.drawRoundedRect(QRectF(self.rect()), 12, 12)
        painter.end()

    def clear_ui(self):
        self._dynamic_widget = None
        if self._update_snackbar:
            self._update_snackbar.hide_snackbar()
        if self._loading_snackbar:
            self._loading_snackbar.hide_snackbar()

        while self.ui_layout.count():
            item = self.ui_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        for ov in self._extra_overlays:
            ov.close_overlay()
        self._extra_overlays.clear()
        self.overlay.close_overlay()

    def add_ui(self, widget, stretch=0):
        self.ui_layout.addWidget(widget, stretch)
        if stretch == 1:
            self._dynamic_widget = widget

    def launch_url(self, url):
        QDesktopServices.openUrl(QUrl(url))

    def show_overlay(self, card, modal=False):
        colors = ThemeManager.get_theme_colors(self.theme_mode)
        scrim_color = QColor(0, 0, 0, 90 if self.theme_mode == "light" else 80)

        if self.overlay._card is not None:
            new_overlay = OverlayLayer(self)
            new_overlay.set_scrim(scrim_color)
            new_overlay.show_card(card, modal=modal)
            self.version_label.raise_()

            self._extra_overlays.append(new_overlay)

            new_overlay.dismissed.connect(
                lambda: self._extra_overlays.remove(new_overlay) if new_overlay in self._extra_overlays else None
            )
            return

        self.overlay.set_scrim(scrim_color)
        self.overlay.show_card(card, modal=modal)
        self.version_label.raise_()

    def close_overlay(self):
        if self._extra_overlays:
            top_overlay = self._extra_overlays.pop()
            top_overlay.close_overlay()
        else:
            self.overlay.close_overlay()

    def _on_version_clicked(self, event):
        if self.version_clicked:
            self.version_clicked(event)

    def fade_transition(self, callback, duration=180):
        pixmap = self.grab()

        overlay = QLabel(self)
        overlay.setPixmap(pixmap)
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.setStyleSheet("background: transparent;")
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        overlay.show()
        overlay.raise_()

        effect = QGraphicsOpacityEffect(overlay)
        overlay.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        anim.finished.connect(overlay.deleteLater)
        anim.start()
        self._transition_anim = anim

        QTimer.singleShot(0, callback)

    def smooth_transition(self, callback, duration=300):
        old_widget = getattr(self, '_dynamic_widget', None)
        old_pixmap = None
        old_geom = None

        if old_widget:
            old_pixmap = old_widget.grab()
            old_geom = old_widget.geometry()

        callback()

        new_widget = getattr(self, '_dynamic_widget', None)

        if old_pixmap and new_widget and old_geom:
            self.update()
            new_widget.update()

            overlay = QLabel(self)
            overlay.setPixmap(old_pixmap)
            overlay.setGeometry(old_geom)
            overlay.setStyleSheet("background: transparent;")
            overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

            effect_old = QGraphicsOpacityEffect(overlay)
            overlay.setGraphicsEffect(effect_old)
            overlay.show()
            overlay.raise_()

            effect_new = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(effect_new)

            anim_old_opacity = QPropertyAnimation(effect_old, b"opacity", self)
            anim_old_opacity.setDuration(duration)
            anim_old_opacity.setStartValue(1.0)
            anim_old_opacity.setEndValue(0.0)
            anim_old_opacity.setEasingCurve(QEasingCurve.Type.InCubic)

            anim_old_pos = QPropertyAnimation(overlay, b"pos", self)
            anim_old_pos.setDuration(duration)
            anim_old_pos.setStartValue(old_geom.topLeft())
            anim_old_pos.setEndValue(old_geom.topLeft() + QPoint(0, 20))
            anim_old_pos.setEasingCurve(QEasingCurve.Type.InCubic)

            anim_new_opacity = QPropertyAnimation(effect_new, b"opacity", self)
            anim_new_opacity.setDuration(duration)
            anim_new_opacity.setStartValue(0.0)
            anim_new_opacity.setEndValue(1.0)
            anim_new_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

            def _finish():
                overlay.deleteLater()
                new_widget.setGraphicsEffect(None)

            anim_old_opacity.finished.connect(_finish)

            anim_old_opacity.start()
            anim_old_pos.start()
            anim_new_opacity.start()

            self._transition_anim = anim_old_opacity
            self._transition_anim2 = anim_new_opacity
        else:
            self.fade_transition(callback, duration)

    def show_update_snackbar(self, update_info, lang):
        if self._update_snackbar is None:
            self._update_snackbar = UpdateSnackbar(self, lang)
        else:
            self._update_snackbar._lang = lang
        colors = ThemeManager.get_theme_colors(self.theme_mode)
        self._update_snackbar.update_theme(colors)
        self._update_snackbar.show_available(update_info)

    def show_loading_snackbar(self, message):
        if self._update_snackbar and self._update_snackbar.isVisible():
            self._update_snackbar.hide_snackbar()
        if self._loading_snackbar is None:
            self._loading_snackbar = LoadingSnackbar(self)
        colors = ThemeManager.get_theme_colors(self.theme_mode)
        self._loading_snackbar.update_theme(colors)
        self._loading_snackbar.show_message(message)
        self._loading_start_time = time.time()

    def hide_loading_snackbar(self, min_duration_ms=1200, on_finished=None):
        if not self._loading_snackbar:
            if on_finished:
                on_finished()
            return

        elapsed_ms = int((time.time() - self._loading_start_time) * 1000)
        remaining = max(0, min_duration_ms - elapsed_ms)

        def _do_hide():
            self._loading_snackbar.hide_snackbar(on_finished=on_finished)

        if remaining > 0:
            QTimer.singleShot(remaining, _do_hide)
        else:
            _do_hide()


class UIComponents:
    def __init__(self, window: AppWindow, lang: dict, scale_factor: float = 1.0):
        self.window = window
        self.lang = lang
        self.scale_factor = scale_factor
        self.icon_size = int(24 * scale_factor)

    def create_top_bar(self):
        top_bar = TitleBar(self.window, self.lang, self.scale_factor)
        return top_bar, top_bar.minimize_btn, top_bar.close_btn, top_bar.logo

    def create_title_container(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, int(10 * self.scale_factor), 0, int(5 * self.scale_factor))
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_image = QLabel()
        title_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(ThemeManager.get_theme_colors(self.window.theme_mode)["logo_src"])
        title_image.setPixmap(pix.scaledToHeight(int(100 * self.scale_factor), Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(title_image)
        container.setFixedHeight(int(120 * self.scale_factor))
        return container, title_image

    def show_error_dialog(self, title: str, message: str):
        self.show_colored_dialog("#B71C1C", "warning", title, message, [("OK", None)])

    def show_colored_dialog(self, bgcolor, icon_name, title, message, actions, extra_widgets=None, on_dismiss=None, width=460):
        card = make_card(bgcolor, width=width)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(12)
        layout.addWidget(dialog_title_row(icon_name, title, "#FFFFFF"))
        if extra_widgets:
            for w in extra_widgets:
                layout.addWidget(w)
        elif message:
            layout.addWidget(_wrap_text(message, "#FFFFFF", 13))
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        for label, callback in actions:
            btn = AnimatedTextButton(label, "#FFFFFF")
            def _clicked(checked=False, cb=callback):
                if cb:
                    cb()
                else:
                    self.window.close_overlay()
            btn.clicked.connect(_clicked)
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)
        if on_dismiss:
            def _after():
                self.window.overlay.dismissed.disconnect(_after)
                on_dismiss()
            self.window.overlay.dismissed.connect(_after)
        self.window.show_overlay(card)
        return card

    def show_themed_dialog(self, icon_name, title, content_widget, actions, width=460, modal=False):
        colors = ThemeManager.get_theme_colors(self.window.theme_mode)
        card = make_card(colors["dialog_bg"], width=width)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(12)
        layout.addWidget(dialog_title_row(icon_name, title, colors["text_color"]))
        layout.addWidget(content_widget)
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        for label, callback, color in actions:
            btn_color = color or colors["button_color"]
            btn = AnimatedTextButton(label, btn_color)
            def _clicked(checked=False, cb=callback):
                if cb:
                    cb()
                else:
                    self.window.close_overlay()
            btn.clicked.connect(_clicked)
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)
        self.window.show_overlay(card, modal=modal)
        return card

    def create_toolbar_buttons(self, on_help, on_language, on_theme, on_mode_switch, mode_tooltip_key="modeswitch2"):
        icon_color = ThemeManager.get_theme_colors(self.window.theme_mode)["icon_color"]
        size = self.icon_size

        help_btn = IconButton("help_outline", icon_color, self.lang["help"], size, 40, "help")
        help_btn.clicked.connect(lambda: on_help(None))

        language_btn = IconButton("public", icon_color, self.lang["cnglang"], size, 40, "language")
        language_btn.clicked.connect(lambda: on_language(None))

        theme_btn = IconButton("brightness_3", icon_color, self.lang["toggletheme"], size, 40, "brightness_medium")
        theme_btn.clicked.connect(lambda: on_theme(None))

        mode_btn = IconButton("swap_horiz", icon_color, self.lang.get(mode_tooltip_key, "Switch mode"), size, 40, "swap_vert")
        mode_btn.clicked.connect(lambda: on_mode_switch(None))

        return {"help": help_btn, "language": language_btn, "theme": theme_btn, "mode": mode_btn}

    def create_social_buttons(self):
        icon_color = ThemeManager.get_theme_colors(self.window.theme_mode)["icon_color"]
        size = self.icon_size
        return {
            "github": SocialButton(asset_path("git.png"), icon_color, self.lang["github"], "https://github.com/stakanyash/displacebin_gui_converter", size),
            "discord": SocialButton(asset_path("dis.png"), icon_color, self.lang["discord"], "https://discord.com/invite/Cd5GanuYud", size),
            "telegram": SocialButton(asset_path("tg.png"), icon_color, self.lang["telegram"], "https://t.me/stakanyasher", size),
            "youtube": SocialButton(asset_path("yt.png"), icon_color, self.lang["youtube"], "https://www.youtube.com/@stakanyash", size),
        }

    def create_toolbar_container(self, toolbar_buttons, social_buttons):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, int(30 * self.scale_factor))
        layout.setSpacing(int(10 * self.scale_factor))
        row1 = QHBoxLayout()
        row1.setSpacing(int(10 * self.scale_factor))
        row1.addStretch()
        for key in ("help", "language", "theme", "mode"):
            row1.addWidget(toolbar_buttons[key])
        row1.addStretch()
        row2 = QHBoxLayout()
        row2.setSpacing(int(10 * self.scale_factor))
        row2.addStretch()
        for key in ("github", "discord", "telegram", "youtube"):
            row2.addWidget(social_buttons[key])
        row2.addStretch()
        layout.addLayout(row1)
        layout.addLayout(row2)
        return container

    def create_version_container(self, on_click):
        self.window.version_clicked = on_click
        self.window.version_label.setText(f"{VERSION} {BUILD}")
        self.window.place_version()
        return self.window.version_label

    def show_version_info(self, e=None):
        colors = ThemeManager.get_theme_colors(self.window.theme_mode)
        text_color = colors["text_color"]
        content = QLabel()
        content.setTextFormat(Qt.TextFormat.RichText)
        content.setOpenExternalLinks(True)
        content.setWordWrap(True)
        content.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        link = colors["icon_color"] if self.window.theme_mode == "dark" else "#1976D2"
        content.setStyleSheet(f"color: {text_color}; background: transparent; font-family: 'Inter'; font-size: 13px;")
        content.setText(
            f'powered by <a href="https://www.python.org/" style="color:{link}">Python</a>, '
            f'<a href="https://www.qt.io/" style="color:{link}">PyQt</a>, '
            f'<a href="https://pillow.readthedocs.io/en/stable/" style="color:{link}">Pillow</a>, '
            f'<a href="https://docs.python.org/3/library/locale.html" style="color:{link}">locale</a>, '
            f'<a href="https://docs.python.org/3/library/logging.html" style="color:{link}">logging</a>, '
            f'<a href="https://docs.python.org/3/library/datetime.html" style="color:{link}">datetime</a>, '
            f'<a href="https://docs.python.org/3/library/traceback.html" style="color:{link}">traceback</a>, '
            f'<a href="https://docs.python.org/3/library/pathlib.html" style="color:{link}">pathlib</a>, '
            f'<a href="https://docs.python.org/3/library/math.html" style="color:{link}">math</a>, '
            f'<a href="https://docs.python.org/3/library/struct.html" style="color:{link}">struct</a>, '
            f'<a href="https://docs.python.org/3/library/sys.html" style="color:{link}">sys</a>'
            f'<br/><br/>Authors: <a href="https://github.com/stakanyash" style="color:{link}">stakan</a> (GUI), '
            f'<a href="https://github.com/ThePlain" style="color:{link}">ThePlain</a> (conversion script)'
        )
        content.setFixedSize(300, 120)
        self.show_themed_dialog("info_outline", self.lang["info"], content, [("OK", None, None)])


class LanguageDialog:
    def __init__(self, window: AppWindow, lang: dict, on_language_change):
        self.window = window
        self.lang = lang
        self.on_language_change = on_language_change
        self.ui = UIComponents(window, lang)

    def show(self):
        colors = ThemeManager.get_theme_colors(self.window.theme_mode)
        column = QWidget()
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        langs = [
            ("Русский", "Ru"),
            ("English", "En"),
            ("Українська", "Uk"),
            ("Беларуская", "Be"),
            ("Polski", "Pl"),
        ]
        for label, code in langs:
            btn = AnimatedTextButton(label, colors["button_color"])
            btn.clicked.connect(lambda checked=False, c=code: self.on_language_change(c))
            layout.addWidget(btn)

        column.setFixedSize(250, 220)
        self.ui.show_themed_dialog(
            "language",
            self.lang["sel_lang"],
            column,
            [(self.lang["cancel"], None, colors["button_color"])],
            width=320,
        )
        return None, None, None