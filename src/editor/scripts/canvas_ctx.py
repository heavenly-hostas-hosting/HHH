from typing import Any, Literal

from js import (  # pyright: ignore[reportMissingImports]
    ImageData,
    MouseEvent,
    document,
)
from pyodide.ffi import JsProxy  # pyright: ignore[reportMissingImports]


class CanvasSettings:
    """`CanvasSettings` for `CanvasContext`."""

    def __init__(self) -> None:
        self.willReadFrequently = True


class CanvasContext:
    """`CanvasContext` for a HTML5 Canvas element."""

    # Custom attributes
    scaled_by: float = 2  # Better resolution
    drawing: bool = False
    action: Literal["pen", "eraser", "smudge"] = "pen"
    type: Literal["smooth", "pixel"] = "smooth"
    current_img: Any
    bounding_rect: Any
    last_x: float
    last_y: float
    smudge_data: ImageData
    prev_data: ImageData
    moving_image: bool
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

    # Builtin attributes
    canvas: Any
    direction: Any
    fillStyle: Any
    filter: Any
    font: Any
    fontKerning: Any
    fontStretch: Any
    fontVariantCaps: Any
    globalAlpha: Any
    globalCompositeOperation: Literal[
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

    imageSmoothingEnabled: bool
    imageSmoothingQuality: Any
    langExperimental: Any
    letterSpacing: Any
    lineCap: str = "round"
    lineDashOffset: Any
    lineJoin: str = "round"
    lineWidth: float
    miterLimit: Any
    shadowBlur: Any
    shadowColor: Any
    shadowOffsetX: Any
    shadowOffsetY: Any
    strokeStyle: str
    textAlign: Any
    textBaseline: Any
    textRendering: Any
    wordSpacing: Any

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
    def getBoundingClientRect(self) -> Any:  # noqa: ANN401
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
    def arc(  # noqa: PLR0913
        self,
        x: float,
        y: float,
        radius: float,
        startAngle: float,
        endAngle: float,
        *,
        counterclockwise: bool = False,
    ) -> None:
        """Add arc."""
        self.ctx.arc(x, y, radius, startAngle, endAngle, counterclockwise)

    def arcTo(self) -> None:
        """Add arcTo."""
        self.ctx.arcTo()

    def beginPath(self) -> None:
        """Add beginPath."""
        self.ctx.beginPath()

    def bezierCurveTo(self) -> None:
        """Add bezierCurveTo."""
        self.ctx.bezierCurveTo()

    def clearRect(self, x: float, y: float, width: float, height: float) -> None:
        """Add clearRect."""
        self.ctx.clearRect(x, y, width, height)

    def clip(self) -> None:
        """Add clip."""
        self.ctx.clip()

    def closePath(self) -> None:
        """Add closePath."""
        self.ctx.closePath()

    def createConicGradient(self) -> None:
        """Add createConicGradient."""
        self.ctx.createConicGradient()

    def createImageData(self) -> None:
        """Add createImageData."""
        self.ctx.createImageData()

    def createLinearGradient(self) -> None:
        """Add createLinearGradient."""
        self.ctx.createLinearGradient()

    def createPattern(self) -> None:
        """Add createPattern."""
        self.ctx.createPattern()

    def createRadialGradient(self) -> None:
        """Add createRadialGradient."""
        self.ctx.createRadialGradient()

    def drawFocusIfNeeded(self) -> None:
        """Add drawFocusIfNeeded."""
        self.ctx.drawFocusIfNeeded()

    def drawImage(
        self,
        image: JsProxy,
        dx: float,
        dy: float,
    ) -> None:
        """Add drawImage."""
        self.ctx.drawImage(image, dx, dy)

    def ellipse(  # noqa: PLR0913 We didn't decide how many args there are so...
        self,
        x: float,
        y: float,
        radiusX: float,
        radiusY: float,
        rotation: float,
        startAngle: float,
        endAngle: float,
        *,
        counterclockwise: bool = False,
    ) -> None:
        """Add ellipse."""
        self.ctx.ellipse(x, y, radiusX, radiusY, rotation, startAngle, endAngle, counterclockwise)

    def fill(self) -> None:
        """Add fill."""
        self.ctx.fill()

    def fillRect(self, x: float, y: float, width: float, height: float) -> None:
        """Add fillRect."""
        self.ctx.fillRect(x, y, width, height)

    def fillText(self) -> None:
        """Add fillText."""
        self.ctx.fillText()

    def getContextAttributes(self) -> None:
        """Add getContextAttributes."""
        self.ctx.getContextAttributes()

    def getImageData(self, sx: float, sy: float, sw: float, sh: float) -> Any:  # noqa: ANN401
        """Get the image data from the canvas."""
        self.ctx.getImageData(sx, sy, sw, sh)

    def getLineDash(self) -> None:
        """Add getLineDash."""
        self.ctx.getLineDash()

    def getTransform(self) -> None:
        """Add getTransform."""
        self.ctx.getTransform()

    def isContextLost(self) -> None:
        """Add isContextLost."""
        self.ctx.isContextLost()

    def isPointInPath(self) -> None:
        """Add isPointInPath."""
        self.ctx.isPointInPath()

    def isPointInStroke(self) -> None:
        """Add isPointInStroke."""
        self.ctx.isPointInStroke()

    def lineTo(self, x: float, y: float) -> None:
        """Make a  line to the x, y given."""
        self.ctx.lineTo(x, y)

    def measureText(self) -> None:
        """Add measureText."""
        self.ctx.measureText()

    def moveTo(self, x: float, y: float) -> None:
        """Move to the x, y given."""
        self.ctx.moveTo(x, y)

    def putImageData(  # noqa: PLR0913
        self,
        imageData: ImageData,
        dx: float,
        dy: float,
        dirtyX: float | None = None,
        dirtyY: float | None = None,
        dirtyWidth: float | None = None,
        dirtyHeight: float | None = None,
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

    def quadraticCurveTo(self) -> None:
        """Add quadraticCurveTo."""
        self.ctx.quadraticCurveTo()

    def rect(self, *_: list) -> None:
        """Set the rect."""
        self.ctx.rect()

    def reset(self) -> None:
        """Add reset."""
        self.ctx.reset()

    def resetTransform(self) -> None:
        """Add resetTransform."""
        self.ctx.resetTransform()

    def restore(self) -> None:
        """Add restore."""
        self.ctx.restore()

    def rotate(self) -> None:
        """Add rotate."""
        self.ctx.rotate()

    def roundRect(self) -> None:
        """Add roundRect."""
        self.ctx.roundRect()

    def save(self) -> None:
        """Add save."""
        self.ctx.save()

    def scale(self, x: float, y: float) -> None:
        """Add scale."""
        self.ctx.scale(x, y)

    def setLineDash(self) -> None:
        """Add setLineDash."""
        self.ctx.setLineDash()

    def setTransform(self) -> None:
        """Add setTransform."""
        self.ctx.setTransform()

    def stroke(self) -> None:
        """Add stroke."""
        self.ctx.stroke()

    def strokeRect(self) -> None:
        """Add strokeRect."""
        self.ctx.strokeRect()

    def strokeText(self) -> None:
        """Add strokeText."""
        self.ctx.strokeText()

    def transform(self) -> None:
        """Add transform."""
        self.ctx.transform()

    def translate(self) -> None:
        """Add translate."""
        self.ctx.translate()
