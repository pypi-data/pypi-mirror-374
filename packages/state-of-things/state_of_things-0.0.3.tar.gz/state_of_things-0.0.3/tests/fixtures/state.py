# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
from src.state_of_things import State, Thing


class EnterExitTrackingState(State):
    """Records when a State is entered or exited."""

    def __init__(self) -> None:
        self.__entered_thing: Thing = None
        self.__exited_thing: Thing = None

    def enter(self, thing: Thing):
        self.__entered_thing = thing

    def exit(self, thing: Thing):
        self.__exited_thing = thing

    def assert_entered(self, thing: Thing):
        assert self.__entered_thing == thing

    def assert_not_entered(self):
        assert self.__entered_thing is None

    def assert_exited(self, thing: Thing):
        assert self.__exited_thing == thing

    def assert_not_exited(self):
        assert self.__exited_thing is None


class ImmediateChangeState(EnterExitTrackingState):
    """State that immediately changes to a next State."""

    def __init__(self, next_state: State) -> None:
        """State that changes into a next State on first update.

        Args:
            next_state (State): the State to change into.
        """
        super().__init__()
        self.__next_state = next_state

    def update(self, thing: Thing) -> State:
        return self.__next_state


class NeverChangeState(EnterExitTrackingState):
    """State that never changes to another State."""

    def update(self, thing: Thing) -> State:
        return self


class TimeTrackingState(State):
    """Record time elapsed and active each time the State is updated."""

    def __init__(self) -> None:
        self.__time_elapsed: float = None
        self.__time_active: float = None

    def update(self, thing: Thing) -> State:
        self.__time_elapsed = thing.time_elapsed
        self.__time_active = thing.time_active

        return self

    @property
    def time_elapsed(self) -> float:
        return self.__time_elapsed

    @property
    def time_active(self) -> float:
        return self.__time_active
