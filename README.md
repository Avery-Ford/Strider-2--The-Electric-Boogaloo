# lil-strider (striderbot)

Python controller for a hexapod robot with 18 servos on two 16-channel servo
boards. It accepts Blender bone-angle messages over WebSocket and provides a
command-line tool for setting servo angles directly. The Blender client and
scene are not included in this repository.

- [Setup and execution](docs/setup.md): environment, hardware configuration,
  commands, message format, and troubleshooting.
- [Code architecture](docs/architecture.md): modules, device registry, and
  command processing.
- [Packages](docs/packages.md): direct dependencies and the locked dependency tree.

## Quick start

Requires Python 3.11 or newer, `uv`, and a host with working I²C access supported
by the Adafruit hardware libraries. Run from the repository root:

```sh
uv sync --locked
mkdir -p .log
test -f .env || cp .env.example .env
```

Review `config.json` against the connected boards and servo calibration, and
set `BLENDER_URL` in `.env` to the local address on which the server should
listen. Then start the controller:

```sh
uv run --locked python src/main.py
```

The default endpoint is `ws://localhost:8080`. Incoming commands move hardware;
read the [setup guide](docs/setup.md) before sending them. There is no simulator
or dry-run mode. These instructions describe the source code; hardware and
end-to-end Blender operation have not been validated as part of this documentation.
