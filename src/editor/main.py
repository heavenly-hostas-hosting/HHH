from nicegui import app, ui
from nicegui.events import ValueChangeEventArguments

app.add_static_files("/scripts", "scripts")


def handle_colour_change(_: ValueChangeEventArguments) -> None:
    """Handle colour change.

    Args:
        _ (ValueChangeEventArguments): Change event

    """
    ui.run_javascript("""
        var event = new Event('change');
        document.querySelector(".colour-picker div div div input").dispatchEvent(event);
        """)


ui.add_head_html("""
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>
""")

picker = ui.color_input(
    label="Color",
    value="#000000",
    on_change=handle_colour_change,
).classes("colour-picker")


ui.add_body_html("""
    <div id="canvas-container">
        <canvas id="image-canvas" style="border: 1px solid black;"></canvas>
    </div>
    <script type="py" src="/scripts/editor.py" defer></script>
""")

ui.run()
