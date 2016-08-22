#!/usr/bin/python

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
def reset_handler(addr, tags, stuff, source):
	global filename
	global cr
	global cn
	cr.loadChromosomeFile(filename)
	cn.reset()

def read_handler(addr, tags, stuff, source):
	global cr
	global cn
	if cr.hasNext():
		cn.addAmino(cr.nextAmino())
		send_read_complete_event()

def step_handler(addr, tags, stuff, source):
	midiEvents = cn.midiEventsForStep(stuff[0])
	send_midi_events(midiEvents)

## OSC Senders
def send_read_complete_event():
	global out_c
	msg = OSC.OSCMessage()
	msg.setAddress("/ready")
	out_c.send(msg)

def send_midi_events(events):
	global out_c
	msg = OSC.OSCMessage()
	msg.setAddress("/midi")
	for event in events:
		for i in event:
			msg.append(i)
	out_c.send(msg)

## Receiving messages
in_c = OSC.OSCServer(('127.0.0.1', listening_port))
in_c.addMsgHandler('/reset', reset_handler)
in_c.addMsgHandler('/read', read_handler)
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