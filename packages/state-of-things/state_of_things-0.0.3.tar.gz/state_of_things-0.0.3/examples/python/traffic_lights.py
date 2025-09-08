# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
"""Traffic light example that supports caution mode and external
control.

This example shows:
- How to externally control a Thing, but still allow the Thing to
    manage its State and transitions (see TrafficLightThing.should_go
    and TrafficLightThing.caution_mode).
- How to provide custom strongly typed observers (see
    TrafficLightObserver).
"""

import time
from state_of_things import State, Thing, ThingObserver


class TrafficLightStates:
    stop: State
    go: State
    slow: State
    caution: State


class TrafficLightThing(Thing):
    """Externally controlled traffic light with a caution mode that
    overrides other states.
    """

    def __init__(self, slow_seconds: float):
        """Construct a new traffic light.

        Args:
            slow_seconds (float): number of seconds to remain in slow
            State before changing to stop.
        """
        super().__init__(TrafficLightStates.stop)
        self.__slow_seconds = slow_seconds
        self.__should_go = False
        self.__caution_mode = False

    def stop(self):
        """Request change to stop"""
        self.__should_go = False
        print("Stop requested.")

    def go(self):
        """Request change to go"""
        self.__should_go = True
        print(f"Go requested (caution mode={self.caution_mode}).")

    @property
    def slow_seconds(self) -> float:
        """Number of seconds to remain in slow before stop"""
        return self.__slow_seconds

    @property
    def should_go(self) -> bool:
        """True if the traffic light should change to go (unless in
        caution mode)"""
        return self.__should_go

    @property
    def caution_mode(self) -> bool:
        """True if the traffic light is in caution mode."""
        return self.__caution_mode

    @caution_mode.setter
    def caution_mode(self, enabled: bool):
        """Enable or disable caution mode."""
        self.__caution_mode = enabled
        print(f"Caution mode set to {enabled}")


class StopState(State):
    """This State will transition to go if requested, or to caution if
    caution mode is enabled."""

    def enter(self, thing: TrafficLightThing):
        # notify observers of stop event
        thing.observers.notify("changed_to_stop", self)

    def update(self, thing: TrafficLightThing) -> State:
        if thing.caution_mode:
            # caution mode is enabled, change to caution State
            return TrafficLightStates.caution

        if thing.should_go:
            # go State requested
            return TrafficLightStates.go

        return self


TrafficLightStates.stop = StopState()


class GoState(State):
    """This State will transition to slow when stop is requested, or to
    caution if caution mode is enabled."""

    def enter(self, thing: TrafficLightThing):
        # notify observers of go event
        thing.observers.notify("changed_to_go", self)

    def update(self, thing: TrafficLightThing) -> State:
        if thing.caution_mode:
            # caution mode is enabled, change to caution State
            return TrafficLightStates.caution

        if not thing.should_go:
            # stop State requested, but need to slow first
            return TrafficLightStates.slow

        return self


TrafficLightStates.go = GoState()


class SlowState(State):
    """After a number of seconds, this State will transition to go or
    stop based on the last traffic light request. If caution mode is
    enabled, it will immediately switch to caution State."""

    def enter(self, thing: TrafficLightThing):
        # notify observers of slow event
        thing.observers.notify("changed_to_slow", self)

    def update(self, thing: TrafficLightThing) -> State:
        if thing.caution_mode:
            # caution mode is enabled, immediately change to caution
            # State
            return TrafficLightStates.caution

        if thing.time_active < thing.slow_seconds:
            # always wait in this State before proceeding to go or stop
            return self

        if thing.should_go:
            # go requested, change to it
            return TrafficLightStates.go

        # default to stop State after slow
        return TrafficLightStates.stop


TrafficLightStates.slow = SlowState()


class CautionState(State):
    """Stays in this State as long as caution mode is enabled, sending a
    blink notification every second. If caution mode is disabled, it
    always changes to stop State even if go was requested."""

    def enter(self, thing: TrafficLightThing):
        # notify observers of caution event
        thing.observers.notify("changed_to_caution", self)

        # local attributes only used within this State
        thing.caution_next_blink = 0
        thing.caution_blink_count = 0

    def update(self, thing: TrafficLightThing) -> State:
        if not thing.caution_mode:
            # caution mode is disabled, go to stop State
            thing.stop()
            return TrafficLightStates.stop

        if time.monotonic() > thing.caution_next_blink:
            # it is time to blink again, and set next blink to 1 second
            # in the future.
            thing.caution_next_blink = time.monotonic() + 1
            thing.caution_blink_count = thing.caution_blink_count + 1

            # notify observers of blink event
            thing.observers.notify("caution_blink", self, thing.caution_blink_count)

        return self


TrafficLightStates.caution = CautionState()


class TrafficLightObserver(ThingObserver):
    """Custom Thing observer that receives events specific to the
    Traffic Light Thing."""

    def changed_to_go(self, thing: TrafficLightThing):
        """Traffic light changed to go."""
        pass

    def changed_to_stop(self, thing: TrafficLightThing):
        """Traffic light changed to stop."""
        pass

    def changed_to_slow(self, thing: TrafficLightThing):
        """Traffic light changed to slow."""
        pass

    def changed_to_caution(self, thing: TrafficLightThing):
        """Traffic light changed to caution mode."""
        pass

    def caution_blink(self, thing: TrafficLightThing, blink_count: int):
        """Traffic light blinked while in caution mode."""
        pass


class TrafficLoggingObserver(TrafficLightObserver):
    """Prints messages when traffic light events are observed."""

    def changed_to_go(self, thing: TrafficLightThing):
        print("-> Green Light")

    def changed_to_stop(self, thing: TrafficLightThing):
        print("-> Red Light")

    def changed_to_slow(self, thing: TrafficLightThing):
        print("-> Yellow Light")

    def changed_to_caution(self, thing: TrafficLightThing):
        print("-> Caution!")

    def caution_blink(self, thing: TrafficLightThing, blink_count: int):
        print(f"-> Blink Yellow (count {blink_count})")


def update_thing(thing: Thing, seconds_to_update: float):
    """Block while updating a Thing for a number of seconds.

    Args:
        thing (Thing): the Thing to update.
        seconds_to_update (float): number of seconds to update.
    """
    time_until_done = time.monotonic() + seconds_to_update
    while time.monotonic() < time_until_done:
        thing.update()


def main():
    # create a new traffic light.
    traffic_light = TrafficLightThing(slow_seconds=3)
    traffic_light.observers.attach(TrafficLoggingObserver())
    # update to change to initial State of stop
    traffic_light.update()

    # request change to go State
    traffic_light.go()
    update_thing(traffic_light, seconds_to_update=2)

    # request change to stop State
    traffic_light.stop()
    update_thing(traffic_light, seconds_to_update=5)

    # enable caution mode
    traffic_light.caution_mode = True
    update_thing(traffic_light, seconds_to_update=2)

    # does not do anything, light is in caution mode!
    traffic_light.go()
    update_thing(traffic_light, seconds_to_update=2)

    # disable caution mode, which sets light back to stop State (not
    # go State as set above)
    traffic_light.caution_mode = False
    update_thing(traffic_light, seconds_to_update=2)

    # request change to go State
    traffic_light.go()
    update_thing(traffic_light, seconds_to_update=2)

    # caution mode also breaks out of go State
    traffic_light.caution_mode = True
    update_thing(traffic_light, seconds_to_update=3)

    print("Done.")


if __name__ == "__main__":
    main()
