import base64

# Following imports have the ignore flag as they are not pip installed
from js import (  # pyright: ignore[reportMissingImports]
    Event,
    FileReader,
    Image,
    Math,
    MouseEvent,
    Object,
    document,
    window,
)
from pyodide.ffi import create_proxy  # pyright: ignore[reportMissingImports]
from pyscript import when  # pyright: ignore[reportMissingImports]

canvas = document.getElementById("image-canvas")

settings = Object()
settings.willReadFrequently = True

ctx = canvas.getContext("2d", settings)

display_height = window.innerHeight * 0.95  # 95vh
display_width = display_height * (2**0.5)  # Same ratio as an A4 sheet of paper

SCALE = 2  # Better resolution

canvas.style.height = f"{display_height}px"
canvas.style.width = f"{display_width}px"

canvas.height = display_height * SCALE
canvas.width = display_width * SCALE

ctx.strokeStyle = "black"
ctx.lineWidth = 5
ctx.lineCap = "round"
ctx.lineJoin = "round"

ctx.drawing = False
ctx.action = "pen"
ctx.rect = canvas.getBoundingClientRect()


def get_canvas_coords(event: MouseEvent) -> tuple[float, float]:
    """Give the canvas coordinates.

    Args:
        event (MouseEvent): The mouse event

    Returns:
        tuple[float, float]: The x and y coordinates

    """
    x = (event.pageX - ctx.rect.left) * SCALE
    y = (event.pageY - ctx.rect.top) * SCALE
    return (x, y)


@when("mousedown", "#image-canvas")
def start_path(event: MouseEvent) -> None:
    """Start drawing the path.

    Args:
        event (MouseEvent): The mouse event

    """
    if event.button != 0:
        return
    ctx.drawing = True
    x, y = get_canvas_coords(event)
    ctx.beginPath()
    ctx.moveTo(x, y)


@when("mousemove", "#image-canvas")
def mouse_tracker(event: MouseEvent) -> None:
    """Draw the path following the mouse.

    Args:
        event (MouseEvent): The mouse event

    """
    if not ctx.drawing:
        return
    x, y = get_canvas_coords(event)
    ctx.lineTo(x, y)
    ctx.stroke()


@when("mouseup", "#image-canvas")
def stop_path(_: MouseEvent) -> None:
    """Stop drawing path.

    Args:
        event (MouseEvent): The mouse event

    """
    if not ctx.drawing:
        return
    ctx.drawing = False


@when("mouseout", "#image-canvas")
def leaves_canvas(event: MouseEvent) -> None:
    """Handle mouse leaving canvas.

    Args:
        event (MouseEvent): The mouse event

    """
    if not ctx.drawing:
        return
    x, y = get_canvas_coords(event)
    ctx.lineTo(x, y)
    ctx.stroke()  # Draws the line to the point on the edge where the mouse leaves the canvas
    ctx.drawing = False


@when("click", "#image-canvas")
def canvas_click(event: MouseEvent) -> None:
    """Handle mouse clicking canvas.

    Args:
        event (MouseEvent): The mouse event

    """
    if event.button != 0:
        return
    x, y = get_canvas_coords(event)
    ctx.beginPath()
    ctx.ellipse(x, y, ctx.lineWidth / 100, ctx.lineWidth / 100, 0, 0, 2 * Math.PI)  # Put a dot here
    if ctx.action == "pen":
        ctx.stroke()
    elif ctx.action == "eraser":
        ctx.fill()


@when("colourChange", "body")
def colour_change(_: Event) -> None:
    """Handle colour change.

    Args:
        _ (Event): Change event

    """
    ctx.strokeStyle = window.pen.colour


@when("change", ".width-input")
def width_change(event: Event) -> None:
    """Handle colour change.

    Args:
        event (Event): Change event

    """
    ctx.lineWidth = int(event.target.getAttribute("aria-valuenow"))


@when("change", "#action-select")
def action_change(event: Event) -> None:
    """Handle action change.

    Args:
        event (Event): Change event

    """
    ctx.action = event.target.getAttribute("value")
    if ctx.action == "pen":
        ctx.globalCompositeOperation = "source-over"
    else:
        ctx.globalCompositeOperation = "destination-out"


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
    img = Image.new()
    img.onload = lambda _: ctx.drawImage(img, 0, 0)
    img.src = e.target.src


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

    canvas.height = display_height * SCALE
    canvas.width = display_width * SCALE

    ctx.rect = canvas.getBoundingClientRect()
    ctx.putImageData(data, 0, 0)

    ctx.lineWidth = line_width
    ctx.strokeStyle = stroke_style

    ctx.lineCap = "round"
    ctx.lineJoin = "round"
    ctx.globalCompositeOperation = global_composite_operation


window.addEventListener("resize", resize)
