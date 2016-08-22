# thesoundoflife
The Sounds of Life

## Introduction
Read through a chromosome, transforming the genetic code into algorithmic music. The system has three parts, in Max, Ableton Live and Python. The Python server loads a chromosome file in the .fa format, which contains the characters NCATGcatg, corresponding to the base pairs in a DNA strand. The server reads through the sequence, and interprets it to create musical events and patterns. Ableton Live contains the samples and instruments that generate the sound itself. Max attaches itself to the Live transport, sending timing information to Python. When the Python responds with MIDI events, Max forwards those to the Live set to generate sound.