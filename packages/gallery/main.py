## PLACEHOLDER, TAKEN FROM:			# think we can remove this now, basically deleted most of their code
## https:#pyscript.com/@examples/webgl-icosahedron/latest

## DOCS
## https:#threejs.org/docs/


# -------------------------------------- IMPORTS --------------------------------------
print("IMPORTS")

from pyodide.ffi import to_js, create_proxy  # pyright: ignore[reportMissingImports]
from pyodide.http import pyfetch  # pyright: ignore[reportMissingImports]
from pyscript import when, window, document  # pyright: ignore[reportMissingImports]
from js import (  # pyright: ignore[reportMissingImports]
    Math,
    THREE,
    Object,
    GLTFLoader,
    RGBELoader,
    PointerLockControls,
)


from collections import defaultdict
from enum import Enum
import asyncio
import json
import warnings

# Typing
from collections.abc import Callable
from typing import Any

# Local
from map_loader import MAP, get_map_layout, ROOM_TYPES, get_gallery_room

# -------------------------------------- GLOBAL VARIABLES --------------------------------------
print("GLOBAL VARIABLES")

# Renderer set up
RENDERER = THREE.WebGLRenderer.new({"antialias": False})
RENDERER.shadowMap.enabled = False
RENDERER.shadowMap.type = THREE.PCFSoftShadowMap
RENDERER.shadowMap.needsUpdate = True
RENDERER.setSize(window.innerWidth, window.innerHeight)
document.body.appendChild(RENDERER.domElement)

# Scene setup
setcolor = "#8B8B8B"  # Nicer than just black
SCENE = THREE.Scene.new()
SCENE.background = THREE.Color.new(setcolor)

# Camera setup
CAMERA = THREE.PerspectiveCamera.new(53, window.innerWidth / window.innerHeight, 0.01, 500)
CAMERA.position.set(3, 1, 3.5)
CAMERA.rotation.set(0, 0.4, 0)
SCENE.add(CAMERA)


# Building blocks for the rooms, will be filled later
GALLERY_BLOCKS: dict[ROOM_TYPES, THREE.Group] = {}


# Other global variables
ROOMS: list[THREE.Group] = []  # a list of all rooms in the scene
PAINTINGS: list[THREE.Object3D] = []  # a list of all the paintings in the scene

# Related to Moving
RUN_STATE: bool = False  # to toggle running
CAN_MOVE: bool = False  # so that the player cant move unless he is "locked in"

# distance which we maintain from walls
OFFSET = 0.2

VELOCITY = THREE.Vector3.new()

REPO_URL = (
    r"https://cdn.jsdelivr.net/gh/"
    r"Matiiss/pydis-cj12-heavenly-hostas@dev/"
    r"packages/gallery/assets/images/"
)

# For Type Hinting
V3 = tuple[float, float, float]
V2 = tuple[float, float]


# -------------------------------------- HELPER FUNCTIONS --------------------------------------
print("HELPER FUNCTIONS")


def tree_print(x, indent=0):
    # Prints a 3D model's tree structure
    qu = '"'
    output = " " * 4 * indent + f"{x.name or qu * 2} ({x.type})"
    for i in x.children:
        output += "\n" + tree_print(i, indent=indent + 1)
    return output


def convert_dict_to_js_object(my_dict: dict):
    """Convert a Python dict to a JavaScript object."""
    return Object.fromEntries(to_js(my_dict))


def mathRandom(num=1):
    setNumber = -Math.random() * num + Math.random() * num
    return setNumber


def get_painting_info(p: THREE.Mesh) -> tuple[V3, V3, V2]:
    v_pos = THREE.Vector3.new()
    p.getWorldPosition(v_pos)
    position: V3 = v_pos.x, v_pos.y, v_pos.z

    # Beware possible Y-up/Z-up shenanigans
    n_array = p.geometry.attributes.normal.array
    world_matrix = p.matrixWorld
    normal_matrix = THREE.Matrix3.new().getNormalMatrix(world_matrix)
    world_normal = (
        THREE.Vector3.new(
            -n_array[2],
            n_array[1],
            n_array[0],
        )
        .applyMatrix3(normal_matrix)
        .normalize()
    )
    normal = world_normal.x, world_normal.y, world_normal.z

    bb = p.geometry.boundingBox
    size_xyz = [abs(getattr(bb.max, i) - getattr(bb.min, i)) for i in ("x", "y", "z")]
    # Height is Z
    size_wh: V2 = (max(size_xyz[0], size_xyz[1]), (size_xyz[2]))

    return (position, normal, size_wh)


