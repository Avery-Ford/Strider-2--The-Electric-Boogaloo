# Setup and execution

## Prerequisites

- Python 3.11 or newer; `.python-version` selects 3.11.
- `uv` available on your command path for the commands below.
- A host with working I²C access supported by Adafruit Blinka and ServoKit.
  Installing the Python packages alone does not configure the host's I²C bus.
- Two connected 16-channel servo boards matching `config.json`: `hat1` at
  `0x41` and `hat2` at `0x40`, with suitable servo power and wiring.

Board-specific wiring, power requirements, and OS I²C setup are not specified
in this repository. Confirm them for your hardware before running a controller.
The configured 270-degree travel and 500–2500 µs pulse range must match your
servos and mechanical limits.

## Install and configure

Run all commands from the repository root. Both entry points load `config.json`
relative to the current working directory, and logging uses `.log/` there.

```sh
uv sync --locked
mkdir -p .log
test -f .env || cp .env.example .env
```

`uv sync --locked` installs the versions recorded in `uv.lock` into `.venv`.
The conditional copy preserves an existing `.env`.

Set the following value in `.env` as needed:

```dotenv
BLENDER_URL="localhost"
```

Despite its name and the comment in `.env.example`, `BLENDER_URL` is the
WebSocket server's local bind host, not the address of a remote Blender server.
Use a hostname or IP without `ws://` or a port. The port is fixed at `8080` in
`src/main.py`. `localhost` accepts local clients; `0.0.0.0` listens on all IPv4
interfaces. A remote Blender client connects to `ws://<robot-host-ip>:8080`,
not to `0.0.0.0`. The server has no authentication or TLS configuration, so
limit access to a trusted network. An existing process environment variable
takes precedence over the `.env` value.

## Hardware configuration

`config.json` contains two sections. Keep `ServoHat` before `Servo`: devices are
created in file order, and each servo looks up an already-created hat.

| Section | Field | Meaning |
| --- | --- | --- |
| `ServoHat` | `address` | Integer I²C address or string, such as `"0x41"` |
| `ServoHat` | `address_base` | Optional base for parsing string addresses; defaults to 16 |
| `Servo` | `hat` | Identifier from `ServoHat`, such as `"hat1"` |
| `Servo` | `channel` | Board channel, 0–15 |
| `Servo` | `min_pulse` | Optional minimum pulse width in µs; defaults to 500 |
| `Servo` | `max_pulse` | Optional maximum pulse width in µs; defaults to 2500 |

The current wiring map is:

| Servos | Hat | Channels, in servo order |
| --- | --- | --- |
| `servo1`–`servo3` | `hat1` (`0x41`) | 0, 1, 2 |
| `servo4`–`servo6` | `hat1` (`0x41`) | 4, 5, 6 |
| `servo7`–`servo9` | `hat1` (`0x41`) | 8, 9, 10 |
| `servo10`–`servo12` | `hat2` (`0x40`) | 5, 6, 7 |
| `servo13`–`servo15` | `hat2` (`0x40`) | 9, 10, 11 |
| `servo16`–`servo18` | `hat2` (`0x40`) | 13, 14, 15 |

The parser sets every servo's `actuation_range` to 270 degrees in code; there
is no JSON setting for that range. Software angle limits do not establish safe
mechanical travel for a particular assembly.

## Run the WebSocket server

```sh
uv run --locked python src/main.py
```

Hardware initialization happens before the server starts listening. A successful
startup prints `WebSocket server started on ws://localhost:8080` with the selected
host. Stop with Ctrl+C. Shutdown does not explicitly disable servo outputs or
move the robot to a resting pose.

Clients send a JSON object whose keys are exact Blender bone paths and whose
values can be converted by Python's `int()`. For example:

```json
{
  "Armature.000.Bone.01.Bone.02": 0,
  "Armature.000.Bone.01.Bone.02.Bone.00": -10,
  "Armature.000.Bone.01.Bone.02.Bone.00.Bone.03": 20
}
```

This commands `servo1`, `servo2`, and `servo3` to 90, 80, and 110 degrees.
The server adds a fixed 90-degree offset after integer conversion. Numeric
strings such as `"20"` work; decimal strings such as `"20.5"` do not. There is
no radians-to-degrees conversion or application-level clamping.

For `Armature.000` through `Armature.005`, the three suffixes shown above map
to consecutive groups of three servos, from `servo1`–`servo3` through
`servo16`–`servo18`. See `BLENDER_LEG_TO_SERVO` in `src/main.py` for the full map.
Unknown keys are ignored. Omitted servos receive no new command. The server
does not return acknowledgments or servo telemetry.

Malformed JSON, non-object messages, and invalid angle values are not handled
as recoverable input errors and can terminate that client's handler. Servo
write errors are printed by the worker, which continues processing. A full
1,000-command queue drops newly arriving commands.

## Set angles directly

Stop the WebSocket controller before using a second program to control the same
boards. The following example moves `servo1` to an absolute angle of 90 degrees:

```sh
uv run --locked python src/arm.py --servo 1 --angle 90
```

The CLI does not apply the WebSocket's 90-degree offset. `--angle` (or `-a`)
defaults to 0. `--servo` (or `-s`) selects a servo by number. It still initializes
all devices from `config.json`, so both configured boards must be available.

Without `--servo`, the current implementation commands only servos 1–17
because it uses `range(1, 18)`, despite describing the target as “all.” Servo 18
can be commanded explicitly:

```sh
uv run --locked python src/arm.py --servo 18 --angle 90
```

View CLI options without configuring hardware (hardware-library imports still occur):

```sh
uv run --locked python src/arm.py --help
```

`src/testScript/libCode.py` and `src/testScript/libCode copy.py` are standalone
hardware experiments, not automated tests. They bypass configuration and
continuously write 180 degrees to channel 1 or 0 degrees to channel 0,
respectively, on the board at `0x41`, without a delay.

## Logs and troubleshooting

Device setup and servo actions log at Debug level by default to
`.log/<timestamp>.<entrypoint>.Debug.log`. Connection messages, received payloads,
and worker errors are printed to the terminal.

| Symptom | Check |
| --- | --- |
| Log file creation fails | Create `.log` in the repository root and run there. |
| `config.json` not found | Run the command from the repository root. |
| Hardware initialization fails | Check host support, I²C enablement/permissions, board power, wiring, and addresses. |
| `Hat was not found` | Put `ServoHat` before `Servo`; match the `hat` identifier exactly. |
| Remote client cannot connect | Check bind host, robot IP, firewall, and port 8080. |
| Server cannot bind | Use an address belonging to this host and ensure port 8080 is free. |
| No movement for a key | Compare the exact bone path with `BLENDER_LEG_TO_SERVO`. |
| Angle write fails | Check the converted angle plus offset, configured range, and hardware connection. |
| Queue full messages | Reduce the client's command rate; stale queued commands are not coalesced. |

There is no automated test suite or hardware-free execution mode in the current
repository. Dependency installation and source inspection alone do not verify
physical motion or Blender connectivity.
