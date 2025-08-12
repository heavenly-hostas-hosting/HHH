## PLACEHOLDER, TAKEN FROM:
## https://pyscript.com/@examples/webgl-icosahedron/latest

## DOCS
## https://threejs.org/docs/

from pyodide.ffi import create_proxy
from pyscript import when, window, document
from js import Math, THREE, GLTFLoader, PointerLockControls

from collections import defaultdict
from enum import Enum
import asyncio


RENDERER = THREE.WebGLRenderer.new({"antialias": False})
document.body.appendChild(RENDERER.domElement)
RENDERER.setSize(1000, 1000)
RENDERER.shadowMap.enabled = False
RENDERER.shadowMap.type = THREE.PCFSoftShadowMap
RENDERER.shadowMap.needsUpdate = True
RENDERER.setSize(window.innerWidth, window.innerHeight)

CAMERA = THREE.PerspectiveCamera.new(53, window.innerWidth / window.innerHeight, 0.01, 500)
CAMERA.position.set(3, 1, 3.5)
CAMERA.rotation.set(0, 0.4, 0)

setcolor = "#000000"
SCENE = THREE.Scene.new()
SCENE.background = THREE.Color.new(setcolor)
# SCENE.fog = THREE.Fog.new(setcolor, 2.5, 3.5)

# CAMERA.lookAt(SCENE.position)

MODULAR_GROUP = THREE.Object3D.new()
SCENE.add(MODULAR_GROUP)


MOUSE = THREE.Vector2.new()

CONTROLS = PointerLockControls.new(CAMERA, document.body)
document.getElementById("instructions").addEventListener("click", create_proxy(CONTROLS.lock))
CONTROLS.addEventListener(
    "lock",
    create_proxy(
        lambda x: setattr(
            document.getElementById("instructions").style,
            "display",
            "none",
        ),
    ),
)
CONTROLS.addEventListener(
    "unlock",
    create_proxy(
        lambda x: setattr(
            document.getElementById("instructions").style,
            "display",
            "",
        ),
    ),
)


INPUTS = Enum("INPUTS", ["FORW", "LEFT", "RIGHT", "BACK", "UP", "DOWN", "RUN"])
KEY_MAPPINGS: dict[INPUTS, set[str]] = {
    INPUTS.FORW: {"KeyW", "KeyK", "ArrowUp"},
    INPUTS.LEFT: {"KeyH", "KeyA", "ArrowLeft"},
    INPUTS.RIGHT: {"KeyL", "KeyD", "ArrowRight"},
    INPUTS.BACK: {"KeyJ", "KeyS", "ArrowDown"},
    #
    INPUTS.UP: {"Space"},
    INPUTS.DOWN: {"ShiftLeft", "ShiftRight"},
    #
    INPUTS.RUN: {"KeyZ"},
}
KEY_STATES: dict[str, bool] = defaultdict(bool)
document.addEventListener("keydown", create_proxy(lambda x: KEY_STATES.__setitem__(x.code, True)))
document.addEventListener("keyup", create_proxy(lambda x: KEY_STATES.__setitem__(x.code, False)))

RUN_STATE = False


def toggle_run(event):
    global RUN_STATE
    if event.code in KEY_MAPPINGS[INPUTS.RUN]:
        RUN_STATE = not RUN_STATE


document.addEventListener("keydown", create_proxy(toggle_run))

VELOCITY = THREE.Vector3.new()


