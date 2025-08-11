## PLACEHOLDER, TAKEN FROM:
## https://pyscript.com/@examples/webgl-icosahedron/latest

## DOCS
## https://threejs.org/docs/

from pyodide.ffi import to_js
from pyscript import when, window, document
from js import Math, THREE, performance, Object
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
SCENE.fog = THREE.Fog.new(setcolor, 2.5, 3.5)

CAMERA.lookAt(SCENE.position)

SCENE_GROUP = THREE.Object3D.new()
SCENE.add(SCENE_GROUP)

PARTICULAR_GROUP = THREE.Object3D.new()
SCENE_GROUP.add(PARTICULAR_GROUP)

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

def genearate_lights()->None:
    ambientLight = THREE.AmbientLight.new(0xFFFFFF, 0.1)
    SCENE.add(ambientLight)

    light = THREE.SpotLight.new(0xFFFFFF, 3)
    light.position.set(5, 5, 2)
    light.castShadow = True
    light.shadow.mapSize.width = 10000
    light.shadow.mapSize.height = light.shadow.mapSize.width
    light.penumbra = 0.5
    SCENE.add(light)

    lightBack = THREE.PointLight.new(0x0FFFFF, 1)
    lightBack.position.set(0, -3, -1)
    SCENE.add(lightBack)


    rectSize = 2
    intensity = 14
    rectLight = THREE.RectAreaLight.new(0x0FFFFF, intensity, rectSize, rectSize)
    rectLight.position.set(0, 0, 1)
    rectLight.lookAt(0, 0, 0)
    SCENE.add(rectLight)

def create_cubes(mathRandom, modularGroup):
    i = 0
    while i < 30:
        geometry = THREE.IcosahedronGeometry.new()
        perms = Object.fromEntries(
            to_js(
                {
                    "flatShading": True,
                    "color": "#111111",
                    "transparent": False,
                    "opacity": 1,
                    "wireframe": False,
                }
            )
        )

        material = THREE.MeshStandardMaterial.new(perms)
        cube = THREE.Mesh.new(geometry, material)
        cube.speedRotation = Math.random() * 0.1
        cube.positionX = mathRandom()
        cube.positionY = mathRandom()
        cube.positionZ = mathRandom()
        cube.castShadow = True
        cube.receiveShadow = True
        newScaleValue = mathRandom(0.3)
        cube.scale.set(newScaleValue, newScaleValue, newScaleValue)
        cube.rotation.x = mathRandom(180 * Math.PI / 180)
        cube.rotation.y = mathRandom(180 * Math.PI / 180)
        cube.rotation.z = mathRandom(180 * Math.PI / 180)
        cube.position.set(cube.positionX, cube.positionY, cube.positionZ)
        modularGroup.add(cube)
        i += 1


def generateParticle(mathRandom, particularGroup, num, amp=2):
    particle_perms = {"color": "#FFFFFF", "side": THREE.DoubleSide}
    particle_perms = Object.fromEntries(to_js(particle_perms))

    gmaterial = THREE.MeshPhysicalMaterial.new(particle_perms)
    gparticular = THREE.CircleGeometry.new(0.2, 5)
    i = 0
    while i < num:
        pscale = 0.001 + Math.abs(mathRandom(0.03))
        particular = THREE.Mesh.new(gparticular, gmaterial)
        particular.position.set(mathRandom(amp), mathRandom(amp), mathRandom(amp))
        particular.rotation.set(mathRandom(), mathRandom(), mathRandom())
        particular.scale.set(pscale, pscale, pscale)
        particular.speedValue = mathRandom(1)
        particularGroup.add(particular)
        i += 1


async def main():
    while True:
        time = performance.now() * 0.0003
        i = 0
        while i < PARTICULAR_GROUP.children.length:
            newObject = PARTICULAR_GROUP.children[i]
            newObject.rotation.x += newObject.speedValue / 10
            newObject.rotation.y += newObject.speedValue / 10
            newObject.rotation.z += newObject.speedValue / 10
            i += 1

        i = 0
        while i < MODULAR_GROUP.children.length:
            newCubes = MODULAR_GROUP.children[i]
            newCubes.rotation.x += 0.008
            newCubes.rotation.y += 0.005
            newCubes.rotation.z += 0.003

            newCubes.position.x = (
                Math.sin(time * newCubes.positionZ) * newCubes.positionY
            )
            newCubes.position.y = (
                Math.cos(time * newCubes.positionX) * newCubes.positionZ
            )
            newCubes.position.z = (
                Math.sin(time * newCubes.positionY) * newCubes.positionX
            )
            i += 1

        PARTICULAR_GROUP.rotation.y += 0.005

        uSpeed = 0.1
        MODULAR_GROUP.rotation.y -= ((MOUSE.x * 4) + MODULAR_GROUP.rotation.y) * uSpeed
        MODULAR_GROUP.rotation.x -= ((-MOUSE.y * 4) + MODULAR_GROUP.rotation.x) * uSpeed

        RENDERER.render(SCENE, CAMERA)
        await asyncio.sleep(0.02)


if __name__ == "__main__":
    generate_lights()
    create_cubes(mathRandom, MODULAR_GROUP)
    generateParticle(mathRandom, PARTICULAR_GROUP, 200, 2)
    asyncio.ensure_future(main())