def get_chunk_coords(room_apothem: float) -> tuple[int, int]:
    x_coord = (CAMERA.position.x - room_apothem) // (room_apothem * 2)
    z_coord = (CAMERA.position.z - room_apothem) // (room_apothem * 2)

    if x_coord < 0:
        x_coord = 0
    if z_coord < 0:
        z_coord = 0

    return x_coord, z_coord


# -------------------------------------- MOVEMENT CONTROLS --------------------------------------
print("MOVEMENT CONTROLS")

# Movement Controls
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


def toggle_run(event):
    global RUN_STATE
    if event.code in KEY_MAPPINGS[INPUTS.RUN]:
        RUN_STATE = not RUN_STATE
    if event.key == "h":
        openHelpMenu()

document.addEventListener("keydown", create_proxy(toggle_run))


# Main move function
def move_character(delta_time: float) -> THREE.Vector3:
    if not CAN_MOVE:
        return THREE.Vector3.new(0, 0, 0)
    pressed_keys = {k for k, v in KEY_MAPPINGS.items() if any(KEY_STATES[i] for i in v)}
    damping = 8
    if RUN_STATE:
        acceleration = 25 * 3
        max_speed = 50 * 3

        CAMERA.fov = min(CAMERA.fov + 60 * delta_time, 60)
    else:
        acceleration = 10 * 3
        max_speed = 20 * 3

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
    return VELOCITY


# -------------------------------------- MOUSE CONTROLS --------------------------------------
print("MOUSE CONTROLS")

MOUSE = THREE.Vector2.new()

# Mouse Lock Functions
def cam_lock(e):
    global CAN_MOVE
    setattr(
        document.getElementById("instructions").style,
        "display",
        "none",
    )
    CAN_MOVE = True

def cam_unlock(e):
    global CAN_MOVE
    setattr(
        document.getElementById("instructions").style,
        "display",
        "block",
    )
    CAN_MOVE = False

# Mouse Lock
CONTROLS = PointerLockControls.new(CAMERA, document.body)
document.getElementById("instructions").addEventListener("click", create_proxy(CONTROLS.lock))
CONTROLS.addEventListener(
    "lock",
    create_proxy(cam_lock),
)
CONTROLS.addEventListener(
    "unlock",
    create_proxy(cam_unlock)
)


# Mouse Controls
@when("mousemove", "body")
def onMouseMove(event):
    event.preventDefault()
    MOUSE.x = (event.clientX / window.innerWidth) * 2 - 1
    MOUSE.y = -(event.clientY / window.innerHeight) * 2 + 1


# -------------------------------------- COLLISION DETECTION --------------------------------------
print("COLLISION DETECTION")


def check_collision(velocity: THREE.Vector3, delta_time: float) -> bool:
    """
    Checks for collision with walls (cubes) and triggers
    returns true if it is safe to move and false if movement should be stopped
    """
    raycaster = THREE.Raycaster.new()
    direction = velocity.clone().normalize()
    raycaster.set(CAMERA.position, direction)

    return check_collision_with_wall(velocity, delta_time, raycaster)


def check_collision_with_wall(velocity: THREE.Vector3, delta_time: float, raycaster: THREE.Raycaster) -> bool:
    cubes = []
    [cubes.extend(c.getObjectByName("Cubes").children) for c in ROOMS]
    intersections = raycaster.intersectObjects(cubes, recursive=True)
    if not intersections:
        return True
    return intersections[0].distance > velocity.length() * delta_time + OFFSET


# -------------------------------------- HELP MENU --------------------------------------
print("HELP MENU")

def closeHelpMenu(e = None):
    help_menu = document.getElementById("help-menu")
    help_menu.close()

    instructions = document.getElementById("instructions")
    instructions.style.display = "block"

def openHelpMenu(e = None):
    CONTROLS.unlock()

    help_menu = document.getElementById("help-menu")
    help_menu.showModal()

    instructions = document.getElementById("instructions")
    instructions.style.display = "none"

