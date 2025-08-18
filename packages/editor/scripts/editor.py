# This should be under the other imports but because it isn't imported in the traditional way, it's above them.
from canvas_ctx import CanvasContext, ImageBitmap  # pyright: ignore[reportMissingImports]

# Following imports have the ignore flag as they are not pip installed
from js import (  # pyright: ignore[reportMissingImports]
    Event,
    Image,
    ImageData,
    KeyboardEvent,
    Math,
    MouseEvent,
    Object,
    createImageBitmap,
    document,
    localStorage,
    window,
)
from pyodide.ffi import create_proxy  # pyright: ignore[reportMissingImports]
from pyscript import when  # pyright: ignore[reportMissingImports]

canvas = document.getElementById("image-canvas")
buffer = document.getElementById("buffer-canvas")
text_input = document.getElementById("text-input")

bold_input = document.getElementById("bold-text")
italics_input = document.getElementById("italics-text")
font_family_input = document.getElementById("text-font-family").querySelector("input")

settings = Object()
settings.willReadFrequently = True

ctx: CanvasContext = canvas.getContext("2d", settings)
buffer_ctx: CanvasContext = buffer.getContext("2d", settings)

canvas.style.imageRendering = "pixelated"
canvas.style.imageRendering = "crisp-edges"

buffer.style.imageRendering = "pixelated"
buffer.style.imageRendering = "crisp-edges"

# Settings properties of the canvas.
display_height = window.innerHeight * 0.95  # 95vh
display_width = display_height * (2**0.5)  # Same ratio as an A4 sheet of paper

ctx.scaled_by = 2  # Better resolution

canvas.style.height = f"{display_height}px"
canvas.style.width = f"{display_width}px"

canvas.height = display_height * ctx.scaled_by
canvas.width = display_width * ctx.scaled_by

buffer.style.height = f"{display_height}px"
buffer.style.width = f"{display_width}px"

buffer.height = display_height * ctx.scaled_by
buffer.width = display_width * ctx.scaled_by


ctx.imageSmoothingEnabled = False
ctx.strokeStyle = "black"
ctx.lineWidth = 5
ctx.lineCap = "round"
ctx.lineJoin = "round"
ctx.font = "50px Arial"

# Custom attributes attached so we don't need to use global vars
ctx.drawing = False
ctx.action = "pen"
ctx.type = "smooth"
ctx.bounding_rect = canvas.getBoundingClientRect()
ctx.current_img = Image.new()
ctx.moving_image = False
ctx.writing_text = False
ctx.text_placed = True
ctx.prev_operation = "source-over"
ctx.text_settings = {"bold": False, "italics": False, "size": 50, "font-family": "Arial"}
ctx.clipping = False
ctx.moving_clip = False
ctx.start_coords = [0, 0]
ctx.prev_stroke_style = "black"
ctx.prev_line_width = 5
ctx.size_change = 0
ctx.rotation = 0
ctx.is_rotating = False
ctx.current_position = [0, 0]


buffer_ctx.imageSmoothingEnabled = False
buffer_ctx.strokeStyle = "black"
buffer_ctx.lineWidth = 5
buffer_ctx.lineCap = "round"
buffer_ctx.lineJoin = "round"
buffer_ctx.font = f"{ctx.text_settings['size']}px {ctx.text_settings['font-family']}"

ctx.history = []
ctx.history_index = -1
MAX_HISTORY = 50
MIN_RESIZE_SIZE = 20
MAX_RESIZE_SIZE = 200
ROTATION_SPEED = 3

PIXEL_SIZE = 8
SMUDGE_BLEND_FACTOR = 0.5


def save_history() -> None:
    """Save the historical data."""
    ctx.history = ctx.history[: ctx.history_index + 1]
    if len(ctx.history) >= MAX_HISTORY:
        ctx.history.pop(0)
        ctx.history_index -= 1

    ctx.history.append(ctx.getImageData(0, 0, canvas.width, canvas.height))
    ctx.history_index += 1
    save_change_to_browser()


def save_change_to_browser() -> None:
    """Save change to browser storage."""
    localStorage.setItem("cj12-hhh-image-data", canvas.toDataURL("image/webp"))
    localStorage.setItem("cj12-hhh-drawing-mode", ctx.type)


