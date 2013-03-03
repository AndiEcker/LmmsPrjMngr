LMMS Project Manager 0.9
========================

Check, display/dump and export LMMS projects including referenced external files.


Dump Mode
---------

The Dump or Display mode is used if you're executing this tool with a single command line argument,
that is specifying the LMMS project file name. In this mode this tool is printing the external files
of the LMMS project to the standard output (on the console).


Export Mode
-----------

As soon as you pass also a second command line argument the tool is exporting the LMMS project
together with the referenced external files to the folder that are specified in the second
command line argument.


Options
-------

The following options are supported:
-h/--help		show help message and quit.
-
-v/--verbose	display more information about the tool actions.



Installation
------------

On Linux: copy the the files LmmsPrjMngrMain.py and app_const.py to your machine and make shure you have
python, pyqt and the Qt runtime installed. Execute the tool with the following command line:
   python LmmsPrjMngrMain.py [options] [command line args]
   
   
On Windows: copy the dist folder to your machine and execute the tool with following command line:
   LmmsPrjMngr.exe [options] [command line args]
   

Future Enhancements
-------------------

* Allow to re-import of exported LMMS project with full integration of external files into the
  LMMS environment (folder structure) of the destination machine.
* GUI

<EOF>
