from .window import get_window_aspect_ratio


class FOVY:
    def __init__(self, minimum_vertical_units: float, minimum_horizontal_units: float) -> None:
        self._minimum_vertical_units: float = minimum_vertical_units
        self._minimum_horizontal_units: float = minimum_horizontal_units

    def correct_for_aspect_ratio(self) -> float:
        window_aspect_ratio: float = get_window_aspect_ratio()
        vertical_fovy: float = self._minimum_vertical_units
        horizontal_fovy: float = self._minimum_horizontal_units / window_aspect_ratio
        greatest_fovy: float = max(vertical_fovy, horizontal_fovy)
        return greatest_fovy
