import flet as ft
from resources import get_asset_path
from config import VERSION, BUILD
import logging

class UIComponents:
    def __init__(self, page: ft.Page, lang: dict, scale_factor: float = 1.0):
        self.page = page
        self.lang = lang
        self.scale_factor = scale_factor
        self.icon_size = int(24 * scale_factor)
        
    def create_top_bar(self, helper):
        btn_size = int(28 * self.scale_factor)
        icon_size = int(14 * self.scale_factor)
        
        minimize_btn = ft.IconButton(
            icon=ft.Icons.REMOVE,
            icon_size=icon_size,
            tooltip=self.lang["min"],
            on_click=helper.minimize,
            padding=int(4 * self.scale_factor),
            width=btn_size,
            height=btn_size,
        )

        close_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=icon_size,
            tooltip=self.lang["exit"],
            on_click=helper.close,
            padding=int(4 * self.scale_factor),
            width=btn_size,
            height=btn_size,
        )

        topbarico = ft.Image(
            src=get_asset_path('icon.ico'), 
            width=16, 
            height=16
        )

        top_bar = ft.Container(
            height=int(27 * self.scale_factor),
            bgcolor=ft.Colors.SURFACE,
            padding=ft.padding.symmetric(horizontal=int(8 * self.scale_factor)),
            content=ft.WindowDragArea(
                ft.Row(
                    [
                        ft.Row(
                            [
                                topbarico,
                                ft.Text(
                                    f"{self.page.title} {VERSION}",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [minimize_btn, close_btn],
                            spacing=4,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ),
        )
        
        return top_bar, minimize_btn, close_btn, topbarico

    def create_title_container(self):
        title_image = ft.Image(
            src=get_asset_path('logo.png'),
            fit=ft.ImageFit.CONTAIN
        )

        title_container = ft.Container(
            content=title_image,
            padding=ft.padding.only(
                top=int(10 * self.scale_factor),
                bottom=int(5 * self.scale_factor)
            ),
            alignment=ft.alignment.center,
            height=int(120 * self.scale_factor)
        )
        
        return title_container, title_image

    def show_error_dialog(self, title: str, message: str):
        def close_error_dialog(e):
            error_dialog.open = False
            self.page.update()

        error_dialog = ft.AlertDialog(
            open=True,
            bgcolor=ft.Colors.RED_900,
            title=ft.Row(
                [
                    ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.WHITE),
                    ft.Text(title, color=ft.Colors.WHITE)
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
            ),
            content=ft.Text(message, color=ft.Colors.WHITE),
            actions=[
                ft.TextButton(
                    "OK", 
                    on_click=close_error_dialog, 
                    style=ft.ButtonStyle(color=ft.Colors.WHITE)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(error_dialog)
        self.page.update()

    def create_toolbar_buttons(self, on_help, on_language, on_theme, on_mode_switch, mode_tooltip_key="modeswitch2"):
        icon_color = ThemeManager.get_theme_colors(self.page.theme_mode)['icon_color']
        
        help_icon = ft.Icons.HELP_OUTLINE
        hover_icon = ft.Icons.HELP
        
        help_btn = ft.Container(
            content=ft.IconButton(
                icon=help_icon,
                on_click=on_help,
                icon_color=icon_color,
                tooltip=self.lang["help"],
                icon_size=self.icon_size,
                width=int(40 * self.scale_factor),
                height=int(40 * self.scale_factor)
            ),
            on_hover=lambda e: setattr(
                help_btn.content, 
                'icon', 
                hover_icon if e.data == 'true' else help_icon
            )
        )

        language_icon = ft.Icons.LANGUAGE
        language_hover_icon = ft.Icons.LANGUAGE_OUTLINED

        language_btn = ft.Container(
            content=ft.IconButton(
                icon=language_icon,
                on_click=on_language,
                icon_color=icon_color,
                tooltip=self.lang["cnglang"],
                icon_size=self.icon_size,
                width=int(40 * self.scale_factor),
                height=int(40 * self.scale_factor)
            ),
            on_hover=lambda e: setattr(
                language_btn.content, 
                'icon', 
                language_hover_icon if e.data == 'true' else language_icon
            )
        )

        theme_btn = ft.IconButton(
            icon=ft.Icons.BRIGHTNESS_MEDIUM,
            on_click=on_theme,
            icon_color=icon_color,
            tooltip=self.lang["toggletheme"],
            icon_size=self.icon_size,
            width=int(40 * self.scale_factor),
            height=int(40 * self.scale_factor)
        )

        rev_btn = ft.IconButton(
            icon=ft.Icons.SWAP_HORIZ,
            icon_size=self.icon_size,
            icon_color=icon_color,
            tooltip=self.lang.get(mode_tooltip_key, "Switch mode"),
            on_click=on_mode_switch
        )

        return {
            'help': help_btn,
            'language': language_btn,
            'theme': theme_btn,
            'mode': rev_btn
        }

    def create_social_buttons(self):
        icon_color = ThemeManager.get_theme_colors(self.page.theme_mode)['icon_color']
        
        git_btn = ft.IconButton(
            content=ft.Image(
                src=get_asset_path('git.png'),
                width=self.icon_size,
                height=self.icon_size,
                color=icon_color,
                tooltip=self.lang["github"]
            ),
            on_click=lambda e: self.page.launch_url(
                "https://github.com/stakanyash/displacebin_gui_converter"
            ),
        )

        dis_btn = ft.IconButton(
            content=ft.Image(
                src=get_asset_path('dis.png'),
                width=self.icon_size,
                height=self.icon_size,
                color=icon_color,
                tooltip=self.lang["discord"]
            ),
            on_click=lambda e: self.page.launch_url(
                "https://discord.com/invite/Cd5GanuYud"
            ),
        )

        tg_btn = ft.IconButton(
            content=ft.Image(
                src=get_asset_path('tg.png'),
                width=self.icon_size,
                height=self.icon_size,
                color=icon_color,
                tooltip=self.lang["telegram"]
            ),
            on_click=lambda e: self.page.launch_url(
                "https://t.me/stakanyasher"
            ),
        )

        yt_btn = ft.IconButton(
            content=ft.Image(
                src=get_asset_path('yt.png'),
                width=self.icon_size,
                height=self.icon_size,
                color=icon_color,
                tooltip=self.lang["youtube"]
            ),
            on_click=lambda e: self.page.launch_url(
                "https://www.youtube.com/@stakanyash"
            ),
        )

        return {
            'github': git_btn,
            'discord': dis_btn,
            'telegram': tg_btn,
            'youtube': yt_btn
        }

    def create_toolbar_container(self, toolbar_buttons, social_buttons):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            toolbar_buttons['help'],
                            ft.Container(width=int(10 * self.scale_factor)),
                            toolbar_buttons['language'],
                            ft.Container(width=int(10 * self.scale_factor)),
                            toolbar_buttons['theme'],
                            ft.Container(width=int(10 * self.scale_factor)),
                            toolbar_buttons['mode'],
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=int(10 * self.scale_factor)),
                    ft.Row(
                        [
                            social_buttons['github'],
                            ft.Container(width=int(10 * self.scale_factor)),
                            social_buttons['discord'],
                            ft.Container(width=int(10 * self.scale_factor)),
                            social_buttons['telegram'],
                            ft.Container(width=int(10 * self.scale_factor)),
                            social_buttons['youtube'],
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(bottom=int(10 * self.scale_factor)),
        )

    def create_version_container(self, on_click):
        vertext = ft.Text(
            f"{VERSION} {BUILD}", 
            size=10, 
            color=ft.Colors.GREY
        )
        
        version_text = ft.GestureDetector(
            content=vertext,
            on_tap=on_click
        )

        version_container = ft.Container(
            content=version_text,
            alignment=ft.alignment.bottom_right,
            padding=ft.padding.only(right=10, bottom=10),
        )
        
        return version_container, vertext

    def show_version_info(self, e):
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        colors = ThemeManager.get_theme_colors(self.page.theme_mode)
        text_color = colors['text_color']
        
        infoicon = ft.Icon(ft.Icons.INFO_OUTLINE, size=30, color=text_color)

        content_column = ft.Container(
            content=ft.Column([
                ft.Text(
                    spans=[
                        ft.TextSpan("powered by "),
                        ft.TextSpan("Python", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://www.python.org/"),
                        ft.TextSpan(", "),
                        ft.TextSpan("Flet", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://flet.dev/"),
                        ft.TextSpan(", "),
                        ft.TextSpan("Pillow", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://pillow.readthedocs.io/en/stable/"),
                        ft.TextSpan(", "),
                        ft.TextSpan("locale", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/locale.html"),
                        ft.TextSpan(", "),
                        ft.TextSpan("logging", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/logging.html"),
                        ft.TextSpan(", "),
                        ft.TextSpan("datetime", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/datetime.html"),
                        ft.TextSpan(", "),
                        ft.TextSpan("traceback", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/traceback.html"),
                        ft.TextSpan(", "),
                        ft.TextSpan("pathlib", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/pathlib.html"),
                        ft.TextSpan(", "),
                        ft.TextSpan("math", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/math.html"),
                        ft.TextSpan(", "),
                        ft.TextSpan("struct", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/struct.html"),
                        ft.TextSpan(", "),
                        ft.TextSpan("sys", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://docs.python.org/3/library/sys.html"),
                    ],
                    selectable=True,
                    no_wrap=False,
                    color=text_color,
                ),
                ft.Text(
                    spans=[
                        ft.TextSpan("Authors: "),
                        ft.TextSpan("stakan ", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://github.com/stakanyash"),
                        ft.TextSpan("(GUI), "),
                        ft.TextSpan("ThePlain ", style=ft.TextStyle(color=ft.Colors.BLUE_400), url="https://github.com/ThePlain"),
                        ft.TextSpan("(conversion script)"),
                    ],
                    selectable=True,
                    no_wrap=False,
                    color=text_color,
                )
            ]),
            height=120,
            width=300,
            padding=10
        )

        dialog = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    infoicon,
                    ft.Text(self.lang["info"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=text_color)
                ],
            ),
            content=content_column,
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dialog)
        self.page.update()

class ThemeManager:
    @staticmethod
    def get_theme_colors(theme_mode: str):
        if theme_mode == "dark":
            return {
                'icon_color': "#9ecaff",
                'logo_src': get_asset_path('logo.png'),
                'topbar_logo': get_asset_path('icon.ico'),
                'text_color': ft.Colors.WHITE,
                'theme_icon': ft.Icons.BRIGHTNESS_MEDIUM,
                'border_color': "#46678F",
                'version_color': ft.Colors.GREY,
                'button_color': "#9ecaff"
            }
        else:
            return {
                'icon_color': "black",
                'logo_src': get_asset_path('logo_white.png'),
                'topbar_logo': get_asset_path('iconblack.ico'),
                'text_color': ft.Colors.BLACK,
                'theme_icon': ft.Icons.BRIGHTNESS_3,
                'border_color': "#000000",
                'version_color': ft.Colors.BLACK,
                'button_color': "#1976D2"
            }

class LanguageDialog:
    def __init__(self, page: ft.Page, lang: dict, on_language_change):
        self.page = page
        self.lang = lang
        self.on_language_change = on_language_change
        
    def show(self):
        colors = ThemeManager.get_theme_colors(self.page.theme_mode)
        text_color = colors['text_color']
        button_color = colors['button_color']
        
        def close_language_dialog(e):
            language_dialog.open = False
            self.page.update()

        lang_buttons = [
            ft.TextButton("Русский", on_click=lambda e: self.on_language_change("Ru"), style=ft.ButtonStyle(color=button_color)),
            ft.TextButton("English", on_click=lambda e: self.on_language_change("En"), style=ft.ButtonStyle(color=button_color)),
            ft.TextButton("Українська", on_click=lambda e: self.on_language_change("Uk"), style=ft.ButtonStyle(color=button_color)),
            ft.TextButton("Беларуская", on_click=lambda e: self.on_language_change("Be"), style=ft.ButtonStyle(color=button_color)),
            ft.TextButton("Polski", on_click=lambda e: self.on_language_change("Pl"), style=ft.ButtonStyle(color=button_color))
        ]

        langdlgicon = ft.Icon(ft.Icons.LANGUAGE, size=30, color=text_color)
        langdlgtext = ft.Text(self.lang["sel_lang"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=text_color)

        language_dialog = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    langdlgicon,
                    langdlgtext
                ],
            ),
            content=ft.Container(
                content=ft.Column(
                    lang_buttons,
                    spacing=10,
                ),
                width=250,
                height=200,
            ),
            actions=[
                ft.TextButton(self.lang["cancel"], on_click=close_language_dialog, style=ft.ButtonStyle(color=button_color))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(language_dialog)
        self.page.update()
        
        return langdlgicon, langdlgtext, lang_buttons