@when("click", "#undo-button")
def undo(_: Event) -> None:
    """Undo history."""
    if ctx.history_index <= 0:
        return
    ctx.history_index -= 1

    def place_history(img_bitmap: ImageBitmap) -> None:
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.prev_operation = ctx.globalCompositeOperation
        ctx.globalCompositeOperation = "source-over"
        ctx.drawImage(img_bitmap, 0, 0, canvas.width, canvas.height)
        ctx.globalCompositeOperation = ctx.prev_operation
        localStorage.setItem("cj12-hhh-image-data", canvas.toDataURL("image/webp"))
        localStorage.setItem("cj12-hhh-drawing-mode", ctx.type)

    createImageBitmap(ctx.history[ctx.history_index]).then(place_history)


@when("click", "#redo-button")
def redo(_: Event) -> None:
    """Redo history."""
    if ctx.history_index >= len(ctx.history) - 1:
        return
    ctx.history_index += 1

    def place_history(img_bitmap: ImageBitmap) -> None:
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.prev_operation = ctx.globalCompositeOperation
        ctx.globalCompositeOperation = "source-over"
        ctx.drawImage(img_bitmap, 0, 0, canvas.width, canvas.height)
        ctx.globalCompositeOperation = ctx.prev_operation
        localStorage.setItem("cj12-hhh-image-data", canvas.toDataURL("image/webp"))
        localStorage.setItem("cj12-hhh-drawing-mode", ctx.type)

    createImageBitmap(ctx.history[ctx.history_index]).then(place_history)


