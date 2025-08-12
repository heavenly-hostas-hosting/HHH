## PLACEHOLDER, TAKEN FROM:			# think we can remove this now, basically deleted most of their code
## https:#pyscript.com/@examples/webgl-icosahedron/latest

## DOCS
## https:#threejs.org/docs/

from pyodide.ffi import to_js, create_proxy
from pyscript import when, window, document
from js import Math, THREE, Object, console
import asyncio

def log(*msgs):
	for msg in msgs:
		console.log(msg)

""" Previous way of handling log
output_div = document.createElement('div')
output_div.id = 'output_div'
document.body.appendChild(output_div)
def log(msg):
	new_p = document.createElement('p')
	new_p.innerHTML = msg
	output_div.appendChild(new_p)
 """

RENDERER = THREE.WebGLRenderer.new({"antialias": False})
RENDERER.shadowMap.enabled = False
RENDERER.shadowMap.type = THREE.PCFSoftShadowMap
RENDERER.shadowMap.needsUpdate = True
RENDERER.setSize(window.innerWidth, window.innerHeight)
document.body.appendChild(RENDERER.domElement)

CAMERA = THREE.PerspectiveCamera.new(75, window.innerWidth / window.innerHeight, 0.1, 1000)
cameraRange = 5
CAMERA.position.set(0, 0, cameraRange)

setcolor = "#8B8B8B"		# helps to differentiate the "plane" from the bg
SCENE = THREE.Scene.new()
SCENE.background = THREE.Color.new(setcolor)

CAMERA.lookAt(SCENE.position)


def mathRandom(num=1):
	setNumber = -Math.random() * num + Math.random() * num
	return setNumber


def load_image():
	textureLoader = THREE.TextureLoader.new()
	texture = textureLoader.load(
		'assets/images/test-image-nobg.png',
		create_proxy(lambda e: create_plane(texture)),
		create_proxy(log),
		create_proxy(log)
	)


def create_plane(texture):
	perms = Object.fromEntries(to_js({
		"map": texture,
		# "color": "#A6D32B",			# the color makes it look wierd so commented it
	}))
	
	geometry = THREE.PlaneGeometry.new(1, 1, 1)
	material = THREE.MeshBasicMaterial.new(perms)
	plane = THREE.Mesh.new(geometry, material)
	SCENE.add(plane)

	RENDERER.render(SCENE, CAMERA)	# so that we render the scene after loading the texture (wont be a problem if we render continuously)


async def main():
	load_image()

log('Running')

if __name__ == "__main__":
	log('Inside IF')
	asyncio.ensure_future(main())	   # can remove the async as no await is used
