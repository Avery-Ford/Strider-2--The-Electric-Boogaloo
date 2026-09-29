# Code architecture

## Module layout

| Path | Responsibility |
| --- | --- |
| `src/main.py` | Loads environment/configuration, hosts WebSocket connections, maps bone paths, and queues servo commands |
| `src/arm.py` | Parses CLI arguments and sets absolute servo angles |
| `src/components/servo/__init__.py` | Re-exports the servo component API |
| `src/components/servo/servo.py` | Registers hat/servo parsers and implements `set_angle` |
| `src/components/utils.py` | Empty placeholder |
| `src/statemanagement/device.py` | Device contexts, registration, configuration loading, and action decorators |
| `src/statemanagement/logger.py` | File logging and optional log filters |
| `src/testScript/` | Direct ServoKit hardware experiments |
| `config.json` | Named boards and servo-to-channel wiring |

## Startup and device registry

Both entry points import the servo component before calling
`configure_device("config.json")`. Importing that component creates two global
contexts in `DEVICE_CONTEXT_COLLECTION`: `ServoHat` for `ServoKit` instances
and `Servo` for `adafruit_motor.servo.Servo` instances.

The `@device_parser(ctx)` decorator installs a parser for each context.
`configure_device` initializes logging and reads JSON sections in insertion
order. Each section name selects a context; each entry is parsed and registered
under its identifier. Unknown sections are logged and skipped. Duplicate
identifiers and objects of the wrong type are rejected.

`parse_hat` creates a 16-channel ServoKit at the specified address.
`parse_servo` resolves a hat identifier, selects its channel, and configures
270-degree travel and pulse widths. This is why hats must precede servos in
the configuration.

`@device_action(ctx)` allows `set_angle` to receive either a device identifier
or a Servo instance. For example, `set_angle("servo1", 90)` resolves the stored
object and assigns its `angle` property. Hardware access is delegated to the
Adafruit libraries.

## WebSocket command flow

```text
Blender / WebSocket client
  -> JSON object received by handle_connection
  -> exact bone-path lookup in BLENDER_LEG_TO_SERVO
  -> int(value) + 90
  -> Queue(maxsize=1000)
  -> one daemon servo_worker thread
  -> set_angle(identifier, angle)
  -> device registry -> Servo -> ServoKit / I²C hardware
```

The asyncio event loop handles connections. A single shared queue carries
individual servo updates from all clients to one worker thread, which performs
blocking hardware writes sequentially. A message containing several bones is
not an atomic synchronized pose update. The worker catches write errors and
continues; the producer drops commands when the queue is full.

`main.py` also creates a `ThreadPoolExecutor(max_workers=6)`, but never submits
work to it. Actual servo writes use the one daemon thread, not six parallel
workers. The queue preserves enqueued command order and does not replace old
angles with newer values for the same servo.

Configuration and worker-thread startup occur at module scope, so importing
`main.py` initializes hardware and starts the worker. The CLI also parses
arguments and configures devices at module scope. Neither is a side-effect-free
library entry point.

On Ctrl+C, the shutdown paths set `running` to false, enqueue a sentinel, and
shut down the unused executor. They do not explicitly join the servo thread,
drain the queue, or deinitialize the boards. Pending commands are not guaranteed
to finish, and outputs are not explicitly disabled.

## Additional registry facilities

`device.py` includes helpers beyond those used by the current servo controller:

- Masked contexts share another context's store while tracking their own names.
  Configuration can register aliases through `__cast`.
- `@device` and `identifier(ctx)` resolve declared device references or parse
  inline device definitions for a decorated class.
- `@device_exit(ctx)` registers an exit callback. The
  `configure_device_w_context` context manager calls registered callbacks after
  a normal exit from its body; it does not wrap the yield in `try/finally`.

The current entry points use `configure_device` directly and do not register
servo exit callbacks.

## Extending the controller

To add a component, create its context and parser, import the component before
configuration, and add a matching JSON section. Place dependent devices after
the devices they reference. Wrap operations with `device_action` to support
named lookup consistently.

To change wiring, edit `config.json`. To change Blender names or the angle
offset, edit `BLENDER_LEG_TO_SERVO` or `ANGLE_OFFSET` in `main.py`. Servo travel
is currently set in `parse_servo`. The repository contains no gait planner,
inverse-kinematics solver, accelerometer feedback loop, or Blender-side code.
