#!/usr/bin/env python
# genome_server.py

"""
Main entry point for the Python portion of the project. Loads a chromosome file in the .fa format,
and offers an OSC endpoint that can be used to read through the chromosome, and to consume MIDI events
generated by interpreting the chromosome code.
"""

import sys
import time, threading
import OSC
from chromosome_reader import *
from conductor import *

listening_port = 3337
sending_port = 3338
filename = sys.argv[1]

## State setup
cr = ChromosomeReader(filename)
cn = Conductor()

## OSC Handlers
def density_handler(addr, tags, stuff, source):
	global cn
	channel = stuff[0]
	density = stuff[1]
	cn.setDensity(channel, density)

def get_amino_acid_handler(addr, tags, stuff, source):
	global out_c
	global cn
	msg = OSC.OSCMessage()
	msg.setAddress("/aminoAcidCounts")
	for cnt in cn.getAminoAcidCounts():
		msg.append(cnt)
	out_c.send(msg)

def ping_handler(addr, tags, stuff, source):
	send_ping_event()

def reset_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /reset address. Moves the curson back to the beginning of the current
	chromosome file, and clears all of the current sequencers
	"""
	global filename
	global cr
	global cn
	print "Resetting"
	cr.loadChromosomeFile(filename)
	cn.reset()

def read_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /read address. Advances the cursor through the genome by a single amino
	acid. Sends a message with the /ready address when the amino acid has been read
	"""
	global cr
	global cn

	toRead = 1
	if len(stuff) > 0:
		toRead = stuff[0]

	for _ in range(toRead):
		if cr.hasNext():
			cn.addAmino(cr.nextAmino())
		else:
			break
	send_read_complete_event()

def step_handler(addr, tags, stuff, source):
	"""
	Handles messages with the /step address. The message should have a single argument, an integer
	that is the current beat. Will send a message to /midi with all of the midi messages associated with
	that beat.
	"""
	midiEvents = cn.processStep(stuff[0])
	send_midi_events(midiEvents)

## OSC Senders
def send_midi_events(events):
	global out_c
	msg = OSC.OSCMessage()
	msg.setAddress("/midi")
	for event in events:
		for i in event:
			msg.append(i)
	out_c.send(msg)

def send_ping_event():
	global out_c
	msg = OSC.OSCMessage()
	msg.setAddress("/echo")
	msg.append(time.time())
	out_c.send(msg)

def send_read_complete_event():
	global out_c
	global cr
	msg = OSC.OSCMessage()
	msg.setAddress("/ready")
	msg.append(cr.getBasePairsRead())
	msg.append(cr.getAminoAcidsRead())
	out_c.send(msg)

## Receiving messages
in_c = OSC.OSCServer(('127.0.0.1', listening_port))
in_c.addMsgHandler('/density', density_handler)
in_c.addMsgHandler('/getAminoAcidCounts', get_amino_acid_handler)
in_c.addMsgHandler('/ping', ping_handler)
in_c.addMsgHandler('/read', read_handler)
in_c.addMsgHandler('/reset', reset_handler)
in_c.addMsgHandler('/step', step_handler)

## Sending messages
out_c = OSC.OSCClient()
out_c.connect(('127.0.0.1', sending_port))

############################## Start OSCServer
print "\nStarting OSCServer, listening on port {}, sending to port {}. Use ctrl-C to quit.".format(listening_port, sending_port)
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