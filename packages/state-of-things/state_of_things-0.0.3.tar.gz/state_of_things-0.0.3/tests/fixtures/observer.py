# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
from state_of_things import State, Thing, ThingObserver


class CapturingObserver:
    """Records when a test event is observed."""

    def __init__(self) -> None:
        self.__captured_params = None

    def test_event(self, *params):
        self.__captured_params = params

    def assert_notified(self, *params):
        assert self.__captured_params == params

    def assert_not_notified(self):
        assert self.__captured_params is None


class StateChangeObserver(ThingObserver):
    """Records when a state change is observed."""

    def __init__(self) -> None:
        self.__thing: Thing = None
        self.__old_state: State = None
        self.__new_state: State = None

    def state_changed(self, thing: Thing, old_state: State, new_state: State):
        self.__thing = thing
        self.__old_state = old_state
        self.__new_state = new_state

    def assert_notified(self, thing: Thing, old_state: State, new_state: State):
        assert self.__thing == thing
        assert self.__old_state == old_state
        assert self.__new_state == new_state

    def assert_not_notified(self):
        assert self.__thing is None
        assert self.__old_state is None
        assert self.__new_state is None


class CustomThingObserver(ThingObserver):
    """Records when a custom event is observed."""

    def __init__(self) -> None:
        self.__notified_v1: str = None
        self.__notified_v2: int = None

    def custom_event(self, v1: str, v2: int):
        self.__notified_v1 = v1
        self.__notified_v2 = v2

    def assert_notified(self, expected_v1: str, expected_v2: int):
        assert self.__notified_v1 == expected_v1
        assert self.__notified_v2 == expected_v2


class CustomNotifierState(State):
    """Notifies a custom event when entered."""

    EVENT_NAME = CustomThingObserver.custom_event.__name__

    def __init__(self, *params) -> None:
        self.params = params

    def enter(self, thing: Thing):
        thing.observers.notify(self.EVENT_NAME, *self.params)
