import asyncio
import base64
import pathlib
import random

from nicegui import app, ui
from nicegui.events import UploadEventArguments, ValueChangeEventArguments

app.add_static_files("/scripts", pathlib.Path(__file__).parent / "scripts")

ui.add_head_html("""
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>
                 <style>
        #loading { outline: none; border: none; background: transparent }
    </style>
    <script type="module">
        const loading = document.getElementById('loading');
        addEventListener('py:ready', () => loading.close());
        loading.showModal();
    </script>
""")

ui.add_body_html("""
    <dialog id="loading">
            <h1>Loading...</h1>
    </dialog>
""")


def do_reset(*, mode_value: bool) -> None:
    """Reset the canvas."""
    if mode_value:
        ui.run_javascript(f"""
            const event = new Event('change');
            const typeSelect = document.querySelector("#type-select");
            typeSelect.setAttribute("value", "{mode_value}");
            typeSelect.dispatchEvent(event);
            """)
    reset()


def reset_confirmation(*, mode_value: bool = False) -> None:
    """Prompt user to reset canvas."""
    with ui.dialog() as dialog, ui.card():
        ui.label("Are you sure you want to clear the canvas?")
        with ui.row().style("display: flex; justify-content: space-between; width: 100%;"):
            ui.button("Cancel", on_click=lambda: dialog.close())
            ui.button("Clear", on_click=lambda: (do_reset(mode_value=mode_value), dialog.close())).props("color='red'")
    dialog.open()


def reset() -> None:
    """Reset canvas."""
    ui.run_javascript("""
        const event = new Event('reset');
        document.body.dispatchEvent(event);
    """)


Hex = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]


async def spin() -> None:
    """Change RGB values."""
    hex_value = ""
    for x in range(10):
        for y in range(3):
            text = random.choice(Hex) + random.choice(Hex)  # noqa: S311
            colour_values[y].text = text
            if x == 9:  # noqa: PLR2004
                hex_value += text
        await asyncio.sleep(0.1)
    ui.run_javascript(f"""
        window.pen = window.pen || {{}};
        window.pen.colour = "#{hex_value}";
        const event = new Event('colourChange');
        document.body.dispatchEvent(event);
    """)


def upload_image(e: UploadEventArguments) -> None:
    """Fire upload event."""
    ui.notify(f"Uploaded {e.name}")
    content = base64.b64encode(e.content.read()).decode("utf-8")
    ui.run_javascript(f"""
        const event = new Event("change");
        const fileUpload = document.querySelector("#file-upload");
        fileUpload.src = "data:{e.type};base64,{content}"
        fileUpload.dispatchEvent(event);
    """)


def switch_action(e: ValueChangeEventArguments):
    ui.run_javascript(f"""
    const event = new Event('change');
    const actionSelect = document.querySelector("#action-select");
    actionSelect.setAttribute("value", "{e.value}");
    actionSelect.dispatchEvent(event);
    """)


ui.element("img").props("id='file-upload'").style("display: none;")

with ui.row().style("display: flex; width: 100%;"):
    # Page controls
    with ui.column().style("flex-grow: 1; flex-basis: 0;"):
        dark = ui.dark_mode()
        ui.switch("Dark mode").bind_value(dark)
        ui.button("Clear Canvas", on_click=reset_confirmation).props("color='red'")
        ui.button("Download").props("id='download-button'")
        ui.upload(
            label="Upload file",
            on_upload=upload_image,
            on_rejected=lambda _: ui.notify("There was an issue with the upload."),
        ).classes(
            "max-w-full",
        ).props("accept='image/*' id='file-input'")
        ui.toggle(
            {"smooth": "✍️", "pixel": "👾"},
            value="smooth",
            on_change=lambda e: reset_confirmation(mode_value=e.value),
        ).props("id='type-select'")

    ui.element("canvas").props("id='image-canvas'").style(
        "border: 1px solid black; background-color: white;",
    )

    # Canvas controls
    with ui.column().style("flex-grow: 1; flex-basis: 0;"):
        ui.toggle(
            {"pen": "🖊️", "eraser": "🧽"},
            value="pen",
            on_change=switch_action,
        ).props(
            "id='action-select'",
        )
        ui.separator().classes("w-full")
        with ui.row():
            colour_values = []
            for colour in ["R", "G", "B"]:
                with ui.column().style("align-items: center;"):
                    ui.label(colour)
                    colour_label = ui.label("00")
                    colour_values.append(colour_label)
        ui.button("Spin", on_click=spin)
        ui.separator().classes("w-full")
        width_input = ui.number(label="Line Width", min=1, max=50, step=1)
        width_slider = ui.slider(
            min=1,
            max=50,
            value=5,
            on_change=lambda _: ui.run_javascript("""
                const event = new Event('change');
                document.querySelector(".width-input").dispatchEvent(event);
                """),
        ).classes("width-input")
        width_input.bind_value(width_slider)

ui.add_body_html("""
    <py-config>
        [[fetch]]
        from = "/scripts/"
        files = ["canvas_ctx.py", "editor.py"]
    </py-config>
    <script type="py" src="/scripts/editor.py"></script>
""")

ui.run()
