#!/usr/bin/env python
# genome_server.py

"""
Main entry point for the Python portion of the project. Loads a chromosome file in the .fa format,
and offers an OSC endpoint that can be used to read through the chromosome.

Calling nextAmino on the ChromosomeReader returns a character representing an amino acid, "Stop" if
the next three base pairs are a stop codon, or None if the end of the chromosome file has been reached.
Passing that amino acid to Conductor, with the addAmino function, causes the Conductor to incorporate
that amino acid into an evolving musical structure. More details on how that interpretation takes place
can be found in conductor.py

By default, the server listens for OSC messages from Max on port 3337, and sends messages back to Max
on port 3338. The server can also be controlled remotely via OSC messages that it listens for on port
3339.
"""

import sys
import time, threading
import OSC
from chromosome_reader import *
from conductor import *

if len(sys.argv) < 2:
	print "Usage: python genome_server.py <filename>\n<filename> must be the path to a .fa genome file"
	return

listening_port = 3337
max_sending_port = 3338
remote_sending_port = 3339
filename = sys.argv[1]

## State setup
cr = ChromosomeReader(filename)
cn = Conductor()

"""
OSC Handlers --- Max
These are the messages that Max sends to the genome server to control genome file reading and MIDI
event generation
"""
def get_amino_acid_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /getAminoAcidCounts address. Simply returns the current count of each
	of the amino acids as a 20 element array

	(from Max)
	/getAminoAcidCounts

	(to Max)
	/aminoAcidCounts 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
	"""
	global out_c_max
	global cn
	msg = OSC.OSCMessage()
	msg.setAddress("/aminoAcidCounts")
	for cnt in cn.getAminoAcidCounts():
		msg.append(cnt)
	out_c_max.send(msg)

def ping_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /ping address. Returns an /echo message with the current time

	(from Max)
	/ping

	(to Max)
	/echo 12934829364
	"""
	print addr
	print tags
	print stuff
	print source
	send_echo_event()

def reset_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /reset address. Moves the curson back to the beginning of the current
	chromosome file, clears all of the current sequencers, and returns the counts for each amino
	acid to zero
	"""
	global filename
	global cr
	global cn
	print "Resetting"
	print source
	cr.loadChromosomeFile(filename)
	cn.reset()

def read_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /read address. Reads a number of amino acids, then sends the /ready
	message when reading is complete. An empty /read message will read a single amino acid. If an integer
	argument is given, that many amino acids will be read instead.

	In typical use, Max sends a /read message to the genome server, then sends another /read message as
	soon as it receives a /ready message in response. These messages may be sent through a speedlim
	object in Max, so that they do not overwhelm the system.

	(from Max)
	/read 5

	(to Max)
	/ready
	"""
	global cr
	global cn

	toRead = 1
	if len(stuff) > 0:
		toRead = int(stuff[0])

	for _ in range(toRead):
		if cr.hasNext():
			cn.addAmino(cr.nextAmino())
		else:
			break
	send_read_complete_event()

def step_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /step address. The message should have a single argument, an integer
	that is the current beat. This beat represents the tatum, or the smallest subdivision of a measure
	that will be used in composition. If sixteenth notes are desired, then there should be 16 steps per
	measure. Steps index from zero, so the 7th 16th note of the 4th measure would be /step 70

	In typical use, this is bound to Live's transport. As the transport advances, it generates a /step message
	once per sixteenth note. The response to that message contains the MIDI events that should occur on that beat.

	These events follow the /midi address, with three integers per midi event defining the pitch, velocity and 
	midi channel of that event. For example, if there were two midi events at a particular step, then the
	/midi message from genome server might look like:
	/midi <event-1-pitch> <event-1-velocity> <event-1-channel> <event-2-pitch> <event-2-velocity> <event-2-channel>

	(from Max)
	/step 70

	(to Max)
	/midi 48 100 1 64 10 1
	"""
	midiEvents = cn.processStep(stuff[0])
	send_midi_events(midiEvents)

def transport_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /transport address. Max sends this messages whenever the state of Live's transport
	changes. Typically, this will happen when the remote controller sends the genome server an /rtransport message,
	which can cause the transport to start, stop or continue. Since Max must communicate with Live to effect
	this change, it sends a /transport message when the change takes effect, so that the remote controller can
	confirm that the change took place

	(from Max)
	/transport <int:bars> <int:beats> <float:ticks> <int:on-off-status>

	(to Remote Controller)
	/rprint <int:bars> <int:beats> <float:ticks> <int:on-off-status>
	"""
	send_transport_status(stuff)

## OSC Senders --- Max
def send_midi_events(events):
	global out_c_max
	msg = OSC.OSCMessage()
	msg.setAddress("/midi")
	for event in events:
		for i in event:
			msg.append(i)
	out_c_max.send(msg)

def send_echo_event():
	global out_c_max
	msg = OSC.OSCMessage()
	msg.setAddress("/echo")
	msg.append(time.time())
	out_c_max.send(msg)

