import pyray as pr

from vector_tompy.vector2 import Vector2, Vector2Injector


class Cursor:
    def __init__(self) -> None:
        self._current: Vector2 = self.position()
        self._previous: Vector2 = self.position()
        self._idle_time: float = 0.0
        self._idle_time_hiding_threshold: float = 5.0
        self._is_hidden: bool = False

    @staticmethod
    def position() -> Vector2:
        mouse_position = pr.get_mouse_position()
        position_: Vector2 = Vector2Injector.from_number(x=mouse_position.x, y=mouse_position.y)
        return position_

    def update(self) -> None:
        self._previous = self._current
        self._current: Vector2 = self.position()

        is_position_same: bool = self._current == self._previous

        if is_position_same:
            self._idle_time += pr.get_frame_time()

            is_time_to_hide: bool = self._idle_time >= self._idle_time_hiding_threshold

            if is_time_to_hide and not self._is_hidden:
                self.hide()
        else:
            self._idle_time = 0.0

            if self._is_hidden:
                self.show()

    def show(self) -> None:
        self._is_hidden = False
        pr.show_cursor()

    def hide(self) -> None:
        self._is_hidden = True
        pr.hide_cursor()
