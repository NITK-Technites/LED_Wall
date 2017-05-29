A simple GUI consisting of a file chooser(to select the program and song) and a way to generate a shell script to run the program via terminal.

-----------------------------------------------------------

To compile gui.cpp, type

``g++ gui.cpp -o gui `pkg-config gtkmm-3.0 --libs --cflags` ``

on terminal in the working directory

-----------------------------------------------------------

To run, type

`./gui`

on terminal in the working directory

-----------------------------------------------------------

Note: The shell script generated the first time need to be made executable. Type

`chmod 755 run.sh`

on terminal in the working directory

-----------------------------------------------------------

Dependencies: libgtkmm-3.0-dev (To install, type `sudo apt-get install libgtkmm-3.0-dev` on terminal)