def move_character(delta_time: float):
    pressed_keys = {k for k, v in KEY_MAPPINGS.items() if any(KEY_STATES[i] for i in v)}
    damping = 7
    if RUN_STATE:
        acceleration = 25
        max_speed = 50

        CAMERA.fov = min(CAMERA.fov + 60 * delta_time, 60)
    else:
        acceleration = 10
        max_speed = 20

        CAMERA.fov = max(CAMERA.fov - 60 * delta_time, 53)
    CAMERA.updateProjectionMatrix()

    move = THREE.Vector3.new()
    if INPUTS.FORW in pressed_keys:
        move.z -= 1
    if INPUTS.BACK in pressed_keys:
        move.z += 1

    if INPUTS.LEFT in pressed_keys:
        move.x -= 1
    if INPUTS.RIGHT in pressed_keys:
        move.x += 1

    if INPUTS.UP in pressed_keys:
        move.y += 1
    if INPUTS.DOWN in pressed_keys:
        move.y -= 1

    if move.length() > 0:
        q = CAMERA.quaternion
        yaw = Math.atan2(2 * (q.w * q.y + q.x * q.z), 1 - 2 * (q.y * q.y + q.z * q.z))
        yaw_q = THREE.Quaternion.new()
        yaw_q.setFromAxisAngle(THREE.Vector3.new(0, 1, 0), yaw)

        move.applyQuaternion(yaw_q).normalize()
        VELOCITY.addScaledVector(move, acceleration * delta_time)

        if VELOCITY.length() > max_speed:
            VELOCITY.setLength(max_speed)

    VELOCITY.multiplyScalar(1 - min(damping * delta_time, 1))
    CAMERA.position.addScaledVector(VELOCITY, delta_time)


@when("mousemove", "body")
def onMouseMove(event):
    event.preventDefault()
    MOUSE.x = (event.clientX / window.innerWidth) * 2 - 1
    MOUSE.y = -(event.clientY / window.innerHeight) * 2 + 1


def mathRandom(num=1):
    setNumber = -Math.random() * num + Math.random() * num
    return setNumber


def generate_lights() -> None:
    light = THREE.SpotLight.new(0xFF_FF_FF, 3)
    light.position.set(5, 5, 2)
    light.castShadow = True
    light.shadow.mapSize.width = 10000
    light.shadow.mapSize.height = light.shadow.mapSize.width
    light.penumbra = 0.5
    SCENE.add(light)

    lightBack = THREE.PointLight.new(0xEF_FF_FF, 1)
    lightBack.position.set(0, -3, -1)
    SCENE.add(lightBack)

    ambientLight = THREE.AmbientLight.new(0xFFFFFF, 0.3)
    SCENE.add(ambientLight)

    # rectSize = 2
    # intensity = 14
    # rectLight = THREE.RectAreaLight.new(0x0FFFFF, intensity, rectSize, rectSize)
    # rectLight.position.set(0, 0, 1)
    # rectLight.lookAt(0, 0, 0)
    # SCENE.add(rectLight)


def tree_print(x, indent=0):
    # Prints a 3D model's tree structure
    qu = '"'
    output = " " * 4 * indent + f"{x.name or qu * 2} ({x.type})"
    for i in x.children:
        output += "\n" + tree_print(i, indent=indent + 1)
    return output


def load_gallery():
    def inner_loader(gltf):
        obj = gltf.scene
        MODULAR_GROUP.add(obj)

        obj.position.x = 0
        obj.position.y = 0
        obj.position.z = 0

        obj.rotation.x = 0
        obj.rotation.y = 0
        obj.rotation.z = 0

        obj.scale.x = 1
        obj.scale.y = 1
        obj.scale.z = 1

        # Backface culling
        for v in obj.children[0].children:
            v.material.side = THREE.FrontSide

        print(f"Loading done! Here's its component structure:")
        print(tree_print(obj))

    def inner_progress(xhr):
        print(str(xhr.loaded) + " loaded")

    def inner_error(error):
        print(f"error: {error}")

    loader = GLTFLoader.new()
    loader.load(
        "./assets/gallery.glb",
        create_proxy(inner_loader),
        create_proxy(inner_progress),
        create_proxy(inner_error),
    )


async def main():
    clock = THREE.Clock.new()
    while True:
        move_character(clock.getDelta())
        RENDERER.render(SCENE, CAMERA)
        await asyncio.sleep(0.02)


if __name__ == "__main__":
    generate_lights()
    load_gallery()
    asyncio.ensure_future(main())
