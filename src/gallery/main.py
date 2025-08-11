## PLACEHOLDER, TAKEN FROM:
## https://pyscript.com/@examples/webgl-icosahedron/latest

## DOCS
## https://threejs.org/docs/

from pyodide.ffi import create_proxy, to_js
from pyscript import when, window, document
from js import Math, THREE, performance, Object, GLTFLoader
import asyncio

RENDERER = THREE.WebGLRenderer.new({"antialias": False})
document.body.appendChild(RENDERER.domElement)
RENDERER.setSize(1000, 1000)
RENDERER.shadowMap.enabled = False
RENDERER.shadowMap.type = THREE.PCFSoftShadowMap
RENDERER.shadowMap.needsUpdate = True
RENDERER.setSize(window.innerWidth, window.innerHeight)

CAMERA = THREE.PerspectiveCamera.new(35, window.innerWidth / window.innerHeight, 1, 500)
cameraRange = 3
CAMERA.position.set(0, 0, cameraRange)

setcolor = "#000000"
SCENE = THREE.Scene.new()
SCENE.background = THREE.Color.new(setcolor)
# SCENE.fog = THREE.Fog.new(setcolor, 2.5, 3.5)

CAMERA.lookAt(SCENE.position)

MODULAR_GROUP = THREE.Object3D.new()
SCENE.add(MODULAR_GROUP)


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

        obj.scale.x = 0.25
        obj.scale.y = 0.25
        obj.scale.z = 0.25

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
    while True:
        uSpeed = 0.1
        MODULAR_GROUP.rotation.y -= ((MOUSE.x * 4) + MODULAR_GROUP.rotation.y) * uSpeed
        MODULAR_GROUP.rotation.x -= ((-MOUSE.y * 4) + MODULAR_GROUP.rotation.x) * uSpeed

        RENDERER.render(SCENE, CAMERA)
        await asyncio.sleep(0.02)


if __name__ == "__main__":
    generate_lights()
    load_gallery()
    asyncio.ensure_future(main())
