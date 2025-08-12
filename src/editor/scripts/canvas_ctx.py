from typing import Any, Literal

from js import ImageData, MouseEvent, document  # pyright: ignore[reportMissingImports]


class CanvasSettings:
    """`CanvasSettings` for `CanvasContext`."""

    def __init__(self) -> None:
        self.willReadFrequently = True


class CanvasContext:
    """`CanvasContext` for a HTML5 Canvas element."""

    # Cutsom attributes
    scale: int = 2  # Better resolution
    drawing: bool = False
    action: Literal["pen", "eraser", "smudge"] = "pen"
    type: Literal["smooth", "pixel"] = "smooth"
    #
    last_x: float
    last_y: float
    smudge_data: ImageData

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
    def getBoundingClientRect(self) -> Any:  # noqa: ANN401, N802
        """Get the canvas getBoundingClientRect."""
        return self.canvas.getBoundingClientRect()

    def get_canvas_coords(self, event: MouseEvent) -> tuple[float, float]:
        """Give the canvas coordinates.

        Args:
            event (MouseEvent): The mouse event

        Returns:
            tuple[float, float]: The x and y coordinates
        """
        x = (event.pageX - self.rect_left) * self.SCALE
        y = (event.pageY - self.rect_top) * self.SCALE
        return (x, y)

    ###########################################################################
    # Builtin Methods
    ###########################################################################
    def arc(self) -> None:
        """Add arc."""
        self.ctx.arc()

    def arcTo(self) -> None:  # noqa: N802
        """Add arcTo."""
        self.ctx.arcTo()

    def beginPath(self) -> None:  # noqa: N802
        """Add beginPath."""
        self.ctx.beginPath()

    def bezierCurveTo(self) -> None:  # noqa: N802
        """Add bezierCurveTo."""
        self.ctx.bezierCurveTo()

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

    def drawImage(self, *args: list) -> None:  # noqa: N802
        """Add drawImage."""
        self.ctx.drawImage(*args)

    def ellipse(self, *args: list) -> None:
        """Add ellipse."""
        self.ctx.ellipse(*args)

    def fill(self) -> None:
        """Add fill."""
        self.ctx.fill()

    def fillRect(self, x: float, y: float, width: float, height: float) -> None:  # noqa: N802
        """Add fillRect."""
        self.ctx.fillRect(x, y, width, height)

    def fillText(self) -> None:  # noqa: N802
        """Add fillText."""
        self.ctx.fillText()

    def getContextAttributes(self) -> None:  # noqa: N802
        """Add getContextAttributes."""
        self.ctx.getContextAttributes()

    def getImageData(self, *args: list, **kwargs: dict) -> Any:  # noqa: ANN401, N802
        """Get the image data from the canvas."""
        self.ctx.getImageData(*args, **kwargs)

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

    def measureText(self) -> None:  # noqa: N802
        """Add measureText."""
        self.ctx.measureText()

    def moveTo(self, x: float, y: float) -> None:  # noqa: N802
        """Move to the x, y given."""
        self.ctx.moveTo(x, y)

    def putImageData(  # noqa: PLR0913
        self,
        imageData,
        dx: float,
        dy: float,
        dirtyX: float | None = None,
        dirtyY: float | None = None,
        dirtyWidth: float | None = None,
        dirtyHeight: float | None = None,
    ) -> None:  # noqa: N802
        """Paints data from the given ImageData object onto the canvas. If a
        dirty rectangle is provided, only the pixels from that rectangle are
        painted. This method is not affected by the canvas transformation
        matrix.

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

    def rect(self, *_: list) -> None:
        """Set the rect."""
        self.ctx.rect()

    def reset(self) -> None:
        """Add reset."""
        self.ctx.reset()

    def resetTransform(self) -> None:  # noqa: N802
        """Add resetTransform."""
        self.ctx.resetTransform()

    def restore(self) -> None:
        """Add restore."""
        self.ctx.restore()

    def rotate(self) -> None:
        """Add rotate."""
        self.ctx.rotate()

    def roundRect(self) -> None:  # noqa: N802
        """Add roundRect."""
        self.ctx.roundRect()

    def save(self) -> None:
        """Add save."""
        self.ctx.save()

    # def scale(self) -> None:
    #     """Add scale."""
    #     self.ctx.scale()

    def setLineDash(self) -> None:  # noqa: N802
        """Add setLineDash."""
        self.ctx.setLineDash()

    def setTransform(self) -> None:  # noqa: N802
        """Add setTransform."""
        self.ctx.setTransform()

    def stroke(self) -> None:
        """Add stroke."""
        self.ctx.stroke()

    def strokeRect(self) -> None:  # noqa: N802
        """Add strokeRect."""
        self.ctx.strokeRect()

    def strokeText(self) -> None:  # noqa: N802
        """Add strokeText."""
        self.ctx.strokeText()

    def transform(self) -> None:
        """Add transform."""
        self.ctx.transform()

    def translate(self) -> None:
        """Add translate."""
        self.ctx.translate()
