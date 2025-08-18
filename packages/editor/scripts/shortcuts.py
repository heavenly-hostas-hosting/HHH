# Disable missing imports as Pyscript is loaded at runtime
from js import Element, KeyboardEvent  # pyright: ignore[reportMissingImports]
from pyscript import document, when  # pyright: ignore[reportMissingImports]

shortcuts_dict = {}
text_input = document.getElementById("text-input")


def handle_toggle(elem: Element, data: list[str]) -> None:
    """Add elements to dictionary.

    Args:
        elem (Element): Toggle element
        data (list[str]): Keybind data

    """
    btn_dict = {btn.innerText: btn for btn in elem.children}

    for d in data:
        key, value = d.split(":")
        action = btn_dict[value].click
        shortcuts_dict[key] = action


def handle_btn(elem: Element, data: list[str]) -> None:
    """Add elements to dictionary.

    Args:
        elem (Element): Button element
        data (list[str]): Keybind data

    """
    action = elem.click
    key = data[0]

    shortcuts_dict[key] = action


for elem in document.getElementsByClassName("keyboard-shortcuts"):
    data = elem.getAttribute("shortcut_data").split(",")
    if not data:
        continue
    if data[0] == "toggle":
        handle_toggle(elem, data[1:])
        continue
    if data[0] == "btn":
        handle_btn(elem, data[1:])
        continue


@when("keydown", "body")
def handle_keydown(event: KeyboardEvent) -> None:
    """Switch action when keybind is pressed.

    Args:
        event (KeyboardEvent): Keydown event

    """
    # Disable keybinds when writing text
    if event.target == text_input:
        return
    if event.repeat:  # runs only once when same key is pressed more than once or held down
        return
    action = shortcuts_dict.get(event.key, None)
    if action:
        action()
