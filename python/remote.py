import OSC
import time, threading

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
		else:
			print ("Unrecognized command. exit to exit, help to view available commands")

except KeyboardInterrupt :
    print "\nClosing OSCServer."
    in_c.close()
    print "Waiting for Server-thread to finish"
    st.join() ##!!!
    print "Done"