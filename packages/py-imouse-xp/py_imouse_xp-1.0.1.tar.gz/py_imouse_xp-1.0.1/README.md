# py-imouse-xp

Python client library for iMouse device automation and control.

## Installation

```bash
pip install py-imouse-xp
```

## Quick Start

### Using the Legacy API

```python
import imouse

# Create a legacy API instance
client = imouse.legacy(host="localhost", port=9911, mode="websocket")

# Use the client for device control
```

### Using the New API

```python
import imouse

# Create a new API instance
client = imouse.api(host="localhost", port=9911, mode="websocket")

# Use the client for device control
```

## Features

- Device automation and control
- Mouse and keyboard simulation
- Image processing capabilities
- WebSocket and HTTP communication modes
- Legacy API compatibility

## Requirements

- Python 3.8+
- See requirements for full dependency list

## License

MIT License