import pyray as pr


def is_one_pressed() -> bool:
    is_one_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_ONE)
    return is_one_pressed_


def is_two_pressed() -> bool:
    is_two_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_TWO)
    return is_two_pressed_


def is_three_pressed() -> bool:
    is_three_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_THREE)
    return is_three_pressed_


def is_f_pressed() -> bool:
    is_f_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_F)
    return is_f_pressed_


def is_p_pressed() -> bool:
    is_p_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_P)
    return is_p_pressed_


def is_q_pressed() -> bool:
    is_q_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_Q)
    return is_q_pressed_


def is_backspace_pressed() -> bool:
    is_backspace_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_BACKSPACE)
    return is_backspace_pressed_


def is_enter_pressed() -> bool:
    is_enter_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_ENTER)
    return is_enter_pressed_


def is_space_pressed() -> bool:
    is_space_pressed_: bool = pr.is_key_pressed(pr.KeyboardKey.KEY_SPACE)
    return is_space_pressed_


def is_a_down() -> bool:
    is_a_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_A)
    return is_a_down_


def is_d_down() -> bool:
    is_d_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_D)
    return is_d_down_


def is_e_down() -> bool:
    is_e_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_E)
    return is_e_down_


def is_q_down() -> bool:
    is_q_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_Q)
    return is_q_down_


def is_s_down() -> bool:
    is_s_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_S)
    return is_s_down_


def is_w_down() -> bool:
    is_w_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_W)
    return is_w_down_


def is_left_shift_down() -> bool:
    is_left_shift_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_SHIFT)
    return is_left_shift_down_


def is_left_ctrl_down() -> bool:
    is_left_ctrl_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL)
    return is_left_ctrl_down_


def is_left_alt_down() -> bool:
    is_left_alt_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_ALT)
    return is_left_alt_down_


def is_right_alt_down() -> bool:
    is_right_alt_down_: bool = pr.is_key_down(pr.KeyboardKey.KEY_RIGHT_ALT)
    return is_right_alt_down_


def is_left_ctrl_and_left_shift_down() -> bool:
    return is_left_ctrl_down() or is_left_shift_down()


def is_left_or_right_alt_down() -> bool:
    return is_left_alt_down() or is_right_alt_down()


def is_left_ctrl_down_and_q_pressed() -> bool:
    return is_left_ctrl_down() and is_q_pressed()


def is_left_or_right_alt_down_and_enter_pressed() -> bool:
    return is_left_or_right_alt_down() and is_enter_pressed()


def is_left_ctrl_and_left_shift_down_and_p_pressed() -> bool:
    return is_left_ctrl_and_left_shift_down() and is_p_pressed()
