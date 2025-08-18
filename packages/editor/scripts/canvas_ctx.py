# There are a lot of NOQAs in this file as these are typehints based on JS classes/methods.

from typing import Any, Literal

from js import (  # pyright: ignore[reportMissingImports]
    ImageData,
    MouseEvent,
    document,
)
from pyodide.ffi import JsProxy  # pyright: ignore[reportMissingImports]


class DOMRect:
    """Bounding box typehint."""

    bottom: float
    height: float
    left: float
    right: float
    top: float
    width: float
    x: float
    y: float


class ImageBitmap:
    """Image bitmap typehint."""

    height: float
    width: float


class TextMetrics:
    """TextMetrics typehint."""

    actualBoundingBoxAscent: float  # noqa: N815
    actualBoundingBoxDescent: float  # noqa: N815
    actualBoundingBoxLeft: float  # noqa: N815
    actualBoundingBoxRight: float  # noqa: N815
    alphabeticBaseline: float  # noqa: N815
    emHeightAscent: float  # noqa: N815
    emHeightDescent: float  # noqa: N815
    fontBoundingBoxAscent: float  # noqa: N815
    fontBoundingBoxDescent: float  # noqa: N815
    hangingBaseline: float  # noqa: N815
    ideographicBaseline: float  # noqa: N815
    width: float


class CanvasSettings:
    """`CanvasSettings` for `CanvasContext`."""

    def __init__(self) -> None:
        self.willReadFrequently = True


