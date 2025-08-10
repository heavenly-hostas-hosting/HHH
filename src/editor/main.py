from nicegui import app, ui

app.add_static_files("/scripts", "scripts")


ui.add_head_html("""
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>
""")

ui.add_body_html("""
    <div id="canvas-container">
        <canvas id="image-canvas" style="border: 1px solid black;"></canvas>
    </div>
    <script type="py" src="/scripts/editor.py"></script>
""")

ui.run()
