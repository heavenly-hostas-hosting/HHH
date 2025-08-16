## PLACEHOLDER, TAKEN FROM:			# think we can remove this now, basically deleted most of their code
## https:#pyscript.com/@examples/webgl-icosahedron/latest

## DOCS
## https:#threejs.org/docs/


# -------------------------------------- IMPORTS --------------------------------------
print('IMPORTS')

from pyodide.ffi import to_js, create_proxy  # pyright: ignore[reportMissingImports]
from pyodide.http import pyfetch  # pyright: ignore[reportMissingImports]
from pyscript import when, window, document  # pyright: ignore[reportMissingImports]
from js import (  # pyright: ignore[reportMissingImports]
    Math,
    THREE,
    Object,
    GLTFLoader,
    PointerLockControls,
)


from collections import defaultdict
from enum import Enum
import asyncio
import json


# -------------------------------------- GLOBAL VARIABLES --------------------------------------
print('GLOBAL VARIABLES')

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

# Other global variables
ROOMS: list[THREE.Group] = []   # a list of all rooms in the scene
LOADED_ROOMS: list[THREE.Group] = []  # a list of all loaded rooms (or the loaded chunks)
CURRENT_ROOM: THREE.Group = None  # the room in which the player currently is
ROOM_SIZE = [11.5, 4.2, 11.5]

OFFSET = 0.1  # distance which we maintain from walls
TRIGGER_COLLISION = False  # whether we are currently colliding with a trigger

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
print('HELPER FUNCTIONS')

# def log(*msgs):
#     for msg in msgs:
#         console.log(msg)

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
    position: V3 = p.position.x, p.position.y, p.position.z

    n_array = p.geometry.attributes.normal.array
    # Beware possible Y-up/Z-up shenanigans
    normal: V3 = (-n_array[2], n_array[1], n_array[0])
    id_ = int(p.name[-3:])
    print(id_, normal)

    bb = p.geometry.boundingBox
    size_xyz = [abs(getattr(bb.max, i) - getattr(bb.min, i)) for i in ("x", "y", "z")]
    # Height is Z
    size_wh: V2 = (max(size_xyz[0], size_xyz[1]), (size_xyz[2]))

    return (position, normal, size_wh)


def get_chunk_coords() -> tuple[int, int]:
    x_coord = (CAMERA.position.x - ROOM_SIZE[0]/2) // ROOM_SIZE[0]
    z_coord = (CAMERA.position.z - ROOM_SIZE[2]/2) // ROOM_SIZE[2]

    if x_coord < 0: x_coord = 0
    if z_coord < 0: z_coord = 0

    return x_coord, z_coord


# -------------------------------------- MOVEMENT CONTROLS --------------------------------------
print('MOVEMENT CONTROLS')

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

# Global variable to toggle running
RUN_STATE = False


def toggle_run(event):
    global RUN_STATE
    if event.code in KEY_MAPPINGS[INPUTS.RUN]:
        RUN_STATE = not RUN_STATE


document.addEventListener("keydown", create_proxy(toggle_run))


# Main move function
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
    return VELOCITY


# -------------------------------------- MOUSE CONTROLS --------------------------------------
print('MOUSE CONTROLS')

MOUSE = THREE.Vector2.new()

# Mouse Lock
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

# Mouse Controls
@when("mousemove", "body")
def onMouseMove(event):
    event.preventDefault()
    MOUSE.x = (event.clientX / window.innerWidth) * 2 - 1
    MOUSE.y = -(event.clientY / window.innerHeight) * 2 + 1


# -------------------------------------- COLLISION DETECTION --------------------------------------
print('COLLISION DETECTION')

def check_collision(velocity: THREE.Vector3, delta_time: float) -> bool:
    '''
    Checks for collision with walls (cubes) and triggers
    returns true if it is safe to move and false if movement should be stopped
    '''
    # print("Checking collision with walls and triggers...")
    # print(CURRENT_ROOM)
    raycaster = THREE.Raycaster.new()
    direction = velocity.clone().normalize()
    raycaster.set(CAMERA.position, direction)

    check_collision_with_trigger(velocity, delta_time, raycaster)

    return check_collision_with_wall(velocity, delta_time, raycaster)

