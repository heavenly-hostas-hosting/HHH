# from js import console
from pyscript import when, document

shortcuts_dict = dict()

# I have commented the stuff related to logs as it was only for debug
# def log(*msgs):
#     [console.log(msg) for msg in msgs]

# log('LOG WORKING')


def handle_toggle(elem, data: list[str]) -> None:
    btn_dict = {btn.innerText: btn for btn in elem.children}

    for d in data:
        key, value = d.split(":")
        action = btn_dict[value].click
        shortcuts_dict[key] = action


def handle_btn(elem, data: list[str]) -> None:
    action = elem.click
    key = data[0]

    shortcuts_dict[key] = action


for elem in document.getElementsByClassName("keyboard-shortcuts"):
    data = elem.getAttribute("shortcut_data").split(",")
    if not data:
        # log("No shortcut data found")
        continue
    if data[0] == 'toggle':
        handle_toggle(elem, data[1:])
        continue
    if data[0] == 'btn':
        handle_btn(elem, data[1:])
        continue

    # log("Invalid shortcut data format")


@when("keydown", "body")
def handle_keydown(event):
    if event.repeat:        # runs only once when same key is pressed more than once or held down
        return
    # log('some key pressed')
    action = shortcuts_dict.get(event.key, None)
    if action:
        # log('action found for key:', event.key)
        action()
    # else:
        # log('no action found for key:', event.key)


