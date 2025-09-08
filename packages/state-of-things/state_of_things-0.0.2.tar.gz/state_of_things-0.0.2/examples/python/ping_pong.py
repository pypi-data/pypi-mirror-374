# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
"""Simple example that ping-pongs between two States every 2 seconds.

The example shows:
- How to use the States class pattern to keep track of valid States
    (see PingPongStates)
- How to change between States (see PingState.update and
    PongState.update)
- How to track elapsed time within a State (see thing.time_active usage)
- How to observer State changes (see LoggingObserver). State change
    observers are typically only used for logging purposes. Code external
    to the Thing should not have logic that references the internal
    States of a Thing.
"""

import time
from state_of_things import State, Thing, ThingObserver


class PingPongStates:
    """The States that a Ping Pong Thing can have. The intention of this
    pattern is to help with type hinting and auto-completion, BUT the
    down side is that each State must be instantiated and set into this
    object after it is defined. See the comments below with 'NOTE:'"""

    ping: State
    pong: State


class PingPongThing(Thing):
    """Alternates between Ping and Pong States, starting with Ping."""

    def __init__(self):
        """Construct a new Ping Pong that starts on Ping."""
        super().__init__(PingPongStates.ping)


class PingState(State):
    def enter(self, thing: PingPongThing):
        # log when the Ping State is entered.
        print("Ping!")

    def update(self, thing: PingPongThing) -> State:
        if thing.time_active > 2:
            # thing has been in Ping State for 2 seconds, time for pong
            return PingPongStates.pong

        # not yet time for pong, stay in this State
        return self


# NOTE: Be sure to create an instance of each State and store it in the
# States class!
PingPongStates.ping = PingState()


class PongState(State):
    def enter(self, thing: PingPongThing):
        # log when the Pong State is entered.
        print("Pong!")

    def update(self, thing: PingPongThing) -> State:
        if thing.time_active > 2:
            # thing has been in Pong State for 2 seconds, time for ping
            return PingPongStates.ping

        # not yet time for ping, stay in this State
        return self


# NOTE: Be sure to create an instance of each State and store it in the
# States class!
PingPongStates.pong = PongState()


class LoggingObserver(ThingObserver):
    """Prints a message when State changes occur."""

    def state_changed(self, thing: Thing, old_state: State, new_state: State):
        print(
            f"State of {thing.name} changed from {old_state.name} to {new_state.name}"
        )


def main():
    # create a new Ping Pong Thing.
    ping_pong = PingPongThing()

    # attach the logging observer so it receives notifications
    ping_pong.observers.attach(LoggingObserver())

    # keep pinging and ponging for 10.5 seconds (extra half a second
    # to end on a Pong)
    time_to_stop = time.monotonic() + 10.5
    while time.monotonic() < time_to_stop:
        ping_pong.update()


if __name__ == "__main__":
    main()
