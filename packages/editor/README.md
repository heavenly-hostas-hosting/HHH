## Dev Guide
### Intended Use
To run this package as intended, please see the [backend package README](https://github.com/heavenly-hostas-hosting/HHH/blob/main/packages/backend/README.md).
### Standalone Execution
If you wish to run this package as a standalone webapp, first install [`NiceGUI`](https://pypi.org/project/nicegui/).
Then, in `main.py` remove the `root_path` argument in `ui.run`, as shown below.

From:
```py
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=9010, title="HHH Editor", root_path="/editor")
```
To:
```py
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=9010, title="HHH Editor")
```
Then run the file such as below.
```
python3 packages/editor/main.py
```

## Concept

This part of the project is an image editor, meant to be similar to apps such as Microsoft Paint.

You can:
- Draw lines or pixels, depending on the mode you select. Changing modes will clear the canvas. Pixel mode is limited in features. [`p`] for pen mode.
- Erase lines/pixels. [`e`] for eraser mode.
- Smudge. [`s`] for smudge mode.
- Clip regions. [`c`] for clip mode.
- Draw circles, squares, triangles, stars, and the Python logo.
- Use a different colour via a slot machine-esque spinner. [`a`] to spin.
- Change line width.
- Add text. You can choose for the text to be bolded and/or italicised. You can also choose the font.
- Upload images.
- Undo/redo. [`ctrl` + `z`] and [`ctrl` + `shift` + `z`] respectively.
- Download your creations.
- Clear the canvas.
- Clipped regions, uploaded images, and text can all be resized or rotated. Using a scrollwheel or a similar device changes the size, and using [`Alt` + `Left Arrow`] or [`Alt` + `Right Arrow`] rotates the region
counterclockwise and clockwise respectively. Pressing [`backspace`] will remove the region.
- Open the help menu [`?`].

Keybinds are in the square brackets. Additional details are in a help menu.

To publish your art to the gallery, click the `Register` button and follow the instructions. After logging in clicking the `Publish` button should add your piece
to the gallery.

## Development

We used [`Pyscript`](https://pyscript.com/) and [`NiceGUI`](https://nicegui.io/) for this part of the project. NiceGUI was used to create the UI, and Pyscript
was used to control the drawing features, via the [Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API).

