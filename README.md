## Uplause Audio Analyzer

This is an old reference implementation.

Basically it's a tool for listening to N many audio devices and N many channels and broadcasting audio data from them to a control tool.

The control tool creates a TCP connection, gets a list of audio devices, and asks for data from a device & channels. The audio analyzer then starts streaming data (RMS only right now)

Relevant files are mostly:
main.py
server.py
audio.py

Requirements:  
Python 3.4+ (tested on 3.5.2)  
PyAudio  
NumPy  
SciPy  
cx_freeze  
Toml  
SimpleWebSocketServer  
requests  
ntp 

Quick(ish) & dirty:  
Py 3.5 -> https://www.python.org/downloads/  
Visual Studio Build Tools 2015 -> http://go.microsoft.com/fwlink/?LinkId=691126  
PyAudio -> http://www.lfd.uci.edu/~gohlke/pythonlibs/ (note: right bitness (32 probably) and right Python version) Install with: pip install <file>.whl  
NumPy & SciPy -> http://www.lfd.uci.edu/~gohlke/pythonlibs/ (note: bitness and Python version) Select "+MLK, NOT Vanilla" for NumPy. Install both NumPy and SciPy with: pip install <file>.whl  
Toml -> pip install toml  
SimpleWebSocketServer -> pip install git+https://github.com/dpallot/simple-websocket-server.git  
requests -> pip install requests  
ntplib ->  pip install ntplib  
cx_freeze -> https://github.com/sekrause/cx_Freeze-Wheels/blob/master/cx_Freeze-5.0-cp35-cp35m-win32.whl & pip install cx_Freeze-5.0-cp35-cp35m-win32.whl  

Visual studio 2015 redistributable needed, http://www.microsoft.com/en-us/download/details.aspx?id=48145 pick x86 version.