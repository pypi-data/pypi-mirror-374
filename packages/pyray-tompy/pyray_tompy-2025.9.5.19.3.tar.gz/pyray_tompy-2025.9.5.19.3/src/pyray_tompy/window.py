import pyray as pr


def get_current_window_monitor() -> int:
    """Pyray check for which system monitor the pyray window is located on."""
    monitor_number: int = 0  # Default monitor number

    window_pos = pr.get_window_position()
    monitor_count: int = pr.get_monitor_count()

    for monitor in range(monitor_count):
        monitor_pos = pr.get_monitor_position(monitor)
        monitor_width: int = pr.get_monitor_width(monitor)
        monitor_height: int = pr.get_monitor_height(monitor)

        is_window_inside_monitor_x_axis: bool = monitor_pos.x <= window_pos.x < monitor_pos.x + monitor_width
        is_window_inside_monitor_y_axis: bool = monitor_pos.y <= window_pos.y < monitor_pos.y + monitor_height
        is_window_inside_monitor_area: bool = is_window_inside_monitor_x_axis and is_window_inside_monitor_y_axis

        if is_window_inside_monitor_area:
            monitor_number = monitor

    return monitor_number


def set_window_from_monitor(fraction: float) -> None:
    monitor: int = get_current_window_monitor()
    monitor_width = pr.get_monitor_width(monitor)
    monitor_height = pr.get_monitor_height(monitor)

    width: int = int(monitor_width * fraction)
    height: int = int(monitor_height * fraction)
    pr.set_window_size(width, height)


def set_and_center_window_from_monitor(fraction: float) -> None:
    monitor: int = get_current_window_monitor()
    monitor_width = pr.get_monitor_width(monitor)
    monitor_height = pr.get_monitor_height(monitor)

    width: int = int(monitor_width * fraction)
    height: int = int(monitor_height * fraction)
    pr.set_window_size(width, height)

    centered_window_position_x: int = int((monitor_width - width) / 2)
    centered_window_position_y: int = int((monitor_height - height) / 2)
    pr.set_window_position(centered_window_position_x, centered_window_position_y)


def set_and_center_window(width: int, height: int) -> None:
    monitor: int = get_current_window_monitor()
    monitor_width = pr.get_monitor_width(monitor)
    monitor_height = pr.get_monitor_height(monitor)

    pr.set_window_size(width, height)

    centered_window_position_x: int = int((monitor_width - width) / 2)
    centered_window_position_y: int = int((monitor_height - height) / 2)
    pr.set_window_position(centered_window_position_x, centered_window_position_y)


def get_monitor_mode() -> tuple[int, int, int, int]:
    monitor_number: int = get_current_window_monitor()
    monitor_width = pr.get_monitor_width(monitor_number)
    monitor_height = pr.get_monitor_height(monitor_number)
    monitor_refresh_rate = pr.get_monitor_refresh_rate(monitor_number)
    return monitor_number, monitor_width, monitor_height, monitor_refresh_rate


def set_and_position_window(position_x, position_y, width, height) -> None:
    pr.set_window_size(width, height)
    pr.set_window_position(position_x, position_y)


def get_monitor_pointer(monitor_number: int):
    monitor_count_c_int = pr.ffi.new("int *")
    monitor_list = pr.glfw_get_monitors(monitor_count_c_int)
    monitor_pointer = monitor_list[monitor_number]
    return monitor_pointer


def set_window_monitor_glfw(monitor_number: int | None,
                            position_x: int,
                            position_y: int,
                            width: int,
                            height: int,
                            refresh_rate: int):

    window_pointer = pr.get_window_handle()

    if monitor_number is not None:
        monitor_pointer = get_monitor_pointer(monitor_number=monitor_number)
    else:
        monitor_pointer = None

    pr.glfw_set_window_monitor(window_pointer,
                               monitor_pointer,
                               position_x,
                               position_y,
                               width,
                               height,
                               refresh_rate)


def set_fullscreen_glfw(monitor_number, width, height, refresh_rate):
    set_window_monitor_glfw(monitor_number=monitor_number,
                            position_x=0,
                            position_y=0,
                            width=width,
                            height=height,
                            refresh_rate=refresh_rate)


def set_windowed_glfw(position_x, position_y, width, height, refresh_rate):
    set_window_monitor_glfw(monitor_number=None,
                            position_x=position_x,
                            position_y=position_y,
                            width=width,
                            height=height,
                            refresh_rate=refresh_rate)


def get_window_position() -> tuple[int, int]:
    position = pr.get_window_position()
    window_position_x: int = int(position.x)
    window_position_y: int = int(position.y)
    return window_position_x, window_position_y


def get_window_size() -> tuple[int, int]:
    window_width: int = pr.get_screen_width()
    window_height: int = pr.get_screen_height()
    return window_width, window_height


def get_window_position_and_size() -> tuple[int, int, int, int]:
    window_position_x, window_position_y = get_window_position()
    window_width, window_height = get_window_size()
    return window_position_x, window_position_y, window_width, window_height


def get_window_aspect_ratio() -> float:
    current_window_width, current_window_height = get_window_size()
    window_aspect_ratio: float = current_window_width / current_window_height
    return window_aspect_ratio


class Window:
    def __init__(self) -> None:
        self._is_fullscreen: bool = False
        self._restore_position_and_size: tuple[int, int, int, int] = get_window_position_and_size()

    def toggle_fullscreen(self) -> None:
        current_monitor_size_and_refresh = get_monitor_mode()

        if self._is_fullscreen:
            arguments = self._restore_position_and_size + current_monitor_size_and_refresh[3:]
            set_windowed_glfw(*arguments)
        else:
            self._restore_position_and_size = get_window_position_and_size()
            set_fullscreen_glfw(*current_monitor_size_and_refresh)

        self._is_fullscreen = not self._is_fullscreen

    @staticmethod
    def close() -> None:
        pr.glfw_set_window_should_close(pr.get_window_handle(), True)
