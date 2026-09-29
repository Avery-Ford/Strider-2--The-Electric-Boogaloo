# Packages

`pyproject.toml` declares Python `>=3.11` and four direct dependencies.
`uv.lock` records the resolved versions listed here; these are repository pins,
not claims about the latest releases. Use `uv sync --locked` to reproduce them.

## Direct dependencies

| Package | Declared minimum | Locked version | Use in this repository |
| --- | --- | --- | --- |
| `adafruit-circuitpython-servokit` | 1.3.19 | 1.3.19 | `ServoKit` configures the two servo boards and exposes channel servos; used by the servo component and experimental scripts |
| `adafruit-circuitpython-lis3dh` | 5.2.4 | 5.2.4 | Declared accelerometer driver; no current source file imports or uses it |
| `python-dotenv` | 1.1.0 | 1.1.0 | `load_dotenv()` loads `.env` for the WebSocket entry point |
| `websockets` | 15.0.1 | 15.0.1 | Provides the asyncio WebSocket server and connection types in `main.py` |

## Transitive dependencies

These are installed through the direct dependencies and recorded in `uv.lock`.
Most support the Adafruit hardware stack rather than being called directly by
application code. `adafruit_motor.servo.Servo` is imported directly by the servo
component, though its package is currently supplied transitively by ServoKit.

| Package | Locked version | Role in the dependency stack |
| --- | --- | --- |
| `adafruit-blinka` | 8.56.0 | CircuitPython hardware compatibility layer for host Python |
| `adafruit-circuitpython-busdevice` | 5.2.11 | Bus device helpers |
| `adafruit-circuitpython-connectionmanager` | 3.1.3 | Connection helpers used by the requests dependency |
| `adafruit-circuitpython-motor` | 3.4.15 | Servo objects and motor control primitives |
| `adafruit-circuitpython-pca9685` | 3.4.17 | PWM controller driver used by ServoKit |
| `adafruit-circuitpython-register` | 1.10.2 | Hardware register helpers |
| `adafruit-circuitpython-requests` | 4.1.10 | Requests support pulled in through CircuitPython typing dependencies |
| `adafruit-circuitpython-typing` | 1.11.2 | Shared CircuitPython types and protocols |
| `adafruit-platformdetect` | 3.77.0 | Platform detection for Blinka |
| `adafruit-pureio` | 1.1.11 | Low-level I/O support |
| `binho-host-adapter` | 0.1.6 | Adapter support pulled in by Blinka |
| `pyftdi` | 0.56.0 | FTDI interface support pulled in by Blinka |
| `pyserial` | 3.5 | Serial transport support |
| `pyusb` | 1.3.1 | USB transport support |
| `sysv-ipc` | 1.1.0 | IPC support; selected on Linux when `platform_machine != 'mips'` |
| `typing-extensions` | 4.13.2 | Typing compatibility helpers |

The lockfile includes support for multiple hardware transports; their presence
does not mean the application uses every transport. Actual host compatibility
and I²C availability still depend on the connected system.

## Standard library and development tooling

No additional packages are needed for `asyncio`, `threading`, `queue`,
`concurrent.futures`, `json`, `os`, `argparse`, `logging`, `datetime`, `inspect`,
`collections`, `contextlib`, `dataclasses`, `functools`, or `typing`; they are
Python standard-library modules used by the source.

`uv` is the environment/dependency tool used by the documented workflow, not
an application runtime dependency. The project currently declares no optional
dependency groups, test framework, linter, or packaged CLI entry points. Run
the scripts by path from the repository root as described in the
[setup guide](setup.md).
