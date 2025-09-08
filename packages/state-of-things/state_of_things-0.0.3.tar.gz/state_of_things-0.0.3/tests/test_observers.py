# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
from src.state_of_things import Observers
from .fixtures.observer import CapturingObserver


class TestObservers:
    def test_attached_observer_is_notified(self):
        """
        When an observer is attached and has a function definition
        that matches the event name, it should be notified when an
        event occurs.
        """
        observers = Observers()

        test_observer = CapturingObserver()
        observers.attach(test_observer)

        observers.notify(CapturingObserver.test_event.__name__, 1234, "Hello!", 0.54321)

        test_observer.assert_notified(1234, "Hello!", 0.54321)

    def test_detached_observer_is_not_notified(self):
        """
        Observers that are detached should no longer receive event
        notifications.
        """
        observers = Observers()

        test_observer = CapturingObserver()
        observers.attach(test_observer)

        # detach the attached observer
        observers.detach(test_observer)

        observers.notify(CapturingObserver.test_event.__name__, 1234, "Hello!", 0.54321)

        test_observer.assert_not_notified()

    def test_notify_skips_observers_without_event_handler(self):
        """
        Observers that do not define a function to handle an event
        should be skipped (and no exception should occur).
        """
        observers = Observers()

        test_observer = CapturingObserver()
        observers.attach(test_observer)

        # this event is not handled by test_observer
        observers.notify("test_unhandled_event", 1234, "Hello!", 0.54321)

        test_observer.assert_not_notified()
