import OSC
import time

sending_port = 3339
out_c = OSC.OSCClient()
out_c.connect(('127.0.0.1', sending_port))

def send_notes(notes, duration):
	global out_c
	msg = OSC.OSCMessage()
	msg.setAddress("/notes")
	for note in notes:
		msg.append(note[0])
		msg.append(note[1])
	out_c.send(msg)
	time.sleep(duration)
	msg = OSC.OSCMessage()
	msg.setAddress("/notes")
	for note in notes:
		msg.append(note[0])
		msg.append(0)
	out_c.send(msg)