---
execute: true
---

```python
from IPython import display
from base64 import b64decode

base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVQI12Nk8HvOwMDAxMDAwMDAAAANvwE5JAfKNQAAAABJRU5ErkJggg=="
display.Image(b64decode(base64_data))
```
