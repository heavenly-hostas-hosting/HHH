import asyncio
import pathlib
import random

from nicegui import app, ui

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


def reset_confirmation() -> None:
    """Prompt user to reset canvas."""
    with ui.dialog() as dialog, ui.card():
        ui.label("Are you sure you want to reset?")
        with ui.row().style("display: flex; justify-content: space-between; width: 100%;"):
            ui.button("Cancel", on_click=lambda: dialog.close())
            ui.button("Reset", on_click=lambda: (reset(), dialog.close())).props("color='red'")
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


with ui.row().style("display: flex; width: 100%; justify-content: space-between;"):
    # Left side contains page controls
    with ui.column().style("flex-grow: 1; flex-basis: 0;"):
        dark = ui.dark_mode()
        ui.switch("Dark mode").bind_value(dark)
        ui.button("Reset", on_click=lambda _: reset_confirmation()).props("color='red'")

    ui.element("canvas").props("id='image-canvas'").style("border: 1px solid black; background-color: white;")

    # Right side contains canvas controls
    with ui.column().style("flex-grow: 1; flex-basis: 0;"):
        ui.toggle(
            {"pen": "🖊️", "eraser": "🧽"},
            value="pen",
            on_change=lambda e: ui.run_javascript(f"""
                const event = new Event('change');
                const actionSelect = document.querySelector("#action-select");
                actionSelect.setAttribute("value", "{e.value}");
                actionSelect.dispatchEvent(event);
                """),
        ).props("id='action-select'")
        with ui.row():
            colour_values = []
            for colour in ["R", "G", "B"]:
                with ui.column().style("align-items: center;"):
                    ui.label(colour)
                    colour_label = ui.label("00")
                    colour_values.append(colour_label)
        ui.button("Spin", on_click=spin)
        ui.label("Line width")
        ui.slider(
            min=1,
            max=50,
            value=5,
            on_change=lambda _: ui.run_javascript("""
                const event = new Event('change');
                document.querySelector(".width-input").dispatchEvent(event);
                """),
        ).classes("width-input")


ui.add_body_html("""
    <script type="py" src="/scripts/editor.py" defer></script>
""")

ui.run()
