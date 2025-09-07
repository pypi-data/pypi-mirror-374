from fspacker import call_console


def fsloader_console() -> None:
    call_console(is_gui=False)


def fsloader_window() -> None:
    call_console(is_gui=True)
