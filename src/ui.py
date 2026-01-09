import flet as ft
import locale
from localization import translations
import os
from resources import get_asset_path
import logging
from datetime import datetime
import traceback
from screeninfo import get_monitors
from updater import check_for_updates, download_update
from converter import process_raw, process_png, struct, _write_metadata
import subprocess
import threading
import time
from config import VERSION, BUILD
from ui_components import UIComponents, ThemeManager, LanguageDialog
from lang_manager import LanguageManager

CHECKED_FOR_UPDATES = False

log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"dgc_{log_timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

locale.setlocale(locale.LC_ALL, '')
current_locale = locale.getlocale()[0]
system_lang = current_locale[:2] if current_locale else 'En'

lang = LanguageManager.set_language(system_lang if system_lang in translations else 'En')

class PageHelper:
    def __init__(self, page: ft.Page):
        self.page = page

    def minimize(self, e):
        self.page.window.minimized = True
        self.page.update()

    def close(self, e):
        self.page.window.close()

def create_ui(page: ft.Page, lang_code="En"):
    global lang

    if lang_code is None:
        lang_code = LanguageManager.get_language()
    
    if lang_code in translations:
        lang = translations[lang_code]
        LanguageManager.set_language(lang_code)
    else:
        logging.warning(f"Unsupported language code '{lang_code}', defaulting to English.")
        lang = translations["En"]
        LanguageManager.set_language("En")

    page.title = "DisplaceBox"
    page.theme_mode = "dark"

    monitor = get_monitors()[0]
    screen_width = monitor.width
    screen_height = monitor.height

    page.window.width = 580
    page.window.height = 680
    scale_factor = 1.0

    page.window.resizable = False
    page.window.maximizable = False
    page.window.minimizable = True
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.window.icon = get_asset_path('icon.ico')
    page.window.center()

    helper = PageHelper(page)
    ui_components = UIComponents(page, lang, scale_factor)

    def switch_to_reverse_ui(page: ft.Page):
        from reverse_ui import create_back_ui
        logging.info("Switched to \".raw/.png to .bin\" mode")
        page.clean()
        create_back_ui(page, LanguageManager.get_language())

    # Создаем верхнюю панель
    top_bar, minimize_btn, close_btn, topbarico = ui_components.create_top_bar(helper)
    page.add(top_bar)

    # Создаем заголовок
    title_container, title_image = ui_components.create_title_container()

    input_file_path = None
    dialog_open = False

    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal input_file_path
        try:
            if e.files:
                input_file_path = e.files[0].path

            if not input_file_path.lower().endswith('.bin'):
                ui_components.show_error_dialog(lang["error"], lang["wrong_extension"])
                file_name.value = ""
                input_file_path = None
                logging.error("Selected file is not .bin file!")
                page.update()
                return
        except AttributeError:
            logging.info("User closed file picker.")
            return

        file_name.value = input_file_path
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    def select_file(e):
        file_picker.pick_files()

    meta_dlg_titleicon = ft.Icon(ft.Icons.INFO_OUTLINE, size=30, color=ft.Colors.WHITE)
    meta_dlg_titletext = ft.Text(lang["metadatainfo"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE)

    def metadata_info_dialog(e):
        def close_dlgmeta(e):
            nonlocal dialog_open
            meta_dlg.open = False
            dialog_open = False
            page.update()

        meta_dlg = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    meta_dlg_titleicon,
                    meta_dlg_titletext
                ],
            ),
            content=ft.Text(lang["meta_text"]),
            actions=[
                ft.TextButton("OK", on_click=close_dlgmeta)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(meta_dlg)
        page.update()

    icon_help_title = ft.Icon(ft.Icons.INFO_OUTLINE, size=30, color=ft.Colors.WHITE)
    text_help_title = ft.Text(lang["help"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE)

    def helpdialog(e):
        def close_dlghelp(e):
            nonlocal dialog_open
            help_dlg.open = False
            dialog_open = False
            page.update()

        help_dlg = ft.AlertDialog(
            open=True,
            title=ft.Row(
                [
                    icon_help_title,
                    text_help_title,
                ],
            ),
            content=ft.Text(lang["help_text"]),
            actions=[
                ft.TextButton(lang["metadatainfo"], on_click=lambda e: [close_dlghelp(e), metadata_info_dialog(e)]),
                ft.TextButton("OK", on_click=close_dlghelp)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(help_dlg)
        page.update()

    file_name = ft.TextField(
        value="",
        label=lang["select_file"],
        read_only=True,
        border_color="#46678F",
        width=int(400 * scale_factor),
        label_style=ft.TextStyle(size=int(14 * scale_factor)),
        text_style=ft.TextStyle(size=int(14 * scale_factor)),
        content_padding=ft.padding.symmetric(
            horizontal=int(12 * scale_factor),
            vertical=int(8 * scale_factor)
        )
    )

    select_button = ft.ElevatedButton(
        text=lang["sel_button"], 
        on_click=select_file, 
        style=ft.ButtonStyle(
            color="#9ecaff",
            padding=ft.padding.symmetric(
                horizontal=int(20 * scale_factor),
                vertical=int(10 * scale_factor)
            ),
            overlay_color=ft.Colors.with_opacity(0.1, "#9ecaff"),
            text_style=ft.TextStyle(
                size=int(14 * scale_factor)
            )
        )
    )

    output_format_text = ft.Text(
        lang["select_format"],
        size=int(16 * scale_factor),
        text_align=ft.TextAlign.CENTER
    )

    output_format = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(
                label=".raw",
                value="RAW",
                scale=scale_factor,
                label_style=ft.TextStyle(
                    size=int(15 * scale_factor)
                )
            ),
            ft.Container(width=int(20 * scale_factor)),
            ft.Radio(
                label=".png",
                value="PNG",
                scale=scale_factor,
                label_style=ft.TextStyle(
                    size=int(15 * scale_factor),
                    weight=ft.FontWeight.W_500
                )
            )
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0)
    )

    output_size = ft.Container(
        content=ft.Dropdown(
            options=[
                ft.dropdown.Option(key="64", text="4x4"),
                ft.dropdown.Option(key="128", text="8x8"),
                ft.dropdown.Option(key="256", text="16x16"),
                ft.dropdown.Option(key="512", text="32x32"),
                ft.dropdown.Option(key="1024", text="64x64")
            ],
            label=lang["select_size"],
            label_style=ft.TextStyle(size=int(12 * scale_factor)),
            text_style=ft.TextStyle(size=int(12 * scale_factor)),
            border_color="#46678F",
            content_padding=ft.padding.symmetric(
                horizontal=int(12 * scale_factor),
                vertical=int(4 * scale_factor)
            ),
            width=int(350 * scale_factor)
        ),
        height=int(35 * scale_factor)
    )

    process_button = ft.ElevatedButton(
        text=lang["convert_file"], 
        on_click=lambda e: process_file(e), 
        style=ft.ButtonStyle(
            color="#9ecaff", 
            padding=ft.padding.only(
                left=int(16 * scale_factor),
                top=int(6 * scale_factor),
                right=int(16 * scale_factor),
                bottom=int(6 * scale_factor)
            ),
            overlay_color=ft.Colors.with_opacity(0.1, "#9ecaff"),
            text_style=ft.TextStyle(
                size=int(12 * scale_factor)
            )
        )
    )

    def process_file(e):
        if input_file_path and output_format.value and output_size.content.value:
            try:
                size = int(output_size.content.value)
            except Exception:
                try:
                    size = int(output_size.content.options[0].key)
                except Exception:
                    size = 64

            output_path = os.path.splitext(input_file_path)[0] + (".raw" if output_format.value == "RAW" else ".png")

            try:
                if output_format.value == "RAW":
                    _min, _max, _del, json_path = process_raw(input_file_path, output_path, size, True)
                else:
                    _min, _max, _del, json_path = process_png(input_file_path, output_path, size, True)

                def close_dlgconvert(e):
                    convertsuc.open = False
                    page.update()

                content_controls = [
                    ft.Text(f"{lang['file_saved']}:", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(output_path, size=12, width=450, color=ft.Colors.WHITE),
                ]

                if json_path:
                    content_controls.extend([
                        ft.Text(f"{lang['meta_path']}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(json_path, size=12, width=450, color=ft.Colors.WHITE),
                    ])

                convertsuc = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.GREEN_900,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK, size=30, color=ft.Colors.WHITE),
                            ft.Text(lang["result"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Column(content_controls, tight=True),
                    actions=[
                        ft.TextButton("OK", on_click=close_dlgconvert, style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    on_dismiss=lambda e: logging.info(f"Min: {_min:.1f}, Max: {_max:.1f}, Delta: {_del:.1f}"),
                )
                page.overlay.append(convertsuc)
                logging.info(f"Converted file saved to: {output_path}")
                page.update()

            except struct.error as e:
                def close_banner(e):
                    errordialog.open = False
                    page.update()

                errordialog = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.RED_900,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.WHITE),
                            ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Text(lang["struct_error"], color=ft.Colors.WHITE),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: close_banner(e), style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.TextButton(lang["help"], on_click=lambda e: [close_banner(e), helpdialog(e)], style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                logging.error(f"struct.error occurred: {e}")
                logging.error("Traceback:\n" + traceback.format_exc())
                page.overlay.append(errordialog)
                page.update()

            except ZeroDivisionError as e:
                def close_zerbanner(e):
                    zererrordialog.open = False
                    page.update()

                zererrordialog = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.RED_ACCENT_700,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR, size=30, color=ft.Colors.WHITE),
                            ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Text(lang["zerodiv_error"], color=ft.Colors.WHITE),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: close_zerbanner(e), style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.TextButton(lang["opengit"], on_click=lambda e: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter/issues/new"), style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                logging.error(f"ZeroDivisionError occurred: {e}")
                logging.error("Traceback:\n" + traceback.format_exc())
                page.overlay.append(zererrordialog)
                page.update()

        else:
            if not input_file_path or not output_format.value or not output_size.content.value:
                def close_dlgpleaseselfile(e):
                    nonlocal dialog_open
                    plsselfile.open = False
                    dialog_open = False
                    page.update()

                plsselfile = ft.AlertDialog(
                    open=True,
                    bgcolor=ft.Colors.RED_900,
                    title=ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING, size=30, color=ft.Colors.AMBER),
                            ft.Text(lang["error"], style=ft.TextThemeStyle.TITLE_MEDIUM, color=ft.Colors.WHITE),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    content=ft.Text(lang["plssel_file"], color=ft.Colors.WHITE),
                    actions=[
                        ft.TextButton("OK", on_click=close_dlgpleaseselfile, style=ft.ButtonStyle(color=ft.Colors.WHITE))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.overlay.append(plsselfile)
                logging.warning("File is not selected!")
                page.update()

    def change_language(language_code):
        global lang
        lang = translations[language_code]
        LanguageManager.set_language(language_code)
        ui_components.lang = lang
        update_ui()
        show_language_dialog(None)

    def update_ui():
        try:
            top_bar.content.content.controls[0].controls[1].value = f"{page.title} {VERSION}"
            top_bar.content.content.controls[1].controls[0].tooltip = lang["min"]
            top_bar.content.content.controls[1].controls[1].tooltip = lang["exit"]
            file_name.label = lang["select_file"]
            select_button.text = lang["sel_button"]
            output_format_text.value = lang["select_format"]
            output_format.content.controls[0].label = ".raw"
            output_format.content.controls[2].label = ".png"
            try:
                output_size.content.label = lang["select_size"]
            except Exception:
                pass
            process_button.text = lang["convert_file"]
            toolbar_buttons['help'].content.tooltip = lang["help"]
            toolbar_buttons['language'].content.tooltip = lang["cnglang"]
            toolbar_buttons['theme'].tooltip = lang["toggletheme"]
            social_buttons['github'].content.tooltip = lang["github"]
            social_buttons['discord'].content.tooltip = lang["discord"]
            social_buttons['telegram'].content.tooltip = lang["telegram"]
            social_buttons['youtube'].content.tooltip = lang["youtube"]
            toolbar_buttons['mode'].tooltip = lang["modeswitch2"]
            text_help_title.value = lang["help"]
            page.update()
        except Exception as ex:
            logging.error("update_ui error: " + str(ex))

    def show_language_dialog(e):
        lang_dialog = LanguageDialog(page, lang, change_language)
        langdlgicon, langdlgtext, lang_buttons = lang_dialog.show()

    def toggle_theme(e):
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        update_theme()

    def update_theme():
        colors = ThemeManager.get_theme_colors(page.theme_mode)
        
        try:
            toolbar_buttons['help'].content.icon_color = colors['icon_color']
            toolbar_buttons['language'].content.icon_color = colors['icon_color']
            toolbar_buttons['theme'].icon = colors['theme_icon']
            toolbar_buttons['theme'].icon_color = colors['icon_color']
            toolbar_buttons['mode'].icon_color = colors['icon_color']
            
            social_buttons['github'].content.color = colors['icon_color']
            social_buttons['discord'].content.color = colors['icon_color']
            social_buttons['telegram'].content.color = colors['icon_color']
            social_buttons['youtube'].content.color = colors['icon_color']
            
            title_image.src = colors['logo_src']
            icon_help_title.color = colors['text_color']
            text_help_title.color = colors['text_color']
            meta_dlg_titleicon.color = colors['text_color']
            meta_dlg_titletext.color = colors['text_color']
            minimize_btn.icon_color = colors['icon_color']
            close_btn.icon_color = colors['icon_color']
            topbarico.src = colors['topbar_logo']
            
            try:
                output_size.content.border_color = colors['border_color']
            except Exception:
                pass
            file_name.border_color = colors['border_color']
            select_button.style.color = colors['icon_color']
            process_button.style.color = colors['icon_color']
            vertext.color = colors['version_color']

            page.update()
        except Exception as ex:
            logging.debug("update_theme partial: " + str(ex))

    # Создаем кнопки тулбара
    toolbar_buttons = ui_components.create_toolbar_buttons(
        on_help=helpdialog,
        on_language=show_language_dialog,
        on_theme=toggle_theme,
        on_mode_switch=lambda e: switch_to_reverse_ui(page),
        mode_tooltip_key="modeswitch2"
    )

    # Создаем социальные кнопки
    social_buttons = ui_components.create_social_buttons()

    # Создаем контейнер тулбара
    toolbar_container = ui_components.create_toolbar_container(toolbar_buttons, social_buttons)

    # Создаем контейнер версии
    version_container, vertext = ui_components.create_version_container(
        on_click=ui_components.show_version_info
    )

    main_content = ft.Container(
        content=ft.Column(
            [
                title_container,
                ft.Container(height=int(10 * scale_factor)),
                
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=file_name,
                                alignment=ft.alignment.center
                            ),
                            ft.Container(height=int(10 * scale_factor)),
                            ft.Container(
                                content=select_button,
                                alignment=ft.alignment.center
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0
                    ),
                    padding=ft.padding.symmetric(
                        horizontal=int(20 * scale_factor),
                        vertical=int(10 * scale_factor)
                    ),
                ),
                
                ft.Container(height=int(20 * scale_factor)),
                
                ft.Container(
                    content=ft.Column(
                        [
                            output_format_text,
                            ft.Container(height=int(10 * scale_factor)),
                            output_format,
                            ft.Container(height=int(30 * scale_factor)),
                            ft.Container(
                                content=output_size,
                                width=int(300 * scale_factor),
                                alignment=ft.alignment.center,
                            ),
                            ft.Container(height=int(30 * scale_factor)),
                            process_button,
                            ft.Container(height=int(20 * scale_factor)),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(horizontal=int(20 * scale_factor)),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        expand=True,
    )

    page.add(main_content)
    page.add(toolbar_container)
    page.add(version_container)

    # Код проверки обновлений остаётся без изменений...
    def check_updates():
        try:
            update_info = check_for_updates(VERSION)
            
            if update_info.get('update_available'):
                def close_update_dialog(e):
                    update_dlg.open = False
                    page.update()
                    logging.info("Update dialog closed by user")
                    
                def start_update(e):
                    try:
                        update_dlg.open = False
                        page.update()
                        logging.info("Starting update process")

                        # Thread-safe флаг отмены
                        cancel_event = threading.Event()
                        
                        def close_download_dialog(e):
                            cancel_event.set()
                            logging.info("Download cancellation requested")

                        progress_bar = ft.ProgressBar(width=400, color="PRIMARY")
                        progress_text = ft.Text("0.0 MB / 0.0 MB", size=12, color=ft.Colors.GREY_500)
                        status_text = ft.Text("", size=11, color=ft.Colors.GREY_400)
                        
                        download_dlg = ft.AlertDialog(
                            modal=True,
                            title=ft.Row([
                                ft.Icon(ft.Icons.DOWNLOAD, color=ft.Colors.BLUE_400),
                                ft.Text(lang["downloading"]),
                            ]),
                            content=ft.Column([
                                progress_bar,
                                ft.Container(
                                    content=progress_text,
                                    alignment=ft.alignment.center_right,
                                    padding=ft.padding.only(top=5)
                                ),
                                status_text
                            ], tight=True),
                            actions=[
                                ft.TextButton(
                                    lang["cancel"],
                                    on_click=close_download_dialog,
                                )
                            ],
                            actions_alignment=ft.MainAxisAlignment.END,
                        )

                        page.overlay.append(download_dlg)
                        download_dlg.open = True
                        page.update()
                        
                        last_update_time = [0]  # Используем список для изменяемости
                        
                        def update_progress(value, current_size, total_size, cancel_fn):
                            # Ограничиваем частоту обновлений UI (не чаще 10 раз в секунду)
                            current_time = time.time()
                            if current_time - last_update_time[0] < 0.1 and value < 99:
                                return
                            last_update_time[0] = current_time
                            
                            if cancel_event.is_set():
                                cancel_fn()
                                return
                                
                            progress_bar.value = value / 100
                            progress_text.value = f"{current_size:.1f} MB / {total_size:.1f} MB"
                            
                            # Показываем скорость
                            if hasattr(update_progress, 'last_size') and hasattr(update_progress, 'last_time'):
                                time_diff = current_time - update_progress.last_time
                                if time_diff > 0:
                                    size_diff = current_size - update_progress.last_size
                                    speed = size_diff / time_diff
                                    status_text.value = f"{lang.get('speed', 'Speed')}: {speed:.2f} MB/s"
                            
                            update_progress.last_size = current_size
                            update_progress.last_time = current_time
                            page.update()
                        
                        try:
                            # Извлекаем checksum если доступен
                            expected_checksum = update_info.get('checksum')
                            
                            save_path = download_update(
                                update_info['download_url'], 
                                update_progress,
                                expected_checksum
                            )
                            
                            if save_path:
                                download_dlg.open = False
                                logging.info("Download completed successfully")
                                
                                success_dlg = ft.AlertDialog(
                                    title=ft.Row([
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400),
                                        ft.Text(lang["update_downloaded"]),
                                    ]),
                                    content=ft.Text(lang["restart"]),
                                )
                                page.overlay.append(success_dlg)
                                success_dlg.open = True
                                page.update()
                                
                                logging.info("Preparing to restart application")
                                
                                def restart_app():
                                    try:
                                        time.sleep(1)
                                        logging.info(f"Starting new version from: {save_path}")
                                        subprocess.Popen([save_path])
                                        logging.info("New version started successfully")
                                        page.window.destroy()
                                    except Exception as e:
                                        logging.error(f"Failed to start new version: {e}")
                                
                                threading.Thread(target=restart_app, daemon=True).start()
                            else:
                                # Скачивание отменено
                                download_dlg.open = False
                                page.update()
                                logging.info("Download was cancelled")
                        
                        except Exception as e:
                            from updater import DownloadCancelled, UpdateError
                            
                            logging.error(f"Update error: {str(e)}")
                            download_dlg.open = False
                            
                            # Различаем типы ошибок
                            if isinstance(e, DownloadCancelled):
                                logging.info("Download cancelled by user")
                                # Не показываем ошибку при отмене пользователем
                                page.update()
                                return
                            
                            # Показываем понятную ошибку
                            error_title = lang.get("update_error", "Update Error")
                            if isinstance(e, UpdateError):
                                error_msg = str(e)
                            else:
                                error_msg = f"{lang.get('unexpected_error', 'Unexpected error')}: {str(e)}"
                            
                            error_dlg = ft.AlertDialog(
                                title=ft.Row([
                                    ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400),
                                    ft.Text(error_title),
                                ]),
                                content=ft.Column([
                                    ft.Text(error_msg, size=14),
                                    ft.Container(height=10),
                                    ft.Text(
                                        lang.get("try_manual", "You can download the update manually from GitHub"),
                                        size=12,
                                        color=ft.Colors.GREY_500
                                    )
                                ], tight=True),
                                actions=[
                                    ft.TextButton(
                                        lang.get("open_github", "Open GitHub"),
                                        on_click=lambda _: page.launch_url("https://github.com/stakanyash/displacebin_gui_converter/releases")
                                    ),
                                    ft.TextButton("OK", on_click=lambda _: (setattr(error_dlg, 'open', False), page.update()))
                                ],
                                actions_alignment=ft.MainAxisAlignment.END,
                            )
                            page.overlay.append(error_dlg)
                            error_dlg.open = True
                            page.update()
                            
                    except Exception as e:
                        logging.error(f"Error in start_update: {str(e)}")
                        logging.error(traceback.format_exc())
                        page.update()

                # Обработка changelog
                changelog_text = update_info.get('description', '')
                changelog_text = changelog_text.replace('###', '')
                changelog_text = changelog_text.replace('##', '')
                changelog_text = changelog_text.replace('#', '')
                changelog_text = changelog_text.replace('*', '')
                changelog_text = changelog_text.replace('`', '')
                changelog_text = changelog_text.replace('>', '')
                changelog_text = changelog_text.replace('-', '•')
                changelog_text = '\n'.join(line.strip() for line in changelog_text.split('\n') if line.strip())
                
                # Информация о размере файла
                file_size_mb = update_info.get('file_size', 0) / (1024 * 1024)
                size_info = f"\n{lang.get('file_size', 'File size')}: {file_size_mb:.1f} MB" if file_size_mb > 0 else ""
                
                update_dlg = ft.AlertDialog(
                    title=ft.Row([
                        ft.Icon(ft.Icons.SYSTEM_UPDATE, color=ft.Colors.BLUE_400),
                        ft.Text(lang["update_available"]),
                    ]),
                    content=ft.Container(
                        width=550,
                        content=ft.Column([
                            ft.Text(
                                f"{lang['version_for_download']} {update_info['version']}{size_info}",
                                size=16,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Divider(),
                            ft.Container(
                                content=ft.ListView(
                                    [
                                        ft.Text(
                                            changelog_text,
                                            selectable=True,
                                            size=14,
                                        )
                                    ],
                                    spacing=10,
                                    height=350,
                                ),
                                padding=10,
                                height=350,
                            )
                        ], tight=True, spacing=10),
                    ),
                    actions=[
                        ft.TextButton(
                            lang["update_now"],
                            on_click=start_update,
                            style=ft.ButtonStyle(color=ft.Colors.BLUE_400)
                        ),
                        ft.TextButton(
                            lang["cancel"],
                            on_click=close_update_dialog
                        )
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                page.overlay.append(update_dlg)
                update_dlg.open = True
                logging.info(f"{update_info['version']} update available.")
                page.update()
                
        except Exception as e:
            logging.error(f"Error checking for updates: {str(e)}")
            logging.error(traceback.format_exc())

    global CHECKED_FOR_UPDATES

    if not CHECKED_FOR_UPDATES:
        check_updates()
        CHECKED_FOR_UPDATES = True

    update_theme()
    update_ui()