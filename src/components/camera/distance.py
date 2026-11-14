
#TODO: Change code to the camera related things



from statemanagement.device import (
    create_context,
    device_action,
    device_parser,
)

from distance_sensor import DistanceSensor

distance_ctx = create_context("DistanceSensor", DistanceSensor)

@device_parser(distance_ctx)
def parse_distance_sensor(config: dict):
    mode = config.get("mode", 1)
    timing_budget = config.get("timing_budget")
    if mode is None or timing_budget is None:
        raise ValueError('"mode" and "timing_budget" are required for a distance sensor')
    return DistanceSensor(mode, timing_budget)

@device_action(distance_ctx)
def read_distance(device: DistanceSensor):
    return device.read_dist()


