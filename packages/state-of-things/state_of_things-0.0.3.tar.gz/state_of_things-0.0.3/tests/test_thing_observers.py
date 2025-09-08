# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
from src.state_of_things import State, Thing, ThingObserver
from .fixtures.observer import (
    StateChangeObserver,
    CustomNotifierState,
    CustomThingObserver,
)
from .fixtures.state import ImmediateChangeState, NeverChangeState


class TestThingObservers:
    def test_state_change_notifies_attached_observers(self):
        """
        Observers that inherit from ThingObserver should receive
        notification of state changes with old and new States.
        """
        observers = [StateChangeObserver(), StateChangeObserver()]

        new_state = State()
        initial_state = ImmediateChangeState(next_state=new_state)

        thing = Thing(initial_state)
        for observer in observers:
            thing.observers.attach(observer)

        # go to initial state, which will change to new_state
        thing.update()

        for observer in observers:
            observer.assert_notified(thing, initial_state, new_state)

    def test_custom_events_can_be_observed(self):
        """
        Observers may define custom events that Things and States can
        notify.
        """
        expected_v1 = "Hello custom event"
        expected_v2 = 12345

        # State will notify a custom event when entered
        custom_state = CustomNotifierState(expected_v1, expected_v2)

        thing = Thing(custom_state)
        observer = CustomThingObserver()
        thing.observers.attach(observer)

        # trigger the custom event by going to the initial state
        thing.update()

        observer.assert_notified(expected_v1, expected_v2)

    def test_going_to_current_state_does_not_notify_change_state(self):
        """
        When changing States, if the new State is the same as the
        current State then do not notify a state change.
        """
        initial_state = NeverChangeState()

        thing = Thing(initial_state)
        # go to the initial state
        thing.update()

        observer = StateChangeObserver()
        thing.observers.attach(observer)

        # stay in the current State (should not trigger a change)
        thing.update()

        observer.assert_not_notified()

    def test_thing_observer_does_nothing_by_default(self):
        """
        By default, ThingObserver will do nothing when state changes
        are received (as opposed to throwing an exception).
        """
        observer = ThingObserver()

        observer.state_changed(Thing(State()), State(), State())
