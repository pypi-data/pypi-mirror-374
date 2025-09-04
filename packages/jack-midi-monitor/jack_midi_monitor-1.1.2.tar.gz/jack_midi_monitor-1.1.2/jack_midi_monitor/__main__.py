#  jack_midi_monitor/jack_midi_monitor/__main__.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
import argparse, logging
from jack import JackError
from midi_notes import NOTE_NAMES
from jack_midi_monitor import JackMidiMonitor


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--auto-connect', '-a', action = 'store_true')
	parser.add_argument('--hex', '-x', action = 'store_true')
	parser.add_argument("--verbose", "-v", action = "store_true", help = "Show more detailed debug information")
	options = parser.parse_args()
	logging.basicConfig(
		level = logging.DEBUG if options.verbose else logging.ERROR,
		format = "[%(filename)24s:%(lineno)4d] %(levelname)-8s %(message)s"
	)

	def print_pretty(last_frame_time, offset, status, val_1, val_2):
		if val_2 is None:
			print(f'{status:02X} {val_1:02X}    : ', end = '')
		else:
			print(f'{status:02X} {val_1:02X} {val_2:02X} : ', end = '')
		opcode = status >> 4
		decoders[opcode](val_1, val_2)

	def print_hex(last_frame_time, offset, status, val_1, val_2):
		if val_2 is None:
			print(f'{status:02X} {val_1:02X}')
		else:
			print(f'{status:02X} {val_1:02X} {val_2:02X}')

	def note_on(val_1, val_2):
		print(f'ON      {NOTE_NAMES[val_1]:-3s} {val_1:-3d} {val_2:-3d}')

	def note_off(val_1, _):
		print(f'OFF     {NOTE_NAMES[val_1]:-3s} {val_1:-3d}')

	def poly_pressure(val_1, val_2):
		print(f'POLY    {NOTE_NAMES[val_1]:-3s} {val_1:d}  pres {val_2:d}')

	def control_change(val_1, val_2):
		print(f'CC_{val_1:-3d} {val_2:d}')

	def program_change(val_1, _):
		print(f'PROG    {val_1:d}')

	def channel_pressure(val_1, _):
		print(f'PRES    {val_1:d}')

	def pitch_bend(val_1, val_2):
		print(f'BEND    {val_1:d} {val_2:d}')

	decoders = {
		0x8: note_off,
		0x9: note_on,
		0xA: poly_pressure,
		0xB: control_change,
		0xC: program_change,
		0xD: channel_pressure,
		0xE: pitch_bend
	}

	try:
		with JackMidiMonitor(options.auto_connect) as mon:
			mon.on_midi_event(print_hex if options.hex else print_pretty)
			print('#' * 80)
			print('press Return to quit')
			print('#' * 80)
			input()
		return 0
	except JackError:
		print('Could not connect to JACK server. Is it running?')
		return 1


if __name__ == "__main__":
	import sys
	sys.exit(main())


#  end jack_midi_monitor/jack_midi_monitor/__main__.py