document.getElementById("close-help-menu").addEventListener("click", create_proxy(closeHelpMenu))


# -------------------------------------- ROOM CREATION --------------------------------------
print("ROOM CREATION")


def room_objects_handling(room: THREE.Group) -> None:
    assert room.children[0].name.startswith("Cube")
    room.children[0].name = "Cubes"
    for v in room.children[0].children:
        v.material.side = THREE.FrontSide

    triggers = THREE.Group.new()
    triggers.name = "Triggers"

    pictures = THREE.Group.new()
    pictures.name = "Pictures"

    for v in room.children[1:]:
        if v.name.startswith("trigger"):
            room.remove(v)
            triggers.add(v)
            v.visible = False

        if v.name.startswith("pic"):
            room.remove(v)
            pictures.add(v)
            v.visible = False

    room.add(triggers)
    room.add(pictures)


def load_image(image_loc: str, slot: int):
    if slot >= len(PAINTINGS):
        warnings.warn(
            f"WARNING: slot to be accessed '{slot}' is greater than the maximum available "
            f"one '{len(PAINTINGS) - 1}'. The image will not be loaded."
        )

    textureLoader = THREE.TextureLoader.new()

    def inner_loader(loaded_obj):
        # Put texture on a plane
        perms = convert_dict_to_js_object(
            {
                "map": loaded_obj,
                "transparent": True,
            }
        )
        geometry = THREE.PlaneGeometry.new(1, 1, 1)
        material = THREE.MeshBasicMaterial.new(perms)
        plane = THREE.Mesh.new(geometry, material)
        plane.scale.x = 1.414

        # Snap the plane to its slot
        (x, y, z), (nx, ny, nz), (w, h) = get_painting_info(PAINTINGS[slot])
        plane.position.set(x, y, z)

        q = THREE.Quaternion.new()
        q.setFromUnitVectors(THREE.Vector3.new(-1, 0, 0), THREE.Vector3.new(nx, ny, nz))
        plane.quaternion.copy(q)

        # Add the plane to the scene
        plane.name = f"picture_{slot:03d}"
        SCENE.add(plane)

    textureLoader.load(
        REPO_URL + image_loc,
        create_proxy(inner_loader),
    )


async def load_images_from_listing() -> None:
    # r = await pyfetch(REPO_URL + "../" + "test-image-listing.json")
    r = await pyfetch("./assets/test-image-listing.json")
    data = await r.text()
    images = json.loads(data)

    for idx, img in enumerate(images):
        load_image(img, idx)


def create_room(
    chunk_coords: tuple[int, int],
    room_apothem: float,
    room_type: ROOM_TYPES,
    rotation: float = 0,
) -> None:
    """
    chunk_coords represent the coordinates of the room
    room_apothem is the perp distance from the center of the room to its edges
    room_type represents the type of the room
    rotation represents the rotation of the room, which is supposed to be multiples of pi/2
    """

    room = GALLERY_BLOCKS[room_type].clone()
    room.name = f"room_{chunk_coords[0]}_{chunk_coords[1]}"
    ROOMS.append(room)

    position = (chunk_coords[0] * room_apothem * 2, 0, chunk_coords[1] * room_apothem * 2)
    room.rotation.y = rotation
    room.position.set(*position)

    # Add its children to a global list of paintings
    for i in room.getObjectByName("Pictures").children:
        i.name = f"pic_{len(PAINTINGS):03d}"
        PAINTINGS.append(i)

    SCENE.add(room)


async def clone_rooms(chunks: list[tuple[int, int]], layout: MAP, apothem: float):
    for x, y in chunks:
        room, rotation = get_gallery_room(x, y, layout)
        create_room((x, y), apothem, room, rotation)
        # print(f"Generated ({x}, {y})")


# -------------------------------------- GALLERY LOADING --------------------------------------
print("GALLERY LOADING")


