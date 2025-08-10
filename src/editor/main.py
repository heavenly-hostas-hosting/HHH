from nicegui import app, ui

app.add_static_files("/scripts", "scripts")


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

with ui.row():
    with ui.column():
        dark = ui.dark_mode()
        ui.switch("Dark mode").bind_value(dark)
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

        ui.color_input(
            label="Color",
            value="#000000",
            on_change=lambda _: ui.run_javascript("""
                const event = new Event('change');
                document.querySelector(".colour-picker div div div input").dispatchEvent(event);
                """),
        ).classes("colour-picker")

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

    ui.element("canvas").props("id='image-canvas'").style("border: 1px solid black; background-color: white;")

ui.add_body_html("""
    <script type="py" src="/scripts/editor.py" defer></script>
""")

ui.run()
