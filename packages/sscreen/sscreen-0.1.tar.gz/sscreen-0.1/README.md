# SScreen (PyQt6)

SScreen is a modern GUI library built on PyQt6.

## Features
- Window with custom icon
- Buttons, Labels with styles
- Basic animations (to be added)
- Light/Dark theme support

## Example
```python
from sscreen.window import SScreenWindow
from sscreen.widgets import SButton, SLabel

app = SScreenWindow(title='My PyQt6 SScreen')
label = SLabel(app, text='Hello SScreen!')
label.move(50,50)
label.resize(200,30)
app.run()
```
