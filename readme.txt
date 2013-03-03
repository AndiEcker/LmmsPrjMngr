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

The third and optional ExportMode parameter affects the path of the external files.
Supported export mode parameter values (defaults to "backup" if omitted; case insensitive):
 - absolutize  use absolute path (also changes path in lmms project file)
 - backup      references to external files keep unchanged
 - factorize   copy user files into factory destination subfolder
 - userize     copy factory files into user subfolder (working or data directory)


Options
-------

The following options are supported:
-c/--compress   compress exported LMMS project file (mmpz format).
-h/--help       show help message and quit.
-u/--uncompress uncompress exported LMMS project file (mmp format).
-v/--verbose	display more information about the tool actions.



Installation
------------

On Linux: copy the the files LmmsPrjMngrMain.py and app_const.py to your machine and make shure you have
python 2.5 or higher, PyQt4 and the Qt runtime or SDK installed. Execute the tool with the following command line:
   python LmmsPrjMngrMain.py [options] [command line args]
   
   
On Windows: copy the win-exe-Vx.x subfolder to your machine and execute the tool with following command line:
   LmmsPrjMngr.exe [options] [command line args]
   

Future Enhancements
-------------------

* Allow to re-import of exported LMMS project with full integration of external files into the
  LMMS environment (folder structure) of the destination machine.
* GUI
* Determine appropriate destination samples subfolder name from the name of the sample/wave file (for factorize export mode).

<EOF>
