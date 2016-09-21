import OSC
import time, threading

"""
Run this script to launch a simple application for controlling a genome_server process running on the same machine.
In typical use, the genome_server process would already be running on an installation machine. A remote user would 
then SSH into the installation machine and run this script, remote.py. This script creates a prompt that reads a 
small set of commands for controlling the genome_server process. Type one of these commands and press return to execute.

Commands:
	ping
		Attempts to communicate with the genome_server process. The genome_server process should respond
		with the current time.
	stop
		Stop the Live transport (pause playback)
	start
		Begin playback from the beginning of the timeline (go to step 0)
	continue
		Resume playback from the current step position
	currenttime
		Return the current playback position in bars beats ticks
	currentstatus
		Print the current geonome file, and current position within that file
	open <x>
		Open the file for chromosome <x>. "open 1" will open chromosome 1, and "open X" will open chromosome X
	jump <x>
		Jumps to the base pair at position <x> in the current chromosome file
	exit
		Stop this script
"""

conductor_port = 3337
listening_port = 3339

## Handlers
def remote_print_handler(addr, tags, stuff, source):
	global out_c
	print("timestamp: " + str(time.time()))
	print("\t" + " ".join(map(str, stuff)))
	print("> ")

## Sending messages
out_c = OSC.OSCClient()
out_c.connect(('127.0.0.1', conductor_port))

## Receiving messages
in_c = OSC.OSCServer(('127.0.0.1', listening_port))
in_c.addMsgHandler('/rprint', remote_print_handler)
in_c.addMsgHandler('/recho', remote_print_handler)

print "\nStarting OSCServer, listening on port {}, sending to port {}. Use ctrl-C to quit.".format(listening_port, conductor_port)
st = threading.Thread( target = in_c.serve_forever )
st.start()

try:
	while 1:
		ip = raw_input('Remote sound of life server command:\n> ')
		if ip == "ping":
			msg = OSC.OSCMessage()
			msg.setAddress("/rping")
			out_c.send(msg)
		elif ip in ["stop", "start", "continue", "currenttime"]:
			msg = OSC.OSCMessage()
			msg.setAddress("/rtransport")
			msg.append(ip)
			out_c.send(msg)
		elif ip == "currentstatus":
			msg = OSC.OSCMessage()
			msg.setAddress("/rstatus")
			out_c.send(msg)
		elif ip == "reset":
			msg = OSC.OSCMessage()
			msg.setAddress("/rreset")
			out_c.send(msg)
		elif ip[0:4] == "open":
			pts = ip.split(" ")
			try:
				v = pts[1]
				msg = OSC.OSCMessage()
				msg.setAddress("/ropen")
				msg.append(v)
				out_c.send(msg)
			except:
				print ("open must be followed by the name of a chromosome to open (1-22, X or Y)")
		elif ip[0:4] == "jump":
			pts = ip.split(" ")
			try:
				v = int(pts[1])
				msg = OSC.OSCMessage()
				msg.setAddress("/rjump")
				msg.append(v)
				out_c.send(msg)
			except:
				print ("jump must be followed by a position to jump to, in amino acids")
		elif ip == "exit":
			break;
		elif ip == "help":
			print """Commands:
ping
	Attempts to communicate with the genome_server process. The genome_server process should respond
	with the current time.
stop
	Stop the Live transport (pause playback)
start
	Begin playback from the beginning of the timeline (go to step 0)
continue
	Resume playback from the current step position
currenttime
	Return the current playback position in bars beats ticks
currentstatus
	Print the current geonome file, and current position within that file
open <x>
	Open the file for chromosome <x>. "open 1" will open chromosome 1, and "open X" will open chromosome X
jump <x>
	Jumps to the base pair at position <x> in the current chromosome file
exit
	Stop this script

			"""
		else:
			print ("Unrecognized command. exit to exit, help to view available commands")
finally:
	print "\nClosing OSCServer."
	in_c.close()
	print "Waiting for Server-thread to finish"
	st.join() ##!!!
	print "Done"