class CanvasContext:
    """`CanvasContext` for a HTML5 Canvas element."""

    # Custom attributes
    scaled_by: float = 2  # Better resolution
    drawing: bool = False
    action: Literal["pen", "eraser", "smudge", "rectangle", "triangle", "star"] = "pen"
    type: Literal["smooth", "pixel"] = "smooth"
    current_img: Any
    bounding_rect: Any
    last_x: float
    last_y: float
    smudge_data: ImageData
    prev_data: ImageData
    moving_image: bool
    writing_text: bool
    text_value: str
    prev_operation: Literal[
        "source-over",
        "source-in",
        "source-out",
        "source-atop",
        "destination-over",
        "destination-in",
        "destination-out",
        "destination-atop",
        "lighter",
        "copy",
        "xor",
        "multiply",
        "screen",
        "overlay",
        "darken",
        "lighten",
        "color-dodge",
        "color-burn",
        "hard-light",
        "soft-light",
        "difference",
        "exclusion",
        "hue",
        "saturation",
        "color",
        "luminosity",
    ]
    text_settings: dict[str, str | bool | int]
    history: list[Any]
    history_index: int
    text_placed: bool
    clipping: bool
    moving_clip: bool
    start_coords: list[float]
    prev_stroke_style: str
    prev_line_width: int
    size_change: int
    rotation: float
    is_rotating: bool
    current_position: list[float]
    drawing_shape: bool

    # Builtin attributes
    canvas: Any
    direction: Any
    fillStyle: Any  # noqa: N815
    filter: Any
    font: Any
    fontKerning: Any  # noqa: N815
    fontStretch: Any  # noqa: N815
    fontVariantCaps: Any  # noqa: N815
    globalAlpha: Any  # noqa: N815
    globalCompositeOperation: Literal[  # noqa: N815
        "source-over",
        "source-in",
        "source-out",
        "source-atop",
        "destination-over",
        "destination-in",
        "destination-out",
        "destination-atop",
        "lighter",
        "copy",
        "xor",
        "multiply",
        "screen",
        "overlay",
        "darken",
        "lighten",
        "color-dodge",
        "color-burn",
        "hard-light",
        "soft-light",
        "difference",
        "exclusion",
        "hue",
        "saturation",
        "color",
        "luminosity",
    ] = "source-over"

    imageSmoothingEnabled: bool  # noqa: N815
    imageSmoothingQuality: Any  # noqa: N815
    langExperimental: Any  # noqa: N815
    letterSpacing: Any  # noqa: N815
    lineCap: str = "round"  # noqa: N815
    lineDashOffset: Any  # noqa: N815
    lineJoin: str = "round"  # noqa: N815
    lineWidth: float  # noqa: N815
    miterLimit: Any  # noqa: N815
    shadowBlur: Any  # noqa: N815
    shadowColor: Any  # noqa: N815
    shadowOffsetX: Any  # noqa: N815
    shadowOffsetY: Any  # noqa: N815
    strokeStyle: str  # noqa: N815
    textAlign: Any  # noqa: N815
    textBaseline: Any  # noqa: N815
    textRendering: Any  # noqa: N815
    wordSpacing: Any  # noqa: N815

    def __init__(
        self,
        settings: CanvasSettings,
    ) -> None:
        """Get the canvas context 2d."""
        self.canvas = document.getElementById("image-canvas")
        self.ctx = self.canvas.getContext("2d", settings)

    ###########################################################################
    # properties
    ###########################################################################
    @property
    def rect_left(self) -> float:
        """The left side of the bounding rect."""
        return self.getBoundingClientRect().left

    @property
    def rect_right(self) -> float:
        """The right side of the bounding rect."""
        return self.getBoundingClientRect().left

    @property
    def rect_top(self) -> float:
        """The top side of the bounding rect."""
        return self.getBoundingClientRect().left

    @property
    def rect_bottom(self) -> float:
        """The bottom side of the bounding rect."""
        return self.getBoundingClientRect().left

    ###########################################################################
    # Cutstom Methods
    ###########################################################################
    def getBoundingClientRect(self) -> DOMRect:  # noqa: N802
        """Get the canvas getBoundingClientRect."""
        return self.canvas.getBoundingClientRect()

    def get_canvas_coords(self, event: MouseEvent) -> tuple[float, float]:
        """Give the canvas coordinates.

        Args:
            event (MouseEvent): The mouse event

        Returns:
            tuple[float, float]: The x and y coordinates

        """
        x = (event.pageX - self.rect_left) * self.scaled_by
        y = (event.pageY - self.rect_top) * self.scaled_by
        return (x, y)

    ###########################################################################
    # Builtin Methods
    ###########################################################################
    def arc(  # noqa: PLR0913 This method has this many arguments.
        self,
        x: float,
        y: float,
        radius: float,
        startAngle: float,  # noqa: N803
        endAngle: float,  # noqa: N803
        *,
        counterclockwise: bool = False,
    ) -> None:
        """Add arc."""
        self.ctx.arc(x, y, radius, startAngle, endAngle, counterclockwise)

    def arcTo(self) -> None:  # noqa: N802
        """Add arcTo."""
        self.ctx.arcTo()

    def beginPath(self) -> None:  # noqa: N802
        """Add beginPath."""
        self.ctx.beginPath()

    def bezierCurveTo(self, cp1x: float, cp1y: float, cp2x: float, cp2y: float, x: float, y: float) -> None:  # noqa: N802
        """Add bezierCurveTo."""
        self.ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y)

    def clearRect(self, x: float, y: float, width: float, height: float) -> None:  # noqa: N802
        """Add clearRect."""
        self.ctx.clearRect(x, y, width, height)

    def clip(self) -> None:
        """Add clip."""
        self.ctx.clip()

    def closePath(self) -> None:  # noqa: N802
        """Add closePath."""
        self.ctx.closePath()

    def createConicGradient(self) -> None:  # noqa: N802
        """Add createConicGradient."""
        self.ctx.createConicGradient()

    def createImageData(self) -> None:  # noqa: N802
        """Add createImageData."""
        self.ctx.createImageData()

    def createLinearGradient(self) -> None:  # noqa: N802
        """Add createLinearGradient."""
        self.ctx.createLinearGradient()

    def createPattern(self) -> None:  # noqa: N802
        """Add createPattern."""
        self.ctx.createPattern()

    def createRadialGradient(self) -> None:  # noqa: N802
        """Add createRadialGradient."""
        self.ctx.createRadialGradient()

    def drawFocusIfNeeded(self) -> None:  # noqa: N802
        """Add drawFocusIfNeeded."""
        self.ctx.drawFocusIfNeeded()

    def drawImage(  # noqa: N802
        self,
        image: JsProxy,
        dx: float,
        dy: float,
        dWidth: float | None = None,  # noqa: N803
        dHeight: float | None = None,  # noqa: N803
    ) -> None:
        """Add drawImage."""
        self.ctx.drawImage(image, dx, dy, dWidth, dHeight)

    def ellipse(  # noqa: PLR0913 This method has this many arguments.
        self,
        x: float,
        y: float,
        radiusX: float,  # noqa: N803
        radiusY: float,  # noqa: N803
        rotation: float,
        startAngle: float,  # noqa: N803
        endAngle: float,  # noqa: N803
        *,
        counterclockwise: bool = False,
    ) -> None:
        """Add ellipse."""
        self.ctx.ellipse(x, y, radiusX, radiusY, rotation, startAngle, endAngle, counterclockwise)

    def fill(self) -> None:
        """Add fill."""
        self.ctx.fill()

    def fillRect(self, x: float, y: float, width: float, height: float) -> None:  # noqa: N802
        """Add fillRect."""
        self.ctx.fillRect(x, y, width, height)

    def fillText(self, text: str, x: float, y: float) -> None:  # noqa: N802
        """Add fillText."""
        self.ctx.fillText(text, x, y)

    def getContextAttributes(self) -> None:  # noqa: N802
        """Add getContextAttributes."""
        self.ctx.getContextAttributes()

    def getImageData(self, sx: float, sy: float, sw: float, sh: float) -> ImageData:  # noqa: N802
        """Get the image data from the canvas."""
        return self.ctx.getImageData(sx, sy, sw, sh)

    def getLineDash(self) -> None:  # noqa: N802
        """Add getLineDash."""
        self.ctx.getLineDash()

    def getTransform(self) -> None:  # noqa: N802
        """Add getTransform."""
        self.ctx.getTransform()

    def isContextLost(self) -> None:  # noqa: N802
        """Add isContextLost."""
        self.ctx.isContextLost()

    def isPointInPath(self) -> None:  # noqa: N802
        """Add isPointInPath."""
        self.ctx.isPointInPath()

    def isPointInStroke(self) -> None:  # noqa: N802
        """Add isPointInStroke."""
        self.ctx.isPointInStroke()

    def lineTo(self, x: float, y: float) -> None:  # noqa: N802
        """Make a  line to the x, y given."""
        self.ctx.lineTo(x, y)

    def measureText(self, text: str) -> TextMetrics:  # noqa: N802
        """Add measureText."""
        return self.ctx.measureText(text)

    def moveTo(self, x: float, y: float) -> None:  # noqa: N802
        """Move to the x, y given."""
        self.ctx.moveTo(x, y)

    def putImageData(  #  # noqa: N802, PLR0913 This method has this many arguments.
        self,
        imageData: ImageData,  # noqa: N803
        dx: float,
        dy: float,
        dirtyX: float | None = None,  # noqa: N803
        dirtyY: float | None = None,  # noqa: N803
        dirtyWidth: float | None = None,  # noqa: N803
        dirtyHeight: float | None = None,  # noqa: N803
    ) -> None:
        """Paint rectangle onto canvas.

        Paints data from the given ImageData object onto the canvas. If a dirty rectangle is provided, only the
        pixels from that rectangle are painted. This method is not affected by the canvas transformation matrix.

        Parameters
        ----------
        imageData
            An ImageData object containing the array of pixel values.

        dx: float
            Horizontal position (x coordinate) at which to place the image data
            in the destination canvas.

        dy: float
            Vertical position (y coordinate) at which to place the image data
            in the destination canvas.

        dirtyX: float | None = None
            Horizontal position (x coordinate) of the top-left corner from
            which the image data will be extracted. Defaults to 0.

        dirtyY: float | None = None
            Vertical position (y coordinate) of the top-left corner from which
            the image data will be extracted. Defaults to 0.

        dirtyWidth: float | None = None
            Width of the rectangle to be painted. Defaults to the width of the
            image data.

        dirtyHeight: float | None = None
            Height of the rectangle to be painted. Defaults to the height of
            the image data.

        """
        self.ctx.putImageData(
            imageData,
            dx,
            dy,
            dirtyX,
            dirtyY,
            dirtyWidth,
            dirtyHeight,
        )

    def quadraticCurveTo(self) -> None:  # noqa: N802
        """Add quadraticCurveTo."""
        self.ctx.quadraticCurveTo()

    def rect(self, x: float, y: float, width: float, height: float) -> None:
        """Set the rect."""
        self.ctx.rect(x, y, width, height)

    def reset(self) -> None:
        """Add reset."""
        self.ctx.reset()

    def resetTransform(self) -> None:  # noqa: N802
        """Add resetTransform."""
        self.ctx.resetTransform()

    def restore(self) -> None:
        """Add restore."""
        self.ctx.restore()

    def rotate(self, angle: float) -> None:
        """Add rotate."""
        self.ctx.rotate(angle)

    def roundRect(self, x: float, y: float, width: float, height: float, radii: list[float]) -> None:  # noqa: N802
        """Add roundRect."""
        self.ctx.roundRect(x, y, width, height, radii)

    def save(self) -> None:
        """Add save."""
        self.ctx.save()

    def scale(self, x: float, y: float) -> None:
        """Add scale."""
        self.ctx.scale(x, y)

    def setLineDash(self, segments: list[float]) -> None:  # noqa: N802
        """Add setLineDash."""
        self.ctx.setLineDash(segments)

    def setTransform(self) -> None:  # noqa: N802
        """Add setTransform."""
        self.ctx.setTransform()

    def stroke(self) -> None:
        """Add stroke."""
        self.ctx.stroke()

    def strokeRect(self, x: float, y: float, width: float, height: float) -> None:  # noqa: N802
        """Add strokeRect."""
        self.ctx.strokeRect(x, y, width, height)

    def strokeText(self) -> None:  # noqa: N802
        """Add strokeText."""
        self.ctx.strokeText()

    def transform(self) -> None:
        """Add transform."""
        self.ctx.transform()

    def translate(self, x: float, y: float) -> None:
        """Add translate."""
        self.ctx.translate(x, y)
