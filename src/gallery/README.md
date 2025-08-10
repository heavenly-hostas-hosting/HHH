**Warning: incomplete. TODOS in the Issues section, comment 'dibs' if you want to solve it yourself.**

## Concept

This is the section of the project that manages the Image Gallery. It's a 3D place that has on display every picture that every user has ever posted on the app.

You are able to navigate the room in 3D from a first-person perspective, being able to fly around the place. You also have the ability to share its different artworks by generating a link that will place you on the exact spot to admire said piece in all of its glory.

## Development

We utilize the [*pyscript*](https://github.com/pyscript/pyscript) framework, which allows the execution of Python code inside the browser, including also some very useful interop with JavaScript. This last feature has been very important for the making of this section, as it allows us to have [three.js](https://github.com/mrdoob/three.js) bindings that enable fast 3D rendering in the web browser (the interface in question being similar to how you can use compiled *C* code through libraries like *numpy*).
