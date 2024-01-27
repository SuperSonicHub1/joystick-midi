"""
Code heavily references example in https://www.pygame.org/docs/ref/joystick.html
See https://www.pygame.org/docs/ref/event.html for event members
"""

import atexit
from math import floor

import mido
from mido import Message
import pygame
from pygame import joystick

from . import util

def main():
	pygame.init()
	atexit.register(pygame.quit)

	joysticks = dict()
	joystick_to_channel = dict()

	output = util.open_midi_output()

	try:
		while True:
			for event in pygame.event.get():
				match event.type:
					# Hot plug devices
					case pygame.JOYDEVICEADDED:
						joy = joystick.Joystick(event.device_index)
						id = joy.get_instance_id()
						joysticks[id] = joy
						if id in joystick_to_channel:
							channel = joystick_to_channel[id]
						else:
							channel = max(joystick_to_channel.values(), default=-1) + 1
							joystick_to_channel[id] = channel
							print(f"Joystick {joy.get_name()} ({id}) connencted to channel #{channel}")
					case pygame.JOYDEVICEREMOVED:
						id = event.instance_id
						del joysticks[id]
						del joystick_to_channel[id]
						print(f"Joystick #{channel} ({id}) disconnected")
					
					# Map buttons to MIDI keys
					case pygame.JOYBUTTONDOWN:
						joy = joysticks[event.instance_id]
						channel = joystick_to_channel[event.instance_id]
						btn = event.button
						output.send(Message('note_on', channel=channel, note=btn))
					case pygame.JOYBUTTONUP:
						joy = joysticks[event.instance_id]
						channel = joystick_to_channel[event.instance_id]
						btn = event.button
						output.send(Message('note_off', channel=channel, note=btn))
	
					# Map axes to pitchwheel/CCs
					case pygame.JOYAXISMOTION:
						joy = joysticks[event.instance_id]
						channel = joystick_to_channel[event.instance_id]
						axis = event.axis
						if axis == 0:
							message = Message(
								'pitchwheel',
								channel=channel,
								pitch=floor(max(-8192, min(util.lerp(0, 8192, event.value), 8191)))
							)
						else:
							message = Message(
								'control_change',
								channel=channel,
								control=axis - 1,
								value=floor(util.lerp(0, 127, abs(event.value)))
							)
						output.send(message)

					# Map axes to CCs after axes
					case pygame.JOYHATMOTION:
						joy = joysticks[event.instance_id]
						channel = joystick_to_channel[event.instance_id]
						hat = event.hat
						control = (joy.get_numaxes() - 1) + hat * 2
						x, y = event.value
						output.send(
							Message(
								'control_change',
								channel=channel,
								control=control,
								value=127*abs(x)
							)
						)
						output.send(
							Message(
								'control_change',
								channel=channel,
								control=control + 1,
								value=127*abs(y)
							)
						)

	except KeyboardInterrupt:
		print()

if __name__ == "__main__":
	main()
