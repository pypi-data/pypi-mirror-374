# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
import time
import pytest
from src.state_of_things import Thing, State
from .fixtures.state import (
    EnterExitTrackingState,
    ImmediateChangeState,
    NeverChangeState,
    TimeTrackingState,
)


class TestThing:
    def test_initial_state_is_entered_on_first_update(self):
        """Things must always enter an initial State on first update."""
        initial_state = EnterExitTrackingState()
        thing = Thing(initial_state)

        assert thing.current_state is None
        assert thing.previous_state is None

        thing.update()

        assert thing.current_state is initial_state
        assert thing.previous_state is None

        initial_state.assert_entered(thing)
        initial_state.assert_not_exited()

    def test_initial_state_is_required(self):
        with pytest.raises(AssertionError) as expected_error:
            Thing(initial_state=None)

        assert str(expected_error.value) == "initial_state is required"

    def test_state_change_exits_and_enters_states(self):
        """
        When changing States, the current State should exit before
        the new State is entered.
        """

        new_state = EnterExitTrackingState()
        initial_state = ImmediateChangeState(next_state=new_state)

        thing = Thing(initial_state)
        # go to initial state, which then changes to the new state
        thing.update()

        assert thing.current_state == new_state
        assert thing.previous_state == initial_state

        initial_state.assert_exited(thing)
        new_state.assert_entered(thing)
        new_state.assert_not_exited()

    def test_going_to_current_state_does_not_change_state(self):
        """
        When changing States, if the new State is the same as the
        current State then do not enter or exit States.
        """
        initial_state = NeverChangeState()

        thing = Thing(initial_state)

        # go to the initial State (should not trigger a change)
        thing.update()

        assert thing.current_state == initial_state
        assert thing.previous_state is None

        initial_state.assert_entered(thing)
        initial_state.assert_not_exited()

    def test_time_elapsed_between_updates(self):
        """
        The time elapsed between updates to a Thing can be accessed
        by a State.
        """

        time_tracking_state = TimeTrackingState()

        thing = Thing(time_tracking_state)
        # go to initial State
        thing.update()

        sleep_time = 0.75
        time.sleep(sleep_time)

        thing.update()

        # assert that time elapsed is within margin of error from the
        # expected time
        assert time_tracking_state.time_elapsed - sleep_time < 0.05

    def test_time_active_after_multiple_updates(self):
        """
        The total time active in a State can be accessed by the
        State.
        """
        time_tracking_state = TimeTrackingState()

        thing = Thing(time_tracking_state)
        # go to initial State
        thing.update()

        sleep_time = 0.25
        sleep_count = 4
        for _ in range(sleep_count):
            time.sleep(sleep_time)
            thing.update()

        # assert that time active is within margin of error from the
        # expected time
        expected_active_time = sleep_time * sleep_count
        assert time_tracking_state.time_active - expected_active_time < 0.05

    def test_thing_name_defaults_to_class_name(self):
        class ExpectedNameThing(Thing):
            pass

        thing = ExpectedNameThing(State())

        assert thing.name == ExpectedNameThing.__name__

    def test_thing_name_can_be_overridden(self):
        expected_thing_name = "OverriddenThingName"

        thing = Thing(State(), name=expected_thing_name)

        assert thing.name == expected_thing_name
