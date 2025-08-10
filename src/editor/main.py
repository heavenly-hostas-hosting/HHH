from nicegui import app, ui

app.add_static_files("/scripts", "scripts")


ui.add_head_html("""
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>
""")

ui.color_input(
    label="Color",
    value="#000000",
    on_change=lambda _: ui.run_javascript("""
        var event = new Event('change');
        document.querySelector(".colour-picker div div div input").dispatchEvent(event);
        """),
).classes("colour-picker")

ui.label("Line width")
ui.slider(
    min=1,
    max=20,
    value=5,
    on_change=lambda _: ui.run_javascript("""
        var event = new Event('change');
        document.querySelector(".width-input").dispatchEvent(event);
        """),
).classes("width-input")


ui.add_body_html("""
    <div id="canvas-container">
        <canvas id="image-canvas" style="border: 1px solid black;"></canvas>
    </div>
    <script type="py" src="/scripts/editor.py" defer></script>
""")

ui.run()
