This is the image gallery part of the project. The final product can be accessed [here!!](https://heavenly-hostas-hosting.github.io/HHH/)

## Concept

This is the section of the project that manages the Image Gallery. It's a 3D place that has on display every picture that every user has ever posted on the app.

You are able to navigate the room in 3D from a first-person perspective, being able to fly around the place. You also have the ability to share its different artworks by generating a link that will place you on the exact spot to admire said piece in all of its glory.

## Development

We utilize the [*pyscript*](https://github.com/pyscript/pyscript) framework, which allows the execution of Python code inside the browser, including also some very useful interop with JavaScript. This last feature has been very important for the making of this section, as it allows us to have [three.js](https://github.com/mrdoob/three.js) bindings that enable fast 3D rendering in the web browser (the interface in question being similar to how you can use compiled *C* code through libraries like *numpy*). The use of said APIs along with some homemade assets built with Blender (all source files in the repo) have made this project possible.

Only external asset used is the free [HDRi image 'Lebombo' by Greg Zaal (CC0)](https://polyhaven.com/a/lebombo), thank you Greg!!

## Dev guide

The easiest way to test the website locally is just to run a basic HTTP server. You can do that in Python by running the following in the directory that contains this file:

```
python3 -m http.server
```

If you run the project locally you might also encounter issues with CORS permissions as the page is intended to access an external, global repository. To substitute said repo with a local placeholder for testing purposes, you can set the `USE_LOCALHOST` global to `True` on `./main.py`.