def send_read_complete_event():
	global out_c_max
	global cr
	msg = OSC.OSCMessage()
	msg.setAddress("/ready")
	msg.append(cr.getBasePairsRead())
	msg.append(cr.getAminoAcidsRead())
	out_c_max.send(msg)

def send_transport_event(typp):
	global out_c_max
	msg = OSC.OSCMessage()
	msg.setAddress("/transport")
	msg.append(typp)
	out_c_max.send(msg)

def send_transport_status(stuff):
	global out_c_remote
	msg = OSC.OSCMessage()
	msg.setAddress("/rprint")
	msg.append("transport: ")
	for s in stuff:
		msg.append(s)
	out_c_remote.send(msg)

"""
OSC Handlers --- Remote
The genome server listens on port 3339 for messages that can be used to control the server remotely.
For example, if the setup were running on a machine at an installation, one could send OSC messages 
to port 3339 to control the server. In typical use, one would SSH into the installation machine, then
run remote.py to form a controller connection to the genome server. The following messages can be used
to control the genome server:

/rjump <int:base-pair-position> [Jump to a particular base pair in the currently loaded genome file]
/ropen <string:genome-file> [Open a particular chromosome file for reading. 
							"/ropen 3" opens chromosome 3, "/ropen X" opens the X chromosome]
/rping [Receive an /recho message, to verify that the server is running]
/rreset [Clear all of the sequencers, and return the count of each amino acid to 0]
/rtransport <string:command> [Control the Live transport "/rtransport stop" stops playback,
							"/rtransport start" plays from the beginning, and "/rtransport continue"
							resumes playback from the current playhead position]
/rstatus [Print the current status: the current genome file, the number of amino acids read, and the
			estimated number of amino acids remaining in the current genome file]
"""
def remote_jump_handler(addr, tags, stuff, source):
	global cr
	global filename
	cr.loadChromosomeFile(filename)
	cr.seekPosition(stuff[0])
	msg = OSC.OSCMessage()
	msg.setAddress("/rprint")
	msg.append("Jump complete")
	out_c_remote.send(msg)

def remote_open_handler(addr, tags, stuff, source):
	global cr
	global filename
	filename = "../data/chromosomes/chr{}.fa".format(stuff[0])
	cr.loadChromosomeFile(filename)

def remote_ping_handler(addr, tags, stuff, source):
	global out_c_remote
	msg = OSC.OSCMessage()
	msg.setAddress("/recho")
	msg.append(time.time())
	out_c_remote.send(msg)

def remote_reset_handler(addr, tags, stuff, source):
	reset_handler(addr, tags, stuff, source)

def remote_transport_handler(addr, tags, stuff, source):
	if stuff and stuff[0] in ["start", "stop", "continue", "currenttime"]:
		send_transport_event(stuff[0])

def remote_status_handler(addr, tags, stuff, source):
	global out_c_remote
	global cr
	print "status handler"
	msg = OSC.OSCMessage()
	msg.setAddress("/rprint")
	msg.append("status---")
	msg.append("filename:")
	msg.append(cr.filename)
	msg.append("aminos_read:")
	msg.append(cr.aminoAcidsRead)
	msg.append("estimated_aminos:")
	msg.append(cr.estimatedTotalAminos)
	out_c_remote.send(msg)

## Receiving messages
in_c = OSC.OSCServer(('127.0.0.1', listening_port))

##		Messages from Max
in_c.addMsgHandler('/getAminoAcidCounts', get_amino_acid_handler)
in_c.addMsgHandler('/ping', ping_handler)
in_c.addMsgHandler('/read', read_handler)
in_c.addMsgHandler('/reset', reset_handler)
in_c.addMsgHandler('/step', step_handler)
in_c.addMsgHandler('/transport', transport_handler)

##		Messages from Remote
in_c.addMsgHandler('/rjump', remote_jump_handler)
in_c.addMsgHandler('/ropen', remote_open_handler)
in_c.addMsgHandler('/rping', remote_ping_handler)
in_c.addMsgHandler('/rreset', remote_reset_handler)
in_c.addMsgHandler('/rtransport', remote_transport_handler)
in_c.addMsgHandler('/rstatus', remote_status_handler)

## Sending messages
out_c_max = OSC.OSCClient()
out_c_max.connect(('127.0.0.1', max_sending_port))
out_c_remote = OSC.OSCClient()
out_c_remote.connect(('127.0.0.1', remote_sending_port))

############################## Start OSCServer
print "\nStarting OSCServer, listening on port {}, sending to port {}. Use ctrl-C to quit.".format(listening_port, max_sending_port)
st = threading.Thread( target = in_c.serve_forever )
st.start()

try :
    while 1 :
        time.sleep(5)

except KeyboardInterrupt :
    print "\nClosing OSCServer."
    in_c.close()
    print "Waiting for Server-thread to finish"
    st.join() ##!!!
    print "Done"