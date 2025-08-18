import asyncio
import base64
import pathlib
import random

from nicegui import app, ui
from nicegui.client import Client
from nicegui.events import UploadEventArguments, ValueChangeEventArguments

SPIN_COUNT = 10

HEX = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]


action_options = {"pen": "🖊️", "eraser": "🧽", "smudge": "💨", "clip": "📎"}
# I really don't want to do this but I don't know how else to achieve it
global_vars = {
    "type_programatically_changed": False,
}

app.add_static_files("/scripts", pathlib.Path(__file__).parent / "scripts")
app.add_static_files("/static", pathlib.Path(__file__).parent / "static")


@ui.page("/", response_timeout=10)
async def index(client: Client) -> None:  # noqa: C901, PLR0915 All of the below lines need to be in this function for private viewing of the page
    """Index page for the editor."""

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
                ui.button("Clear", on_click=lambda: (do_reset(mode_value=mode_value), dialog.close())).props(
                    "color='red'",
                )
        dialog.open()

    def revert_type() -> None:
        """Revert the type change when cancel is clicked."""
        global_vars["type_programatically_changed"] = True
        type_toggle.set_visibility(False)
        type_toggle.value = "smooth" if type_toggle.value == "pixel" else "pixel"
        type_toggle.update()
        type_toggle.set_visibility(True)
        global_vars["type_programatically_changed"] = False

    def handle_type_change(dialog: ui.dialog, *, mode_value: bool) -> None:
        """Handle type change."""
        dialog.close()
        do_reset(mode_value=mode_value)
        action_toggle.set_value("pen")
        if type_toggle.value == "smooth":
            width_input.enable()
            width_slider.enable()
            file_uploader.enable()
            text_input.enable()
            add_text_button.enable()
            bold_checkbox.enable()
            italics_checkbox.enable()
            font_family.enable()
        elif type_toggle.value == "pixel":
            width_input.disable()
            width_slider.disable()
            file_uploader.disable()
            text_input.disable()
            add_text_button.disable()
            bold_checkbox.disable()
            italics_checkbox.disable()
            font_family.disable()

    def change_type(*, mode_value: bool = False) -> None:
        """Prompt user to reset canvas."""
        if global_vars["type_programatically_changed"]:
            return
        with ui.dialog() as dialog, ui.card():
            ui.label(
                """
                Are you sure you want to change the drawing mode? This will clear the canvas.
                You will not be able to undo this.
                """,
            ).style("text-align: center;")
            with ui.row().style("display: flex; justify-content: space-between; width: 100%;"):
                ui.button(
                    "Cancel",
                    on_click=lambda: (
                        dialog.close(),
                        revert_type(),
                    ),
                )
                ui.button(
                    "Change",
                    on_click=lambda: handle_type_change(dialog, mode_value=mode_value),
                ).props(
                    "color='red'",
                )
        dialog.open()

    def reset() -> None:
        """Reset canvas."""
        ui.run_javascript("""
            const event = new Event('reset');
            document.body.dispatchEvent(event);
        """)

    async def spin() -> None:
        """Change RGB values."""
        hex_value = ""
        for x in range(SPIN_COUNT):
            for y in range(3):
                text = random.choice(HEX) + random.choice(HEX)  # noqa: S311 This isn't for cryptography
                colour_values[y].text = text
                if x == SPIN_COUNT - 1:
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
            let event = new Event("change");
            const fileUpload = document.querySelector("#file-upload");
            fileUpload.src = "data:{e.type};base64,{content}";
            fileUpload.dispatchEvent(event);
        """)
        # e.sender is the file upload element which has a .reset() method
        e.sender.reset()  # type: ignore  # noqa: PGH003

    def switch_action(e: ValueChangeEventArguments) -> None:
        """Fire switch action event."""
        if type_toggle.value == "pixel" and e.value in ("smudge", "clip"):
            action_toggle.value = "pen"
            ui.notify("You cannot select the smudge or select action while in pixel mode.", type="negative")
            return
        ui.run_javascript(f"""
            const event = new Event('change');
            const actionSelect = document.querySelector("#action-select");
            actionSelect.setAttribute("value", "{e.value}");
            actionSelect.dispatchEvent(event);
        """)

    def show_help_menu() -> None:
        """Show help modal."""
        with ui.dialog() as dialog, ui.card():
            with ui.card_section():
                ui.markdown(
                    """
                    There are keybinds for the editor actions.
                    """,
                )
                with ui.list().props("dense separator"):
                    ui.item("p: Select pen (🖊️) mode.")
                    ui.item("e: Select eraser (🧽) mode.")
                    ui.item("s: Select smudge (💨) mode.")
                    ui.item("c: Select clip (📎) mode.")
                    ui.item("z: Spin a new colour.")
                    ui.item("u: Undo.")
                    ui.item("?: Show this help menu.")
                ui.markdown(
                    """
                    To add images to the canvas, upload one via the file upload, and then click where you want to add
                    it on the canvas.
                    """,
                )
                ui.markdown(
                    """
                    To add text to the canvas, type in the text input and click the `Add to canvas` button. You can
                    set the text to be bolded or italicised. You can also select the font from the dropdown.
                    """,
                )
                ui.markdown(
                    """
                    Clipped regions, images, and text can all be resized and rotated. They can be resized using the
                    scroll wheel or similar. They can be rotated by holding `Alt` and then pressing the
                    left or right arrow key.
                    """,
                )
                ui.markdown(
                    """
                    You can switch between the smooth (✍️) or pixel (👾) modes using the toggle below.
                    """,
                )
            ui.button(
                "Close",
                on_click=dialog.close,
            )
        dialog.open()

    def show_registration_menu() -> None:
        with ui.dialog() as dialog, ui.card():
            with ui.card_section():
                with ui.column():
                    ui.html(
                        """
                        <p>To register you must have a GitHub account.</p>
                        <p>
                            <small>If you don't have a GitHub account yet, you can create one <a href="https://github.com/signup">here</a>.</small>
                        </p>
                        <p>
                            <small>Already registered? <a href="https://github.com/login">Log In instead</a>.</small>
                        </p>
                        <br>
                        <p>Follow these steps to complete registration:</p>

                        <ol>
                            <li>
                                Go to
                                <a href="https://github.com/heavenly-hostas-hosting/HHH">
                                    https://github.com/heavenly-hostas-hosting/HHH
                                </a> and create a fork of the repository.
                            </li>
                            <li>
                                Head over to
                                <a href="https://github.com/apps/pydis-cj12-heavenly-hostas-app/installations/new">
                                    the app installation link
                                </a> to
                                authorize and install our GitHub app, make sure to only select the repository you
                                forked.
                            </li>
                            <li>You can now Sign in with GitHub.</li>
                        </ol>
                        """
                    ).classes("registration-menu")
                    ui.space()
                    ui.separator().classes("w-full")
                    ui.space()
                    ui.label("Step By Step Reference Images")
                    with ui.expansion("Forking The Repository").classes("w-full"):
                        ui.image("/static/forking-1.png")
                        ui.image("/static/forking-2.png")
                    with ui.expansion("Installing The Application").classes("w-full"):
                        ui.image("/static/installing-app.png")

            ui.button(
                "Close",
                on_click=dialog.close,
            )
        dialog.open()

    async def publish() -> None:
        """Fetch the API and publish the canvas."""
        ui.notify("Publishing...")
        try:
            response_ok = await ui.run_javascript(
                """
                const format = "image/webp";
                const quality = 0.7;  // 70%

                const canvas = document.querySelector("#image-canvas");
                const blob = await new Promise((r) => canvas.toBlob(r, format, quality));

                if (blob === null) {
                    return false;
                }

                // Use FormData so FastAPI can read it as UploadFile
                const form = new FormData();
                form.append("image", blob, "canvas.webp");

                response = await fetch(
                    "/api/publish",
                    {
                        method: "POST",
                        body: form,
                    },
                ).catch((e) => console.error(e));

                return response.ok;
                """,
                timeout=300,
            )

            if not response_ok:
                ui.notify("Failed to publish!", type="negative")
                return

            ui.notify("Artwork published successfully!", type="positive")

        except Exception as e:  # noqa: BLE001
            ui.notify(f"An error occurred: {e}", type="negative")

    async def login() -> None:
        """Fetch the API and login."""
        ui.notify("Logging in...")
        try:
            await ui.run_javascript(
                """
                const redirectUrl = "/api/login";
                window.location.href = redirectUrl;

                sessionStorage.setItem("cj12-hhh-logged-in", "true");
                """,
                timeout=60,
            )

            ui.notify("Logged in successfully!", type="positive")

            register_button.move(hidden_buttons)
            login_button.move(hidden_buttons)

            publish_button.move(shown_buttons)
            logout_button.move(shown_buttons)

        except Exception as e:
            ui.notify(f"An error occurred: {e}", type="negative")

    async def logout() -> None:
        """Fetch the API and logout."""
        ui.notify("Logging out...")
        try:
            await ui.run_javascript(
                """
                const redirectUrl = "/api/logout";
                window.location.href = redirectUrl;

                sessionStorage.setItem("cj12-hhh-logged-in", "false");
                """,
                timeout=60,
            )

            ui.notify("Logged out successfully!", type="positive")

            register_button.move(shown_buttons)
            login_button.move(shown_buttons)

            publish_button.move(hidden_buttons)
            logout_button.move(hidden_buttons)

        except Exception as e:
            ui.notify(f"An error occurred: {e}", type="negative")

    async def check_login_status() -> None:
        try:
            response = await ui.run_javascript(
                """
                response = await fetch(
                    "/api/status",
                    { method: "GET" },
                ).catch((e) => console.error(e));

                response_json = response.json();

                sessionStorage.setItem("cj12-hhh-logged-in", response_json['logged_in']);

                return response_json;
                """,
                timeout=60,
            )

            # if not response.ok:
            #     ui.notify("Failed to check status!", type="negative")
            #     return

            if response["logged_in"]:
                username.set_text(response["username"])
                register_button.move(hidden_buttons)
                login_button.move(hidden_buttons)

                publish_button.move(shown_buttons)
                logout_button.move(shown_buttons)
            else:
                username.set_text("")
                register_button.move(shown_buttons)
                login_button.move(shown_buttons)

                publish_button.move(hidden_buttons)
                logout_button.move(hidden_buttons)
                # ui.notify("You were logged out. Please login again.")

        except Exception as e:
            ui.notify(f"An error occurred: {e}", type="negative")

    ui.add_head_html("""
        <link rel="stylesheet" href="https://pyscript.net/releases/2024.1.1/core.css">
        <script type="module" src="https://pyscript.net/releases/2024.1.1/core.js"></script>
        <style>
            #loading {
                outline: none;
                border: none;
                background: transparent;
            }

            .registration-menu a {
                color: blue;
                text-decoration: underline;
            }

            .registration-menu li {
                list-style-type: decimal;
            }
        </style>
        <script type="module">
            const loading = document.getElementById('loading');
            addEventListener('py:ready', () => loading.close());
            loading.showModal();

            window.onload = () => {emitEvent('content_loaded');};
        </script>
    """)

    ui.add_body_html("""
        <dialog id="loading">
                <h1>Loading...</h1>
        </dialog>
    """)

    ui.element("img").props("id='file-upload'").style("display: none;")

    with ui.row().style("display: flex; width: 100%;"):
        # Page controls
        with ui.column().style("flex-grow: 1; flex-basis: 0;"):
            username = ui.label("")
            ui.separator().classes("w-full")
            with ui.row():
                dark = ui.dark_mode()
                ui.switch("Dark mode").bind_value(dark)
                ui.button(icon="help", on_click=lambda: show_help_menu()).props(
                    "class='keyboard-shortcuts' shortcut_data='btn,?'",
                )
            ui.button("Clear Canvas", on_click=reset_confirmation).props("color='red'")
            ui.button("Download").props("id='download-button'")
            file_uploader = (
                ui.upload(
                    label="Upload file",
                    auto_upload=True,
                    on_upload=upload_image,
                    on_rejected=lambda _: ui.notify("There was an issue with the upload."),
                )
                .props("accept='image/*' id='file-input'")
                .style("width: 100%;")
            )
            type_toggle = ui.toggle(
                {"smooth": "✍️", "pixel": "👾"},
                value="smooth",
                on_change=lambda e: change_type(mode_value=e.value),
            ).props("id='type-select'")

            with ui.row().props("id='shown-buttons'") as shown_buttons:
                register_button = ui.button("Register", on_click=show_registration_menu)
                login_button = ui.button("Login", on_click=login)
            with ui.row().props("id='hidden-buttons'").style("display: none") as hidden_buttons:
                publish_button = ui.button("Publish", on_click=publish)
                logout_button = ui.button("Logout", on_click=logout)

        with ui.element("div").style("position: relative;"):
            ui.element("canvas").props("id='image-canvas'").style(
                "border: 1px solid black; background-color: white;",
            )
            ui.element("canvas").props("id='buffer-canvas'").style(
                "pointer-events: none; position: absolute; top: 0; left: 0;",
            )

        # Canvas controls
        with ui.column().style("flex-grow: 1; flex-basis: 0;"):
            with ui.row():
                ui.button("Undo").props("id='undo-button' class='keyboard-shortcuts' shortcut_data='btn,u'")
                ui.button("Redo").props("id='redo-button' class='keyboard-shortcuts' shortcut_data='btn,r'")

            action_toggle = ui.toggle(
                action_options,
                value="pen",
                on_change=switch_action,
            ).props(
                "id='action-select' class='keyboard-shortcuts' shortcut_data='toggle,p:🖊️,e:🧽,s:💨,c:📎'",
            )
            ui.separator().classes("w-full")
            with ui.row():
                colour_values = []
                for colour in ["R", "G", "B"]:
                    with ui.column().style("align-items: center;"):
                        ui.label(colour)
                        colour_label = ui.label("00")
                        colour_values.append(colour_label)
            ui.button("Spin", on_click=spin).props("class='keyboard-shortcuts' shortcut_data='btn,z'")
            ui.separator().classes("w-full")
            width_input = ui.number(label="Line Width", min=1, max=100, step=1)
            width_slider = ui.slider(
                min=1,
                max=100,
                value=1,
                on_change=lambda _: ui.run_javascript("""
                    const event = new Event('change');
                    document.querySelector(".width-input").dispatchEvent(event);
                    """),
            ).classes("width-input")
            width_input.bind_value(width_slider)
            ui.separator().classes("w-full")
            text_input = ui.input(
                label="Text",
                placeholder="Start typing",
            ).props("id='text-input'")
            with ui.row():
                bold_checkbox = ui.checkbox("Bold").props("id='bold-text'")
                italics_checkbox = ui.checkbox("Italics").props("id='italics-text'")
            with ui.row():
                font_family = ui.select(
                    [
                        "Arial",
                        "Verdana",
                        "Tahoma",
                        "Trebuchet MS",
                        "Times New Roman",
                        "Georgia",
                        "Garamond",
                        "Courier New",
                        "Brush Script MT",
                    ],
                    value="Arial",
                ).props("id='text-font-family'")
                add_text_button = ui.button(
                    "Add to canvas",
                    on_click=lambda: (
                        ui.run_javascript("""
                        const event = new Event("addText");
                        document.querySelector("#text-input").dispatchEvent(event);
                    """),
                        text_input.set_value(""),
                    ),
                )

    ui.add_body_html("""
        <py-config>
            [[fetch]]
            from = "/scripts/"
            files = ["canvas_ctx.py", "editor.py", "shortcuts.py"]
        </py-config>
        <script type="py" src="/scripts/editor.py"></script>
        <script type="py" src="/scripts/shortcuts.py"></script>
    """)

    await client.connected()
    drawing_mode = await ui.run_javascript("return localStorage.getItem('cj12-hhh-drawing-mode');")
    if drawing_mode == "pixel":
        revert_type()
        width_input.disable()
        width_slider.disable()
        file_uploader.disable()
        text_input.disable()
        add_text_button.disable()
        bold_checkbox.disable()
        italics_checkbox.disable()
        font_family.disable()

    logged_in = await ui.run_javascript("return sessionStorage.getItem('cj12-hhh-logged-in');")
    if logged_in == "true":
        register_button.move(hidden_buttons)
        login_button.move(hidden_buttons)

        publish_button.move(shown_buttons)
        logout_button.move(shown_buttons)

    ui.on("content_loaded", check_login_status)
    ui.timer(5.0, check_login_status)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=9010, title="HHH Editor", root_path="/editor")