def check_collision_with_wall(velocity: THREE.Vector3, delta_time: float, raycaster: THREE.Raycaster) -> bool:
    # print('walls', CURRENT_ROOM.name)
    cubes = []
    [cubes.extend(c.getObjectByName("Cubes").children) for c in LOADED_ROOMS]
    intersections = raycaster.intersectObjects(cubes, recursive=True)
    if not intersections:
        return True
    return intersections[0].distance > velocity.length() * delta_time + OFFSET

def check_collision_with_trigger(velocity: THREE.Vector3, delta_time: float, raycaster: THREE.Raycaster):
    global CURRENT_ROOM, TRIGGER_COLLISION
    # print('trigger', CURRENT_ROOM.name)

    triggers = []
    [triggers.extend(c.getObjectByName("Triggers").children) for c in LOADED_ROOMS]

    intersections = raycaster.intersectObjects(triggers, recursive=True)
    if intersections and intersections[0].distance <= velocity.length() * delta_time:
        if not TRIGGER_COLLISION:
            TRIGGER_COLLISION = True
    else:
        if TRIGGER_COLLISION:
            TRIGGER_COLLISION = False
            print("Exited trigger area")

            calc = lambda x, y: (x - y/2) // y

            """
            coords = get_chunk_coords()
            CURRENT_ROOM = SCENE.getObjectByName(f"room_{int(coords[0])}_{int(coords[1])}")
            print("UPDATED CURRENT ROOM", CURRENT_ROOM.name)
            load_room()
            """


# -------------------------------------- ROOM CREATION --------------------------------------
print('ROOM CREATION')

def generate_lights() -> THREE.Group:
    light_main = THREE.SpotLight.new(0xFF_FF_FF, 3)
    light_main.position.set(5, 5, 2)
    light_main.castShadow = True
    light_main.shadow.mapSize.width = 10000
    light_main.shadow.mapSize.height = light_main.shadow.mapSize.width
    light_main.penumbra = 0.5

    light_back = THREE.PointLight.new(0xEF_FF_FF, 1)
    light_back.position.set(0, -3, -1)

    ambient_light = THREE.AmbientLight.new(0xFFFFFF, 0.3)

    lights = THREE.Group.new()
    lights.add(light_main)
    lights.add(light_back)
    lights.add(ambient_light)

    return lights


def load_image(image_loc: str) -> THREE.Texture:
    textureLoader = THREE.TextureLoader.new()
    texture = textureLoader.load(REPO_URL + image_loc)
    return texture


def create_plane(texture: THREE.Texture) -> THREE.Mesh:
    perms = convert_dict_to_js_object(
        {
            "map": texture,
            "transparent": True,
        }
    )

    geometry = THREE.PlaneGeometry.new(1, 1, 1)
    material = THREE.MeshBasicMaterial.new(perms)
    plane = THREE.Mesh.new(geometry, material)

    plane.scale.x = 1.414  # as HiPeople said the aspect ratio is 1 : sqrt2

    return plane


async def snap_to_slot(photo: THREE.Group, slot: int, picture_grp: THREE.Group) -> None:
    # while not PAINTING_SLOTS:
    #     await asyncio.sleep(0.05)
    (x, y, z), (nx, ny, nz), (w, h) = get_painting_info(picture_grp.children[slot])
    photo.position.x = x
    photo.position.y = y
    photo.position.z = z

    q = THREE.Quaternion.new()
    q.setFromUnitVectors(THREE.Vector3.new(-1, 0, 0), THREE.Vector3.new(nx, ny, nz))
    photo.quaternion.copy(q)


async def create_photoframe(image_loc, slot: int, picture_grp: THREE.Group) -> THREE.Group:
    texture = load_image(image_loc)
    plane = create_plane(texture)

    photo = THREE.Object3D.new()
    photo.add(plane)

    await snap_to_slot(photo, slot, picture_grp)
    photo.name = f"picture_{slot:03d}"
    picture_grp.add(photo)

    return photo


