# Ribbon preview/mockup tool

A browser-based tool for previewing ribbon placement on jacket images.

I made this to quickly iterate and mock up our 20 or so AO participation ribbon options, but this tool can naturally be used for any ribbon use case

Click and drag to place the medal on the jacket. Move with arrow buttons and keyboard arrows for pixel-perfect adjustments

Gaussian blur is applied to match the ribbon to the jacket's compression, feel free to change that with the blur field

## Usage

Open `medal_preview.html` in browser

There is also a standalone Python/tkinter version:

```
pip install Pillow
python medal_preview.py [base_image] [medal_image]
```

Enjoy!