def draw_pixel(x: float, y: float) -> None:
    """Draws the pixel on the canvas.

    Args:
        x (float): X coordinate
        y (float): Y coordinate

    """
    ctx.fillStyle = ctx.strokeStyle
    ctx.fillRect(x - PIXEL_SIZE // 2, y - PIXEL_SIZE // 2, PIXEL_SIZE, PIXEL_SIZE)


def show_action_icon(x: float, y: float) -> bool:
    """Show icon to let user know what the action would look like.

    Args:
        x (float): X coordinate
        y (float): Y coordinate

    Returns:
        bool: If True is returned mousemove doesn't do anything else

    """

    def draw_clip(img_bitmap: ImageBitmap) -> None:
        buffer_ctx.clearRect(0, 0, canvas.width, canvas.height)

        buffer_ctx.translate(
            x,
            y,
        )
        buffer_ctx.rotate(ctx.rotation)
        ratio = img_bitmap.width / img_bitmap.height

        if img_bitmap.width < img_bitmap.height:
            buffer_ctx.strokeRect(
                -(img_bitmap.width + ctx.size_change) / 2,
                -(img_bitmap.height + ctx.size_change * ratio) / 2,
                img_bitmap.width + ctx.size_change,
                img_bitmap.height + ctx.size_change * ratio,
            )
            buffer_ctx.drawImage(
                img_bitmap,
                -(img_bitmap.width + ctx.size_change) / 2,
                -(img_bitmap.height + ctx.size_change * ratio) / 2,
                img_bitmap.width + ctx.size_change,
                img_bitmap.height + ctx.size_change * ratio,
            )
        else:
            buffer_ctx.strokeRect(
                -(img_bitmap.width + ctx.size_change * ratio) / 2,
                -(img_bitmap.height + ctx.size_change) / 2,
                img_bitmap.width + ctx.size_change * ratio,
                img_bitmap.height + ctx.size_change,
            )
            buffer_ctx.drawImage(
                img_bitmap,
                -(img_bitmap.width + ctx.size_change * ratio) / 2,
                -(img_bitmap.height + ctx.size_change) / 2,
                img_bitmap.width + ctx.size_change * ratio,
                img_bitmap.height + ctx.size_change,
            )
        buffer_ctx.rotate(-ctx.rotation)
        buffer_ctx.translate(
            -x,
            -y,
        )

    if ctx.moving_clip:
        createImageBitmap(ctx.prev_data).then(draw_clip)
        return True
    buffer_ctx.clearRect(0, 0, canvas.width, canvas.height)
    if ctx.moving_image:
        buffer_ctx.translate(
            x,
            y,
        )
        buffer_ctx.rotate(ctx.rotation)
        ratio = ctx.current_img.width / ctx.current_img.height
        if ctx.current_img.width < ctx.current_img.height:
            buffer_ctx.drawImage(
                ctx.current_img,
                -(ctx.current_img.width + ctx.size_change) / 2,
                -(ctx.current_img.height + ctx.size_change * ratio) / 2,
                ctx.current_img.width + ctx.size_change,
                ctx.current_img.height + ctx.size_change * ratio,
            )
        else:
            buffer_ctx.drawImage(
                ctx.current_img,
                -(ctx.current_img.width + ctx.size_change * ratio) / 2,
                -(ctx.current_img.height + ctx.size_change) / 2,
                ctx.current_img.width + ctx.size_change * ratio,
                ctx.current_img.height + ctx.size_change,
            )

        buffer_ctx.rotate(-ctx.rotation)
        buffer_ctx.translate(
            -x,
            -y,
        )
        return True
    if ctx.writing_text and not ctx.text_placed:
        buffer_ctx.translate(
            x,
            y,
        )
        buffer_ctx.rotate(ctx.rotation)
        text_dimensions = ctx.measureText(ctx.text_value)
        buffer_ctx.fillText(
            ctx.text_value,
            -text_dimensions.width / 2,
            (text_dimensions.actualBoundingBoxAscent + text_dimensions.actualBoundingBoxDescent) / 2,
        )
        buffer_ctx.rotate(-ctx.rotation)
        buffer_ctx.translate(
            -x,
            -y,
        )
        return True
    if ctx.clipping:
        buffer_ctx.strokeRect(
            ctx.start_coords[0],
            ctx.start_coords[1],
            x - ctx.start_coords[0],
            y - ctx.start_coords[1],
        )
        return True
    regular_icon_show(x, y)
    return False


def regular_icon_show(x: float, y: float) -> None:
    """Show preview for regular actions.

    Args:
        x (float): X coordinate
        y (float): Y coordinate

    """
    if ctx.type == "smooth":
        buffer_ctx.beginPath()
        buffer_ctx.arc(x, y, ctx.lineWidth / 2, 0, 2 * Math.PI)  # Put a dot here
        if ctx.action == "pen":
            buffer_ctx.fill()
        elif ctx.action == "eraser":
            prev_width = buffer_ctx.lineWidth
            prev_fill = buffer_ctx.fillStyle
            buffer_ctx.lineWidth = ctx.scaled_by
            buffer_ctx.fillStyle = "white"
            buffer_ctx.fill()
            buffer_ctx.arc(x, y, ctx.lineWidth / 2, 0, 2 * Math.PI)
            buffer_ctx.stroke()
            buffer_ctx.lineWidth = prev_width
            buffer_ctx.fillStyle = prev_fill


def get_smudge_data(x: float, y: float) -> ImageData:
    """Get the smudge data around the xy for smudgeing."""
    smudge_size = ctx.lineWidth

    return ctx.getImageData(
        x - (smudge_size // 2),
        y - (smudge_size // 2),
        smudge_size,
        smudge_size,
    )


def put_smudge_data(x: float, y: float) -> None:
    """Put the smudge data around the xy for smudgeing."""
    smudge_size = ctx.lineWidth

    ctx.putImageData(
        ctx.smudge_data,
        x - (smudge_size // 2),
        y - (smudge_size // 2),
    )


def update_smudge_data(x: float, y: float) -> None:
    """Update the smudge data around the xy for smudgeing."""
    ctx.smudge_data = get_smudge_data(x, y)
    ctx.last_x = x
    ctx.last_y = y


def draw_smudge(event: MouseEvent) -> None:
    """Draws the smudge data on the canvas.

    Args:
        event (MouseEvent): The javascript mouse event

    """
    x, y = get_canvas_coords(event)
    # draw the pevious smudge data at the current xy.
    put_smudge_data(x, y)

    update_smudge_data(x, y)


def get_canvas_coords(event: MouseEvent) -> tuple[float, float]:
    """Give the canvas coordinates.

    Args:
        event (MouseEvent): The mouse event

    Returns:
        tuple[float, float]: The x and y coordinates

    """
    x = (event.pageX - ctx.bounding_rect.left) * ctx.scaled_by
    y = (event.pageY - ctx.bounding_rect.top) * ctx.scaled_by
    if ctx.type == "pixel":
        x = (int(x) + 5) // 10 * 10
        y = (int(y) + 5) // 10 * 10
    return (x, y)


@when("mousedown", "#image-canvas")
def start_path(event: MouseEvent) -> None:
    """Start drawing the path.

    Args:
        event (MouseEvent): The mouse event

    """
    if event.button != 0:
        return

    if ctx.moving_image:
        return

    ctx.drawing = True

    x, y = get_canvas_coords(event)
    if ctx.action == "smudge":
        update_smudge_data(x, y)
    elif ctx.type == "smooth":
        x, y = get_canvas_coords(event)
        ctx.beginPath()
        ctx.moveTo(x, y)


@when("mousemove", "#image-canvas")
def mouse_tracker(event: MouseEvent) -> None:
    """Draw the path following the mouse.

    Args:
        event (MouseEvent): The mouse event

    """
    x, y = get_canvas_coords(event)
    ctx.current_position = [x, y]
    if show_action_icon(x, y):
        return
    if not ctx.text_placed:
        text_dimensions = ctx.measureText(ctx.text_value)

        buffer_ctx.fillText(
            ctx.text_value,
            x - text_dimensions.width / 2,
            y + (text_dimensions.actualBoundingBoxAscent + text_dimensions.actualBoundingBoxDescent) / 2,
        )
    if ctx.writing_text:
        return
    if not ctx.drawing:
        return
    draw_action(event, x, y)


def draw_action(event: MouseEvent, x: float, y: float) -> None:
    """Draw the event on the screen.

    Args:
        event (MouseEvent): Mouse event
        x (float): X coordinate
        y (float): Y coordinate

    """
    match ctx.type:
        case "smooth":
            if ctx.action == "smudge":
                draw_smudge(event)
            elif ctx.action in ("pen", "eraser"):  # this is "pen" or "eraser"
                ctx.lineTo(x, y)
                ctx.stroke()
        case "pixel":
            if ctx.action == "pen":
                draw_pixel(x, y)
            elif ctx.action == "eraser":
                ctx.clearRect(x - PIXEL_SIZE // 2, y - PIXEL_SIZE // 2, PIXEL_SIZE, PIXEL_SIZE)


@when("mouseup", "body")
def stop_path(_: MouseEvent) -> None:
    """Stop drawing path.

    Args:
        event (MouseEvent): The mouse event

    """
    if ctx.drawing and not ctx.clipping:
        ctx.drawing = False
        save_history()


@when("mouseup", "body")
def drop_media(event: MouseEvent) -> None:
    """Place text or clipping.

    Args:
        event (MouseEvent): Mouse event

    """
    if ctx.text_placed:
        ctx.writing_text = False
    if ctx.clipping:
        ctx.clipping = False
        ctx.moving_clip = True
        x, y = get_canvas_coords(event)
        ctx.prev_data = ctx.getImageData(
            ctx.start_coords[0],
            ctx.start_coords[1],
            x - ctx.start_coords[0],
            y - ctx.start_coords[1],
        )
        ctx.clearRect(
            ctx.start_coords[0],
            ctx.start_coords[1],
            x - ctx.start_coords[0],
            y - ctx.start_coords[1],
        )


@when("mouseenter", "#image-canvas")
def start_reentry_path(event: MouseEvent) -> None:
    """Start a new path from the edge upon canvas entry.

    Args:
        event (MouseEvent): Mouse event

    """
    if ctx.drawing:
        x, y = get_canvas_coords(event)
        ctx.beginPath()
        ctx.moveTo(x, y)


@when("mouseout", "#image-canvas")
def leaves_canvas(event: MouseEvent) -> None:
    """Handle mouse leaving canvas.

    Args:
        event (MouseEvent): The mouse event

    """
    if not ctx.drawing or ctx.clipping:
        return
    if ctx.type == "smooth" and ctx.action != "smudge":  # "pen" or "eraser"
        x, y = get_canvas_coords(event)
        ctx.lineTo(x, y)
        ctx.stroke()


@when("mousedown", "#image-canvas")
def canvas_click(event: MouseEvent) -> None:
    """Handle mouse clicking canvas.

    Args:
        event (MouseEvent): The mouse event

    """
    if event.button != 0:
        return
    x, y = get_canvas_coords(event)
    if special_actions(x, y):
        return
    if ctx.type == "smooth":
        if ctx.action == "clip" and not ctx.moving_clip:
            ctx.clipping = True
            ctx.start_coords = [x, y]
            ctx.setLineDash([2, 10])
            buffer_ctx.setLineDash([2, 10])
            ctx.prev_stroke_style = ctx.strokeStyle
            ctx.prev_line_width = ctx.lineWidth

            ctx.strokeStyle = "black"
            ctx.lineWidth = 5
            buffer_ctx.strokeStyle = "black"
            buffer_ctx.lineWidth = 5
        else:
            ctx.beginPath()
            ctx.ellipse(x, y, ctx.lineWidth / 100, ctx.lineWidth / 100, 0, 0, 2 * Math.PI)  # Put a dot here
            if ctx.action in ("pen", "eraser"):
                ctx.stroke()
    elif ctx.type == "pixel":
        if ctx.action == "pen":
            draw_pixel(x, y)
        elif ctx.action == "eraser":
            ctx.clearRect(x - PIXEL_SIZE // 2, y - PIXEL_SIZE // 2, PIXEL_SIZE, PIXEL_SIZE)


def special_actions(x: float, y: float) -> bool:
    """Draw special action on canvas.

    Args:
        x (float): X coordinate
        y (float): Y coordinate

    Returns:
        bool: Whether to skip the regular drawing process or not

    """
    if ctx.moving_image:
        draw_image(x, y)

        return True
    if ctx.writing_text:
        ctx.text_placed = True
        buffer_ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.translate(
            x,
            y,
        )
        ctx.rotate(ctx.rotation)
        text_dimensions = ctx.measureText(ctx.text_value)

        ctx.fillText(
            ctx.text_value,
            -text_dimensions.width / 2,
            (text_dimensions.actualBoundingBoxAscent + text_dimensions.actualBoundingBoxDescent) / 2,
        )
        ctx.globalCompositeOperation = ctx.prev_operation

        ctx.rotate(-ctx.rotation)
        ctx.translate(
            -x,
            -y,
        )

        ctx.rotation = 0
        return True

    if ctx.moving_clip:
        ctx.moving_clip = False

        def draw_clip(img_bitmap: ImageBitmap) -> None:
            buffer_ctx.clearRect(0, 0, canvas.width, canvas.height)
            ctx.translate(
                x,
                y,
            )
            ctx.rotate(ctx.rotation)
            ratio = img_bitmap.width / img_bitmap.height

            if img_bitmap.width < img_bitmap.height:
                ctx.drawImage(
                    img_bitmap,
                    -(img_bitmap.width + ctx.size_change) / 2,
                    -(img_bitmap.height + ctx.size_change * ratio) / 2,
                    img_bitmap.width + ctx.size_change,
                    img_bitmap.height + ctx.size_change * ratio,
                )
            else:
                ctx.drawImage(
                    img_bitmap,
                    -(img_bitmap.width + ctx.size_change * ratio) / 2,
                    -(img_bitmap.height + ctx.size_change) / 2,
                    img_bitmap.width + ctx.size_change * ratio,
                    img_bitmap.height + ctx.size_change,
                )

            ctx.size_change = 0

            ctx.rotate(-ctx.rotation)
            ctx.translate(
                -x,
                -y,
            )
            ctx.rotation = 0

        createImageBitmap(ctx.prev_data).then(draw_clip)
        ctx.setLineDash([])
        buffer_ctx.setLineDash([])
        ctx.strokeStyle = ctx.prev_stroke_style
        ctx.lineWidth = ctx.prev_line_width

        buffer_ctx.strokeStyle = ctx.prev_stroke_style
        buffer_ctx.lineWidth = ctx.prev_line_width

        return True
    return False


def draw_image(x: float, y: float) -> None:
    """Draws the uploaded image to the canvas.

    Args:
        x (float): X coordinate
        y (float): Y coordinate

    """
    ctx.moving_image = False
    buffer_ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.translate(
        x,
        y,
    )
    ctx.rotate(ctx.rotation)
    ratio = ctx.current_img.width / ctx.current_img.height
    if ctx.current_img.width < ctx.current_img.height:
        ctx.drawImage(
            ctx.current_img,
            -(ctx.current_img.width + ctx.size_change) / 2,
            -(ctx.current_img.height + ctx.size_change * ratio) / 2,
            ctx.current_img.width + ctx.size_change,
            ctx.current_img.height + ctx.size_change * ratio,
        )
    else:
        ctx.drawImage(
            ctx.current_img,
            -(ctx.current_img.width + ctx.size_change * ratio) / 2,
            -(ctx.current_img.height + ctx.size_change) / 2,
            ctx.current_img.width + ctx.size_change * ratio,
            ctx.current_img.height + ctx.size_change,
        )
    ctx.globalCompositeOperation = ctx.prev_operation
    ctx.size_change = 0
    ctx.rotate(-ctx.rotation)
    ctx.translate(
        -x,
        -y,
    )
    ctx.rotation = 0
    save_history()


@when("colourChange", "body")
def colour_change(_: Event) -> None:
    """Handle colour change.

    Args:
        _ (Event): Change event

    """
    ctx.strokeStyle = window.pen.colour
    ctx.fillStyle = window.pen.colour
    buffer_ctx.strokeStyle = window.pen.colour
    buffer_ctx.fillStyle = window.pen.colour


@when("change", ".width-input")
def width_change(event: Event) -> None:
    """Handle colour change.

    Args:
        event (Event): Change event

    """
    ctx.lineWidth = int(event.target.getAttribute("aria-valuenow"))
    buffer_ctx.lineWidth = ctx.lineWidth


@when("change", "#action-select")
def action_change(event: Event) -> None:
    """Handle action change from `pen` to `eraser` or vice versa.

    Args:
        event (Event): Change event

    """
    ctx.action = event.target.getAttribute("value")
    match ctx.action:
        case "pen":
            ctx.globalCompositeOperation = "source-over"
        case "eraser":
            ctx.globalCompositeOperation = "destination-out"
        case "smudge":
            ctx.globalCompositeOperation = "source-over"
        case "clip":
            ctx.globalCompositeOperation = "source-over"


@when("addText", "#text-input")
def add_text(_: Event) -> None:
    """Add text to canvas.

    Args:
        _ (Event): Add text event

    """
    ctx.text_value = text_input.value
    if ctx.text_value:
        ctx.writing_text = True
        ctx.text_placed = False
        ctx.prev_operation = ctx.globalCompositeOperation
        ctx.globalCompositeOperation = "source-over"
        ctx.text_settings["bold"] = "bold" if bold_input.getAttribute("aria-checked") == "true" else "normal"
        ctx.text_settings["italics"] = "italic" if italics_input.getAttribute("aria-checked") == "true" else "normal"
        ctx.text_settings["font-family"] = font_family_input.value
        # I know it's too long but it doesn't work otherwise
        ctx.font = f"{ctx.text_settings['italics']} {ctx.text_settings['bold']} {ctx.text_settings['size']}px {ctx.text_settings['font-family']}"  # noqa: E501
        buffer_ctx.font = f"{ctx.text_settings['italics']} {ctx.text_settings['bold']} {ctx.text_settings['size']}px {ctx.text_settings['font-family']}"  # noqa: E501


@when("change", "#type-select")
def type_change(event: Event) -> None:
    """Handle type change.

    Args:
        event (Event): Change event

    """
    ctx.type = event.target.getAttribute("value")
    if ctx.type == "smooth":
        ctx.imageSmoothingEnabled = True
        ctx.scaled_by = 2
    elif ctx.type == "pixel":
        ctx.imageSmoothingEnabled = False
        ctx.scaled_by = 0.5
        buffer_ctx.clearRect(0, 0, canvas.width, canvas.height)

    resize(event, keep_content=False)

    # As far as I know there's no way to check when we change from pixel to smooth in the history so there's
    # no way to switch the modes in the UI. Hence I've decided to just clear the history instead.
    ctx.history.clear()
    ctx.history_index = 0
    save_history()


@when("reset", "body")
def reset_board(_: Event) -> None:
    """Reset the canvas.

    Args:
        _ (Event): Reset event

    """
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    save_history()


@when("click", "#download-button")
def download_image(_: Event) -> None:
    """Download the canvas content as an image.

    Args:
        _ (Event): Click event

    """
    link = document.createElement("a")
    link.download = "download.webp"
    link.href = canvas.toDataURL()
    link.click()
    link.remove()


@when("change", "#file-upload")
def upload_image(e: Event) -> None:
    """Handle image upload.

    Args:
        e (Event): Upload event

    """
    ctx.prev_operation = ctx.globalCompositeOperation
    ctx.globalCompositeOperation = "source-over"
    ctx.prev_data = ctx.getImageData(0, 0, canvas.width, canvas.height)
    ctx.current_img.src = e.target.src
    ctx.moving_image = True


@create_proxy
def resize(_: Event, keep_content: dict | bool = True) -> None:  # noqa: FBT001, FBT002 keep_content has to be a positional arg
    """Resize canvas according to window.

    Args:
        _ (Event): Resize event
        keep_content (bool): Flag to keep the existing content. It's technically not a dict. It's an Object,
                            but I can't type hint with it.

    """
    data = ctx.getImageData(0, 0, canvas.width, canvas.height)
    line_width = ctx.lineWidth
    stroke_style = ctx.strokeStyle
    font = ctx.font
    global_composite_operation = ctx.globalCompositeOperation
    display_height = window.innerHeight * 0.95

    display_width = display_height * (2**0.5)

    canvas.style.height = f"{display_height}px"
    canvas.style.width = f"{display_width}px"

    canvas.height = display_height * ctx.scaled_by
    canvas.width = display_width * ctx.scaled_by
    ctx.bounding_rect = canvas.getBoundingClientRect()

    if isinstance(keep_content, bool):
        if keep_content:
            createImageBitmap(data).then(
                lambda img_bitmap: ctx.drawImage(img_bitmap, 0, 0, canvas.width, canvas.height),
            )
    # I don't know why but keep_content is an object sometimes
    elif keep_content.keep_content:  # pyright: ignore[reportAttributeAccessIssue]
        createImageBitmap(data).then(
            lambda img_bitmap: ctx.drawImage(img_bitmap, 0, 0, canvas.width, canvas.height),
        )

    ctx.lineWidth = line_width
    ctx.strokeStyle = stroke_style
    ctx.fillStyle = stroke_style

    ctx.imageSmoothingEnabled = False
    ctx.lineCap = "round"
    ctx.lineJoin = "round"
    ctx.font = font
    ctx.globalCompositeOperation = global_composite_operation

    buffer.style.height = f"{display_height}px"
    buffer.style.width = f"{display_width}px"

    buffer.height = display_height * ctx.scaled_by
    buffer.width = display_width * ctx.scaled_by

    buffer_ctx.imageSmoothingEnabled = False
    buffer_ctx.strokeStyle = stroke_style
    buffer_ctx.lineWidth = line_width
    buffer_ctx.fillStyle = stroke_style
    buffer_ctx.lineCap = "round"
    buffer_ctx.lineJoin = "round"
    buffer_ctx.font = font


@create_proxy
def handle_scroll(e: Event) -> None:
    """Handle scrolling on the canvas. Used to increase/decrease the size of images/text etc.

    Args:
        e (Event): Scroll event

    """
    e.preventDefault()
    x, y = get_canvas_coords(e)
    if ctx.writing_text:
        # ctx.text_settings["size"] is an int
        if e.deltaY > 0 and ctx.text_settings["size"] > MIN_RESIZE_SIZE:  # pyright: ignore[reportOperatorIssue]
            ctx.text_settings["size"] -= 5  # pyright: ignore[reportOperatorIssue]
        elif e.deltaY < 0 and ctx.text_settings["size"] < MAX_RESIZE_SIZE:  # pyright: ignore[reportOperatorIssue]
            ctx.text_settings["size"] += 5  # pyright: ignore[reportOperatorIssue]
        ctx.font = f"{ctx.text_settings['italics']} {ctx.text_settings['bold']} {ctx.text_settings['size']}px {ctx.text_settings['font-family']}"  # noqa: E501
        buffer_ctx.font = f"{ctx.text_settings['italics']} {ctx.text_settings['bold']} {ctx.text_settings['size']}px {ctx.text_settings['font-family']}"  # noqa: E501
        show_action_icon(x, y)
    elif ctx.moving_image:
        if (
            e.deltaY > 0
            and min(ctx.current_img.width + ctx.size_change, ctx.current_img.height + ctx.size_change)
            > MIN_RESIZE_SIZE
        ):
            ctx.size_change -= 10
        elif (
            e.deltaY < 0
            and max(ctx.current_img.width + ctx.size_change, ctx.current_img.height + ctx.size_change)
            < MAX_RESIZE_SIZE * 100
        ):
            ctx.size_change += 10
        show_action_icon(x, y)
    elif ctx.moving_clip:
        if (
            e.deltaY > 0
            and min(ctx.prev_data.width + ctx.size_change, ctx.prev_data.height + ctx.size_change) > MIN_RESIZE_SIZE
        ):
            ctx.size_change -= 10
        elif (
            e.deltaY < 0
            and max(ctx.prev_data.width + ctx.size_change, ctx.prev_data.height + ctx.size_change)
            < MAX_RESIZE_SIZE * 100
        ):
            ctx.size_change += 10
        show_action_icon(x, y)


@create_proxy
def keydown_event(event: KeyboardEvent) -> None:
    """Handle keydown events.

    Args:
        event (KeyboardEvent): Keydown event

    """
    if event.key == "Backspace":
        if ctx.moving_image:
            ctx.moving_image = False
            ctx.globalCompositeOperation = ctx.prev_operation
            ctx.size_change = 0
        elif ctx.moving_clip:
            ctx.moving_clip = False
            ctx.setLineDash([])
            buffer_ctx.setLineDash([])
            ctx.strokeStyle = ctx.prev_stroke_style
            ctx.lineWidth = ctx.prev_line_width

            buffer_ctx.strokeStyle = ctx.prev_stroke_style
            buffer_ctx.lineWidth = ctx.prev_line_width
        elif ctx.writing_text:
            ctx.writing_text = False
            ctx.text_placed = True
            ctx.globalCompositeOperation = ctx.prev_operation
        show_action_icon(ctx.current_position[0], ctx.current_position[1])
    elif event.key == "Alt":
        ctx.is_rotating = True
    elif event.key == "ArrowLeft" and ctx.is_rotating and (ctx.moving_image or ctx.moving_clip or ctx.writing_text):
        ctx.rotation -= Math.PI / 180 * ROTATION_SPEED
        show_action_icon(ctx.current_position[0], ctx.current_position[1])
    elif event.key == "ArrowRight" and ctx.is_rotating and (ctx.moving_image or ctx.moving_clip or ctx.writing_text):
        ctx.rotation += Math.PI / 180 * ROTATION_SPEED
        show_action_icon(ctx.current_position[0], ctx.current_position[1])


@create_proxy
def keyup_event(event: KeyboardEvent) -> None:
    """Handle keyup event.

    Args:
        event (KeyboardEvent): Keyup event

    """
    if event.key == "Alt":
        ctx.is_rotating = False


@create_proxy
def load_image(event: Event = None) -> None:
    """Load image from the browser storage."""
    data_url = localStorage.getItem("cj12-hhh-image-data")
    drawing_mode = localStorage.getItem("cj12-hhh-drawing-mode")
    if data_url:
        if drawing_mode == "pixel":
            ctx.type = "pixel"
            ctx.imageSmoothingEnabled = False
            ctx.scaled_by = 0.5
        saved_canvas_data = Image.new()
        saved_canvas_data.src = data_url
        saved_canvas_data.addEventListener(
            "load",
            create_proxy(
                lambda _: ctx.drawImage(saved_canvas_data, 0, 0, canvas.width, canvas.height),
            ),
        )
        if drawing_mode == "pixel":
            resize(event)


if document.readyState == "loading":
    window.addEventListener("DOMContentLoaded", load_image)
else:
    load_image()


window.addEventListener("resize", resize)

ctx.current_img.addEventListener("load", resize)

document.addEventListener("keydown", keydown_event)
document.addEventListener("keyup", keyup_event)

# The wheel event is for most browsers. The mousewheel event is deprecated
# but the wheel event is not supported by Safari and Webviewer on iOS.
canvas.addEventListener("wheel", handle_scroll)
canvas.addEventListener("mousewheel", handle_scroll)

save_history()