async def load_images_from_listing(room: THREE.Group) -> None:
    r = await pyfetch(REPO_URL + "../" + "test-image-listing.json")
    data = await r.text()
    images = json.loads(data)

    while not room.getObjectByName("Pictures"):
        await asyncio.sleep(0.05)
    picture_grp = room.getObjectByName("Pictures")

    for idx, img in enumerate(images):
        asyncio.ensure_future(create_photoframe(img, idx, picture_grp))


def room_objects_handling(room: THREE.Group) -> THREE.Group:
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
            # v.visible = False
            # size_xyz = [1, 4.2, 1.8]

        if v.name.startswith("pic"):
            room.remove(v)
            pictures.add(v)
            v.visible = False
    
    room.add(triggers)
    room.add(pictures)

    return pictures


async def create_room(chunk_coords: tuple[int, int] = (0, 0), rotation: int = 0, room_type: int = 0) -> THREE.Group:
    '''
    chunk_coords represent the coordinates of the room
    rotation represents the rotation of the room, which is supposed to be multiples of pi/2
    room_type represents the type of the room (TODO)
    '''

    lights = generate_lights()
    print("Lights generated")

    gltf = None

    def inner_loader(loaded_obj):
        nonlocal gltf
        gltf = loaded_obj

    def inner_progress(xhr):
        print(str(xhr.loaded) + " loaded")

    def inner_error(error):
        print(f"error: {error}")

    loader = GLTFLoader.new()
    loader.load(
        "./assets/gallery_2c.glb",
        create_proxy(inner_loader),
        create_proxy(inner_progress),
        create_proxy(inner_error),
    )

    while not gltf:
        await asyncio.sleep(0.05)

    print('loaded gltf')
    obj = gltf.scene
    # obj.visible = False
    obj.name = f"room_{chunk_coords[0]}_{chunk_coords[1]}"
    ROOMS.append(obj)

    # Backface culling
    picture_grp = room_objects_handling(obj)

    print(f"Loading done! Here's its component structure:")
    print(tree_print(obj))
    print(f"Number of painting slots:", len(picture_grp.children))

    room = gltf.scene
    position = (chunk_coords[0] * ROOM_SIZE[0], 0, chunk_coords[1] * ROOM_SIZE[2])
    room.position.set(*position)
    room.rotation.y = rotation * 1.57


    await load_images_from_listing(room)

    room.add(lights)
    SCENE.add(room)

    return room


# -------------------------------------- GALLERY LOADING --------------------------------------
print('GALLERY LOADING')

async def load_gallery() -> None:
    print("Creating first room")
    await create_room((0, 0), 2)
    print("Creating second room")
    await create_room((0, 1), 3)
    await create_room((1, 0), 1)
    await create_room((1, 1), 0)


""" def load_room(r: int = 3) -> None:
    '''
    Loads all rooms which are at r distance from the current room
    '''
    print("Loading rooms...")
    for room in ROOMS:
        if room not in LOADED_ROOMS:
            if room.position.distanceTo(CAMERA.position) < r * ROOM_SIZE[0]:
                room.visible = True
                LOADED_ROOMS.append(room)
                print(f"Room {room.name} loaded at position {room.position.toArray()}")
            else:
                print(f"Room {room.name} is too far away, not loading it.")
    pass
 """

async def main():
    global CURRENT_ROOM

    while not SCENE.getObjectByName("room_0_0"):
        print("Waiting for the initial room to load...")
        await asyncio.sleep(0.05)
    print("Initial room loaded")
    CURRENT_ROOM = SCENE.getObjectByName("room_0_0")
    # load_room()

    clock = THREE.Clock.new()
    while True:
        delta = clock.getDelta()
        velocity = move_character(delta)
        if check_collision(velocity, delta):
            CAMERA.position.addScaledVector(velocity, delta)

        RENDERER.render(SCENE, CAMERA)
        await asyncio.sleep(0.02)


if __name__ == "__main__":
    print("Loading gallery...")
    asyncio.ensure_future(load_gallery())
    print("Starting main loop...")
    asyncio.ensure_future(main())
