from js import MouseEvent, document, window
from pyscript import when

canvas = document.getElementById("image-canvas")
ctx = canvas.getContext("2d")

display_height = window.innerHeight * 0.8
display_width = display_height * (2**0.5)

SCALE = 2

canvas.style.height = f"{display_height}px"  # 80vh
canvas.style.width = f"{display_width}px"  # Same ratio as an A4 sheet of paper

canvas.height = display_height * SCALE
canvas.width = display_width * SCALE

ctx.strokeStyle = "black"
ctx.lineWidth = 10
ctx.lineCap = "round"
ctx.lineJoin = "round"

drawing = False
rect = canvas.getBoundingClientRect()


def get_canvas_coords(event: MouseEvent) -> tuple[float, float]:
    """Give the canvas coordinates.

    Args:
        event (MouseEvent): The mouse event

    Returns:
        tuple[float, float]: The x and y coordinates

    """
    x = (event.clientX - rect.left) * SCALE
    y = (event.clientY - rect.top) * SCALE
    return (x, y)


@when("mousedown", "#image-canvas")
def start_path(event: MouseEvent) -> None:
    """Start drawing the path.

    Args:
        event (MouseEvent): The mouse event

    """
    global drawing
    drawing = True
    x, y = get_canvas_coords(event)
    ctx.beginPath()
    ctx.moveTo(x, y)


@when("mousemove", "#image-canvas")
def mouse_tracker(event: MouseEvent) -> None:
    """Draw the path following the mouse.

    Args:
        event (MouseEvent): The mouse event

    """
    if not drawing:
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
    global drawing
    if not drawing:
        return
    drawing = False


@when("mouseout", "#image-canvas")
def leaves_canvas(event: MouseEvent) -> None:
    """Handle mouse leaving canvas.

    Args:
        event (MouseEvent): The mouse event

    """
    global drawing
    if not drawing:
        return
    x, y = get_canvas_coords(event)
    ctx.lineTo(x, y)
    ctx.stroke()  # Draws the line to the point on the edge where the mouse leaves the canvas
    drawing = False
