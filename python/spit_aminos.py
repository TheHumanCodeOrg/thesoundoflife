#!/usr/bin/python

import sys
import json
import time, threading
import OSC

with open("../data/dna_key.json") as f:
	dna_key = json.load(f)

codons = dna_key['codons']
ascii2idx = dna_key['ascii2idx']
idx2class = dna_key['idx2class']

listening_port = 3337
sending_port = 3338
filename = sys.argv[1]

chromo = 0
chunk = 0
chunksize = 10000
chunkidx = 0
buf = [0 for x in range(3)]
idx = 0

def load_chromosome(filename):
	global chromo
	global buf
	global idx
	if (chromo):
		chromo.close()
	chromo = open(filename, 'r')
	chromo.readline()
	buf = [0 for x in range(3)]
	idx = 0
	load_next_chunk()

def load_next_chunk():
	global chromo
	global chunk
	global chunkidx
	chunk = chromo.read(chunksize)
	chunkidx = 0

def process(buf):
	global codons
	buf = "".join(buf).upper()
	cod = codons[buf]
	return cod

def reset_handler(addr, tags, stuff, source):
	global filename
	load_chromosome(filename)

def step_handler(addr, tags, stuff, source):
	global idx
	global buf
	global chromo
	global chunkidx
	termine = False
	while (idx < 3):

		## Try to read in the next chunk
		if (chunkidx >= len(chunk)):
			load_next_chunk();
			if (len(chunk) == 0):
				termine = True
				break

		ch = chunk[chunkidx]
		chunkidx = chunkidx + 1
		if (ch is 'N'):
			idx = 0
		elif ch in 'CATGcatg':
			buf[idx] = ch
			idx = idx + 1
	idx = 0
	if not termine:
		out_aa = process(buf)
		send_amino(out_aa)

def send_amino(aa):
	global out_c
	global dna_key
	msg = OSC.OSCMessage()
	msg.setAddress("/amino")
	msg.append(aa)
	if aa != "Stop":
		aa_idx = ascii2idx[str(ord(aa))]
		aa_class = idx2class[str(aa_idx)]
		msg.append(aa_class)
	out_c.send(msg)

load_chromosome(sys.argv[1])

## Receiving messages
in_c = OSC.OSCServer(('127.0.0.1', listening_port))
in_c.addMsgHandler('/reset', reset_handler)
in_c.addMsgHandler('/step', step_handler)

## Sending messages
out_c = OSC.OSCClient()
out_c.connect(('127.0.0.1', sending_port))

############################## Start OSCServer
print "\nStarting OSCServer. Use ctrl-C to quit."
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