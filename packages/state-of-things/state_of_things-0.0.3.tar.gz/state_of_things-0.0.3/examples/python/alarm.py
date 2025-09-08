# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
"""Example of an Alarm that will wait for a while, loop between the
alarm going off and snoozing a number of times, and then exiting
the application.

The example shows:
- How to pass configuration into a Thing (see AlarmThing.__init__).
- How to pass data between States (see AlarmThing.snooze_count).
- How to branch into multiple States (see SnoozeState).
- How to terminate an application with States (see AlarmThing.finished).
"""

from state_of_things import State, Thing


class AlarmStates:
    """The states that the Alarm can have."""

    waiting: State
    triggered: State
    snooze: State
    finished: State


class AlarmThing(Thing):
    """Waits a number of seconds and then triggers the alarm."""

    def __init__(
        self,
        seconds_until_alarm: float,
        alarm_seconds: float,
        snooze_seconds: float,
        snoozes: int,
    ):
        """Constructor that configures a new Alarm.

        Args:
            seconds_until_alarm (float): number of seconds to wait before
            triggering the alarm
            alarm_seconds (float): number of seconds to sound the alarm
            snooze_seconds (float): number of seconds to snooze before
            triggering the alarm again
            snoozes (int): number of times the alarm was snoozed
        """
        super().__init__(AlarmStates.waiting)

        self.__seconds_until_alarm = seconds_until_alarm
        self.__alarm_seconds = alarm_seconds
        self.__snooze_seconds = snooze_seconds
        self.__snoozes = snoozes
        self.__snooze_count = 0

    @property
    def seconds_until_alarm(self) -> float:
        """Seconds until the alarm should trigger"""
        return self.__seconds_until_alarm

    @property
    def alarm_seconds(self) -> float:
        """Seconds the alarm should sound"""
        return self.__alarm_seconds

    @property
    def snooze_seconds(self) -> float:
        """Seconds to stay in snooze state"""
        return self.__snooze_seconds

    @property
    def snoozes(self) -> int:
        """The number of times the alarm should snooze"""
        return self.__snoozes

    @property
    def snooze_count(self) -> int:
        """The number of times the alarm was in snooze state"""
        return self.__snooze_count

    @snooze_count.setter
    def snooze_count(self, count: int):
        self.__snooze_count = count

    @property
    def finished(self) -> bool:
        """True if this alarm has triggered"""
        return self.current_state == AlarmStates.finished


class WaitingState(State):
    """
    Remains in the current state until it has been active long enough
    for the alarm to trigger.
    """

    def enter(self, thing: AlarmThing):
        print(f"Waiting for {thing.seconds_until_alarm} seconds")
        # reset the snooze count when starting to wait for an alarm
        thing.snooze_count = 0

    def update(self, thing: AlarmThing) -> State:
        if thing.time_active >= thing.seconds_until_alarm:
            # waited long enough, time to trigger the alarm
            return AlarmStates.triggered

        return self


AlarmStates.waiting = WaitingState()


class TriggeredState(State):
    """Whoops every second and then snoozes."""

    def enter(self, thing: AlarmThing):
        print("Alarm has triggered!")

        # triggered_last_whoop was not formally declared on AlarmThing.
        # Be very careful when using this pattern, and only when the
        # attribute is used within a single State.
        thing.triggered_last_whoop = 0

    def update(self, thing: AlarmThing) -> State:
        if thing.time_active > thing.alarm_seconds:
            # time to snooze the alarm
            return AlarmStates.snooze

        # use int to round time down to the nearest second
        if int(thing.time_active) > thing.triggered_last_whoop:
            # time for another whoop!
            print("Whoop!")

            # wait a second for the next whoop
            thing.triggered_last_whoop = thing.triggered_last_whoop + 1

        return self


AlarmStates.triggered = TriggeredState()


class SnoozeState(State):
    """Wait for a while and then transition back to triggered."""

    def enter(self, thing: AlarmThing):
        print(f"Alarm snoozing for {thing.snooze_seconds}")

        # keep track of number of snoozes
        thing.snooze_count = thing.snooze_count + 1

    def update(self, thing: AlarmThing) -> State:
        # if snoozed enough times, the alarm is finished
        if thing.snooze_count > thing.snoozes:
            return AlarmStates.finished

        # if snoozed long enough, trigger the alarm again
        if thing.time_active > thing.snooze_seconds:
            return AlarmStates.triggered

        # otherwise, keep waiting
        return self


AlarmStates.snooze = SnoozeState()


class FinishedState(State):
    """Do nothing and stay in this state when the alarm is finished."""

    def enter(self, thing: Thing):
        print("Finished!")


AlarmStates.finished = FinishedState()


def main():
    # configure a new Alarm
    thing = AlarmThing(
        seconds_until_alarm=5, alarm_seconds=4, snooze_seconds=3, snoozes=2
    )

    # keep updating the alarm until it is finished
    while not thing.finished:
        thing.update()


if __name__ == "__main__":
    main()
