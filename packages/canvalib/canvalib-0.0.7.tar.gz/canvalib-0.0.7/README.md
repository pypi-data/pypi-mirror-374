# Canvalib

###### by danb1551

Canvalib is library for window with diferent text and backround color in your terminal.

<video src="show.mp4" autoplay>show video</video>

## Installation
```bash
pip install canvalib
```

## Usage

#### Import library

```python
from canvalib import Canvas
```

#### Create object:

```python
c = Canvas(width, height, background, color)
```

All parameters is optional. If you are strugelling why WIDTH and HEIGHT are in default without maked with - 1 then it's because if not, it will do something strange even I don't know why.

WIDTH: default to terminal width - 1. If you add more than default (it depend on your terminal size) it will not work properly.

HEIGHT: default to terminal height - 1. If you add more than default (it depend on your terminal size) it will not work properly.

BACKGROUND: default to Back.BLACK. If you want to change it import Back from colorama and give Back.color to your char or string.

COLOR: default to Fore.GREEN. If you want to change it import Fore from colorama and give Fore.color to your char or string.

#### Add text to your canvas:

```python
c.add_text(x, y, text, color, background)
```

X: row of the canvas where your text will be. Notice that it's starting from 0 index.

Y: column of the canvas where your text will be. Notice that it's starting from 0 index.

TEXT: whatever you want

COLOR: default to self.color. Must be Fore.color or escape sequence that setting text color

BACKGROUND: default to self.background. Must be Back.color or escape sequence that setting background color

#### Render it:

```python
c.render()
```