def generate_global_lights():
    # Global lighting
    ambient_light = THREE.AmbientLight.new(0xFF_FF_FF, 0.5)
    # Lighting for floors
    hemi_light = THREE.HemisphereLight.new(0xFF_FF_FF, 0x44_44_44, 0.2)
    hemi_light = THREE.HemisphereLight.new(0x0, 0xFF_FF_FF, 0.3)
    # Adds some depth
    main_light = THREE.DirectionalLight.new(0xFF_FF_FF, 1.2)
    main_light.position.set(10, 20, 10)
    main_light.castShadow = True

    SCENE.add(ambient_light)
    SCENE.add(hemi_light)
    SCENE.add(main_light)

    # Sexy reflections
    loader = RGBELoader.new()

    def inner_loader(loaded_obj, *_):
        pmrem = THREE.PMREMGenerator.new(RENDERER)
        env_map = pmrem.fromEquirectangular(loaded_obj).texture
        SCENE.environment = env_map
        loaded_obj.dispose()
        pmrem.dispose()

    loader.load(
        "./assets/lebombo_1k.hdr",
        create_proxy(inner_loader),
    )


async def load_gallery_blocks() -> None:
    loader = GLTFLoader.new()

    # Needs to do it this way or python will reference the same 'i'
    def inner_loader_factory(i: ROOM_TYPES) -> Callable[[Any], None]:
        def inner_loader(loaded_obj):
            room = loaded_obj.scene
            # Backface culling, invisible objects, etc.
            room_objects_handling(room)
            GALLERY_BLOCKS[i] = room

        return inner_loader

    def inner_progress(xhr):
        print(str(xhr.loaded) + " loaded")

    def inner_error(error):
        print(f"error: {error}")

    inner_progress_proxy = create_proxy(inner_progress)
    inner_error_proxy = create_proxy(inner_error)

    for i in ROOM_TYPES:
        inner_loader = inner_loader_factory(i)

        loader.load(
            f"./assets/gallery_{i.value}.glb",
            create_proxy(inner_loader),
            inner_progress_proxy,
            inner_error_proxy,
        )

    # Ensure they are loaded
    while True:
        for i in ROOM_TYPES:
            if i not in GALLERY_BLOCKS:
                await asyncio.sleep(0.02)
                break
        else:
            break

"""     # Ensure they are loaded
    all_loaded = False
    while not all_loaded:
        all_loaded = True
        for i in ROOM_TYPES:
            if i not in GALLERY_BLOCKS:
                all_loaded = False
                await asyncio.sleep(0.02)
                break
 """


def get_room_apothem() -> float:
    # Get the corner room, estimate distance from center
    room = GALLERY_BLOCKS[ROOM_TYPES._2c]
    assert room.children[0].name.startswith("Cube")
    # Centers
    cx, cz = room.position.x, room.position.z

    triggers: list[THREE.Group] = [i for i in room.getObjectByName("Triggers").children]
    trigger_centers: list[tuple[float, float]] = [(i.position.x, i.position.z) for i in triggers]

    apothems = [max(abs(cx - ix), abs(cz - iz)) for ix, iz in trigger_centers]
    output = sum(apothems) / len(apothems)
    print(f"Apothem: {output:.4f} ± {(max(apothems) - min(apothems)) / 2:.4f} metres")
    return output


async def load_gallery() -> None:
    print("Loading gallery rooms, map layout, and image listing")
    _, layout = await asyncio.gather(
        load_gallery_blocks(),
        get_map_layout(),
    )
    apothem = get_room_apothem()
    # Get all layout points, sorted by Hamiltonian distance from (0, 0)
    layout_points = sorted(
        [(x, y) for y in range(len(layout)) for x in range(len(layout)) if layout[y][x] is not None],
        key=lambda p: abs(p[0]) + abs(p[1]),
    )
    await clone_rooms(layout_points, layout, apothem)
    await load_images_from_listing()


async def main():
    while not SCENE.getObjectByName("room_0_0"):
        print("Waiting for the initial room to load...")
        await asyncio.sleep(0.05)
    print("Initial room loaded")

    clock = THREE.Clock.new()
    while True:
        delta = clock.getDelta()
        velocity = move_character(delta)
        if velocity == THREE.Vector3.new(0, 0, 0):
            continue
        if check_collision(velocity, delta):
            CAMERA.position.addScaledVector(velocity, delta)

        RENDERER.render(SCENE, CAMERA)
        await asyncio.sleep(0.02)


if __name__ == "__main__":
    print("Loading gallery...")
    asyncio.ensure_future(load_gallery())
    generate_global_lights()
    print("Starting main loop...")
    asyncio.ensure_future(main())
