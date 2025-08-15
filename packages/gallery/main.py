## PLACEHOLDER, TAKEN FROM:			# think we can remove this now, basically deleted most of their code
## https:#pyscript.com/@examples/webgl-icosahedron/latest

## DOCS
## https:#threejs.org/docs/

from pyodide.ffi import to_js, create_proxy  # pyright: ignore[reportMissingImports]
from pyodide.http import pyfetch  # pyright: ignore[reportMissingImports]
from pyscript import when, window, document  # pyright: ignore[reportMissingImports]
from js import (  # pyright: ignore[reportMissingImports]
    Math,
    THREE,
    LineSegments2,
    LineMaterial,
    Object,
    console,
    GLTFLoader,
    PointerLockControls,
)


from collections import defaultdict
from enum import Enum
import asyncio
import json


def log(*msgs):
    for msg in msgs:
        console.log(msg)


def convert_dict_to_js_object(my_dict: dict):
    """Convert a Python dict to a JavaScript object."""
    return Object.fromEntries(to_js(my_dict))


RENDERER = THREE.WebGLRenderer.new({"antialias": False})
RENDERER.shadowMap.enabled = False
RENDERER.shadowMap.type = THREE.PCFSoftShadowMap
RENDERER.shadowMap.needsUpdate = True
RENDERER.setSize(window.innerWidth, window.innerHeight)
document.body.appendChild(RENDERER.domElement)

CAMERA = THREE.PerspectiveCamera.new(53, window.innerWidth / window.innerHeight, 0.01, 500)
CAMERA.position.set(3, 1, 3.5)
CAMERA.rotation.set(0, 0.4, 0)

setcolor = "#8B8B8B"  # Nicer than just black
SCENE = THREE.Scene.new()
SCENE.background = THREE.Color.new(setcolor)
# SCENE.fog = THREE.Fog.new(setcolor, 2.5, 3.5)
# CAMERA.lookAt(SCENE.position)

MODULAR_GROUP = THREE.Object3D.new()
SCENE.add(MODULAR_GROUP)


# Camera controls and mouse lock
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
            "block",
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

# Global variable to toggle running
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


MOUSE = THREE.Vector2.new()


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


REPO_URL = (
    r"https://cdn.jsdelivr.net/gh/"
    r"Matiiss/pydis-cj12-heavenly-hostas@dev/"
    r"packages/gallery/assets/images/"
)


def load_image(image_loc: str):
    textureLoader = THREE.TextureLoader.new()
    texture = textureLoader.load(REPO_URL + image_loc)
    # texture = textureLoader.load(
    #     image_loc,
    #     create_proxy(lambda e: create_photoframe(texture)),
    #     create_proxy(log),
    #     create_proxy(log),
    # )
    return texture


def create_plane(texture):
    perms = convert_dict_to_js_object(
        {
            "map": texture,
            "transparent": True,  # removes the black bg
            # the color makes it look wierd so commented it
            # "color": "#A6D32B",
        }
    )

    geometry = THREE.PlaneGeometry.new(1, 1, 1)
    material = THREE.MeshBasicMaterial.new(perms)
    plane = THREE.Mesh.new(geometry, material)

    plane.scale.x = 1.414  # as HiPeople said the aspect ratio is 1 : sqrt2

    return plane


V3 = tuple[float, float, float]
V2 = tuple[float, float]
PAINTING_SLOTS: dict[int, tuple[V3, V3, V2]] = {}

# doesnt work, idk why
"""
def create_borders(plane):
    width = 0.02  # Width of the border

    # Create a border around the plane
    borderGeometry = THREE.EdgesGeometry.new(plane.geometry)
    borderMaterial = LineMaterial.new(
        convert_dict_to_js_object({
            "color": "#FF0000",
            "linewidth": 10
            })
        )
    border = LineSegments2.new(borderGeometry, borderMaterial)

    # Set the position and scale of the border
    border.position.copy(plane.position)
    border.scale.x = plane.scale.x * (1 + width)
    border.scale.y = plane.scale.y * (1 + width)
    border.scale.z = plane.scale.z * (1 + width)

    return border
 """


async def snap_to_slot(photo, slot: int):
    while slot not in PAINTING_SLOTS:
        await asyncio.sleep(0.05)
    (x, y, z), (nx, ny, nz), (w, h) = PAINTING_SLOTS[slot]
    photo.position.x = x
    photo.position.y = y
    photo.position.z = z

    q = THREE.Quaternion.new()
    q.setFromUnitVectors(THREE.Vector3.new(-1, 0, 0), THREE.Vector3.new(nx, ny, nz))
    photo.quaternion.copy(q)


async def create_photoframe(image_loc, slot: int = 0):
    texture = load_image(image_loc)
    plane = create_plane(texture)
    # border = create_borders(plane)

    photo = THREE.Object3D.new()
    photo.add(plane)
    # photo.add(border)

    await snap_to_slot(photo, slot)
    SCENE.add(photo)

    return photo


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

        # Backface culling
        assert obj.children[0].name == "Cube"
        for v in obj.children[0].children:
            v.material.side = THREE.FrontSide

        for v in obj.children[1:]:
            id_ = int(v.name[-3:])
            position: V3 = v.position.x, v.position.y, v.position.z

            n_array = v.geometry.attributes.normal.array
            # Y-up/Z-up shenanigans
            normal: V3 = (n_array[0], n_array[2], n_array[1])

            bb = v.geometry.boundingBox
            size_xyz = [abs(getattr(bb.max, i) - getattr(bb.min, i)) for i in ("x", "y", "z")]
            # Height is Z
            size_wh: V2 = (max(size_xyz[0], size_xyz[1]), (size_xyz[2]))

            PAINTING_SLOTS[id_] = (position, normal, size_wh)

            v.visible = False

        print(f"Loading done! Here's its component structure:")
        print(tree_print(obj))
        print(f"Painting slots:")
        print(list(PAINTING_SLOTS.keys()))

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


async def load_images_from_listing() -> None:
    r = await pyfetch(REPO_URL + "../" + "test-image-listing.json")
    data = await r.text()
    images = json.loads(data)
    for idx, img in enumerate(images):
        asyncio.ensure_future(create_photoframe(img, idx))


async def main():
    clock = THREE.Clock.new()
    while True:
        move_character(clock.getDelta())
        RENDERER.render(SCENE, CAMERA)
        await asyncio.sleep(0.02)


if __name__ == "__main__":
    generate_lights()
    load_gallery()
    asyncio.ensure_future(load_images_from_listing())

    asyncio.ensure_future(main())
