# Following imports have the ignore flag as they are not pip installed
from canvas_ctx import CanvasContext
from js import (  # pyright: ignore[reportMissingImports]
    Event,
    Image,
    ImageData,
    Math,
    MouseEvent,
    Object,
    document,
    window,
)
from pyodide.ffi import create_proxy  # pyright: ignore[reportMissingImports]
from pyscript import when  # pyright: ignore[reportMissingImports]

canvas = document.getElementById("image-canvas")
buffer = document.getElementById("buffer-canvas")

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

# Custom attributes attached so we don't need to use global vars
ctx.drawing = False
ctx.action = "pen"
ctx.type = "smooth"
ctx.bounding_rect = canvas.getBoundingClientRect()
ctx.current_img = Image.new()
ctx.moving_image = False
ctx.prev_operation = "source-over"


buffer_ctx.imageSmoothingEnabled = False
buffer_ctx.strokeStyle = "black"
buffer_ctx.lineWidth = 5
buffer_ctx.lineCap = "round"
buffer_ctx.lineJoin = "round"


PIXEL_SIZE = 8
SMUDGE_BLEND_FACTOR = 0.5


def draw_pixel(x: float, y: float) -> None:
    """Draws the pixel on the canvas.

    Args:
        x (float): X coordinate
        y (float): Y coordinate
    """
    ctx.fillStyle = ctx.strokeStyle
    ctx.fillRect(x - PIXEL_SIZE // 2, y - PIXEL_SIZE // 2, PIXEL_SIZE, PIXEL_SIZE)


def show_action_icon(x: float, y: float) -> None:
    """Show icon to let user know what the action would look like.

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

    buffer_ctx.clearRect(0, 0, canvas.width, canvas.height)
    if ctx.moving_image:
        buffer_ctx.drawImage(ctx.current_img, x - ctx.current_img.width / 2, y - ctx.current_img.height / 2)
        return
    show_action_icon(x, y)
    if not ctx.drawing:
        return

    match ctx.type:
        case "smooth":
            if ctx.action == "smudge":
                draw_smudge(event)

            else:  # this is "pen" or "eraser"
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
    if ctx.drawing:
        ctx.drawing = False


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
    if not ctx.drawing:
        return
    if ctx.type == "smooth" and ctx.action != "smudge":  # "pen" or "eraser"
        x, y = get_canvas_coords(event)
        ctx.lineTo(x, y)
        ctx.stroke()

    ctx.drawing = False
    ctx.smudge_data = None


@when("mousedown", "#image-canvas")
def canvas_click(event: MouseEvent) -> None:
    """Handle mouse clicking canvas.

    Args:
        event (MouseEvent): The mouse event
    """
    if event.button != 0:
        return
    x, y = get_canvas_coords(event)

    if ctx.moving_image:
        ctx.moving_image = False
        buffer_ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(ctx.current_img, x - ctx.current_img.width / 2, y - ctx.current_img.height / 2)
        ctx.globalCompositeOperation = ctx.prev_operation
    elif ctx.type == "smooth":
        ctx.beginPath()
        ctx.ellipse(x, y, ctx.lineWidth / 100, ctx.lineWidth / 100, 0, 0, 2 * Math.PI)  # Put a dot here
        if ctx.action in ("pen", "eraser"):
            ctx.stroke()
    elif ctx.type == "pixel":
        if ctx.action == "pen":
            draw_pixel(x, y)
        elif ctx.action == "eraser":
            ctx.clearRect(x - PIXEL_SIZE // 2, y - PIXEL_SIZE // 2, PIXEL_SIZE, PIXEL_SIZE)


@when("colourChange", "body")
def colour_change(_: Event) -> None:
    """Handle colour change.

    Args:
        _ (Event): Change event
    """
    ctx.strokeStyle = window.pen.colour
    buffer_ctx.strokeStyle = window.pen.colour


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
    resize(event)


@when("reset", "body")
def reset_board(_: Event) -> None:
    """Reset the canvas.

    Args:
        _ (Event): Reset event
    """
    line_width = ctx.lineWidth
    stroke_style = ctx.strokeStyle
    global_composite_operation = ctx.globalCompositeOperation
    ctx.reset()
    ctx.lineWidth = line_width
    ctx.strokeStyle = stroke_style
    ctx.lineCap = "round"
    ctx.lineJoin = "round"
    ctx.globalCompositeOperation = global_composite_operation


@when("click", "#download-button")
def download_image(_: Event) -> None:
    """Download the canvas content as an image.

    Args:
        _ (Event): Click event
    """
    link = document.createElement("a")
    link.download = "download.avif"
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
def resize(_: Event) -> None:
    """Resize canvas according to window.

    Args:
        _ (Event): Resize event
    """
    data = ctx.getImageData(0, 0, canvas.width, canvas.height)
    line_width = ctx.lineWidth
    stroke_style = ctx.strokeStyle
    global_composite_operation = ctx.globalCompositeOperation
    display_height = window.innerHeight * 0.95

    display_width = display_height * (2**0.5)

    canvas.style.height = f"{display_height}px"
    canvas.style.width = f"{display_width}px"

    canvas.height = display_height * ctx.scaled_by
    canvas.width = display_width * ctx.scaled_by

    ctx.bounding_rect = canvas.getBoundingClientRect()
    ctx.putImageData(data, 0, 0)

    ctx.lineWidth = line_width
    ctx.strokeStyle = stroke_style

    ctx.lineCap = "round"
    ctx.lineJoin = "round"
    ctx.globalCompositeOperation = global_composite_operation


window.addEventListener("resize", resize)

ctx.current_img.onload = resize
