# SPDX-FileCopyrightText: Copyright (c) 2024 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
"""Example using Observers as a stand-alone feature.

The example shows:
- How to direct events to a set of observers
"""

from state_of_things import Observers


class InputObserver:
    """Notified when input is received."""

    def input_received(self, input_string: str):
        pass


class LoggingObserver(InputObserver):
    """Logs the observed input."""

    def input_received(self, input_string: str):
        print(f"Observed: {input_string}")


class WordCountObserver(InputObserver):
    """Logs the number of words observed."""

    def input_received(self, input_string: str):
        print(f"Word Count: {len(input_string.split())}")


def main():
    # set up Observers for input
    observers = Observers()
    observers.attach(LoggingObserver())
    observers.attach(WordCountObserver())

    # display instructions. Type "exit" to terminate the program.
    print(
        'Input text and press enter to cause an event. Input "exit" to terminate this application.'
    )

    # will be set to True when "exit" is input
    exit_requested = False

    while not exit_requested:
        # display a prompt and wait until a line of input is received
        print("> ", end="")
        input_string = input()

        # notify observers of input
        observers.notify("input_received", input_string)

        # if "exit" is received, leave the loop
        exit_requested = input_string == "exit"


if __name__ == "__main__":
    main()
