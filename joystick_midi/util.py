import mido
from mido.ports import BaseInput, BaseOutput

def open_midi_output() -> BaseOutput:
    """
    Interactively pick output from terminal.
    """
    names = mido.get_output_names()
    print("-1: Virtual Port")
    for i, name in enumerate(names):
        print(f"{i}: {name}")
    idx = int(input("> "))
    if idx == -1:
        return mido.open_output("Joystick MIDI", virtual=True)
    return mido.open_output(names[idx])

def lerp(left, right, amount):
    return amount * (right - left) + left
