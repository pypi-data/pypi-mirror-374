# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
from src.state_of_things import State, Thing


class NoopState(State):
    pass


class NoopThing(Thing):
    def __init__(self):
        super().__init__(NoopState())


class TestState:
    def test_name_defaults_to_classname(self):
        assert NoopState().name == "NoopState"

    def test_update_does_not_change_state_by_default(self):
        state = NoopState()
        thing = NoopThing()

        assert state.update(thing) == state

    def test_enter_and_exit_pass_by_default(self):
        state = NoopState()
        thing = NoopThing()

        state.enter(thing)
        state.exit(thing)
