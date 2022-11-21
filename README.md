# hrctl
Hardrock 50 Amp remote control via quisk

hrctl.py - talks to a Hardrock 50 Amp via its USB serial port and provides a JSON-RPC service to fetch the current status and initiate tune

hermes_quisk.py - quisk widget addition to add a tune button and the status output. Status won't be updated during transmit (the Hardrock 50 disables serial communication during TX).

Q'n'D P'o'C, works for me, feel free to raise PR for enhancements
