# Rene Koch AG SIP Gateway — Home Assistant Integration

[![HACS Custom Repository](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.2%2B-blue.svg)](https://www.home-assistant.io)

A [HACS](https://hacs.xyz) custom integration for Home Assistant that connects to the **Rene Koch AG SIP Gateway** over its local HTTP API and exposes the video stream as a camera entity.

---

## Features

| Entity | Description |
|---|---|
| **Camera** | Live MJPEG video stream from the gateway |

---

## Requirements

- Home Assistant **2026.2** or newer
- Rene Koch AG SIP Gateway reachable on your local network
- The gateway's HTTP API port and video stream port must be accessible from the HA host

---

## Installation

### Via HACS (recommended)

1. Open HACS in your Home Assistant instance.
2. Go to **Integrations** → three-dot menu → **Custom repositories**.
3. Add this repository URL and select category **Integration**.
4. Click **Download** on the *Rene Koch AG SIP Gateway* card.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/koch_ag` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

1. Go to **Settings → Integrations → Add Integration**.
2. Search for **Rene Koch AG SIP Gateway**.
3. Fill in the form:

| Field | Default | Description |
|---|---|---|
| Host / IP address | — | IP or hostname of the gateway (e.g. `192.168.1.200`) |
| API port | `80` | Port of the gateway's HTTP REST API |
| Video stream port | `12000` | Port serving the MJPEG video stream |

4. Click **Submit**. The integration will test the connection before saving.

---

## Entities

### Camera — `camera.koch_ag_video`

Streams the MJPEG feed from `http://<host>:<video_port>/video.mjpeg`.
The entity appears under the **Koch AG Gateway** device in Home Assistant.

---

## Development

### Prerequisites

- Python 3.13+
- A virtual environment with dev dependencies installed

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run Home Assistant locally

```bash
.venv/bin/hass --config .ha-config
```

The `custom_components/` folder is symlinked into `.ha-config/` so changes are picked up after an HA restart.

### Lint & type-check

```bash
ruff check custom_components tests
mypy custom_components
```

### Tests

```bash
pytest
```

---

## License

[MIT](LICENSE)
