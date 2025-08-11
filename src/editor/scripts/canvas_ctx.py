from typing import Any, Literal
from js import MouseEvent, document  # pyright: ignore[reportMissingImports]


class CanvasSettings:
    """`CanvasSettings` for `CanvasContext`."""

    def __init__(self) -> None:
        self.willReadFrequently = True


class CanvasContext:
    """`CanvasContext` for a HTML5 Canvas element."""

    # Cutsom attributes
    SCALE: int = 2  # Better resolution
    drawing: bool = False
    action: Literal["pen", "eraser"] = "pen"
    rect: 

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
    ]

    imageSmoothingEnabled: Any
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
        canvas = document.getElementById("image-canvas")
        self.ctx = canvas.getContext("2d", settings)

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
    def getBoundingClientRect(self) -> Any:  # noqa: N802
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

    def arcTo(self) -> None:
        """Add arcTo."""
        self.ctx.arcTo()

    def beginPath(self) -> None:
        """Add beginPath."""
        self.ctx.beginPath()

    def bezierCurveTo(self) -> None:
        """Add bezierCurveTo."""
        self.ctx.bezierCurveTo()

    def clearRect(self) -> None:
        """Add clearRect."""
        self.ctx.clearRect()

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

    def drawImage(self) -> None:
        """Add drawImage."""
        self.ctx.drawImage()

    def ellipse(self) -> None:
        """Add ellipse."""
        self.ctx.ellipse()

    def fill(self) -> None:
        """Add fill."""
        self.ctx.fill()

    def fillRect(self) -> None:
        """Add fillRect."""
        self.ctx.fillRect()

    def fillText(self) -> None:
        """Add fillText."""
        self.ctx.fillText()

    def getContextAttributes(self) -> None:
        """Add getContextAttributes."""
        self.ctx.getContextAttributes()

    def getImageData(self, *args, **kwargs) -> Any:
        """Get the image data from the canvas."""
        self.ctx.getImageData(*args, **kwargs)

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

    def putImageData(self) -> None:
        """Add putImageData."""
        self.ctx.putImageData()

    def quadraticCurveTo(self) -> None:
        """Add quadraticCurveTo."""
        self.ctx.quadraticCurveTo()

    def rect(self, *args) -> None:
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

    def scale(self) -> None:
        """Add scale."""
        self.ctx.scale()

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
