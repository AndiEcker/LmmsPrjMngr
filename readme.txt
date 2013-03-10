LMMS Project Manager
====================

Check, display/dump and export referenced external files of a LMMS project.


Installation
------------

On Linux:

Copy the the files LmmsPrjMngrMain.py and app_const.py to your machine and make shure you have
python 2.5 or higher, PyQt4 and the Qt runtime or SDK installed. Execute the tool with the following command line:

   python LmmsPrjMngrMain.py [options] [command line arguments]
   
   
On Windows:

Copy the win-exe-Vx.x.x subfolder to your machine and execute the tool with following command line:

   <PathToYourInstallationFolder>\LmmsPrjManager.exe [options] [command line args]
   


Dump Mode
---------

Executing the tool with a single command line argument (the LMMS project file) is activating the Dump or Display mode. In this mode this tool is printing a list of all the external files of the specified LMMS project to the standard output (on the console).



Export Mode
-----------

As soon as you pass also a second command line argument the tool is exporting the LMMS project together with the referenced external files to the folder that are specified by the second command line argument.

The third and optional command line argument/parameter called ExportMode is controlling the way how the path of the external files are handled. The currently four supported export mode argument values are (defaults to "backup" if omitted; case insensitive):

* absolutize  use absolute path (also changes path in lmms project file) - use for to exchange colaboration projects.
* backup      references to external files keep unchanged - use for to backup your LMMs project(s).
* factorize   copy user files into factory destination subfolder - use for to prepare a LMMS project to get a factory/example project.
* userize     copy factory files into user subfolder (working or data directory) - use for to put factory files of a different LMMS version into your user/data subfolders.



Command Line Options
--------------------

The following options are supported:

* -c/--compress   compress exported LMMS project file (mmpz format).
* -h/--help       show help message and quit.
* -u/--uncompress uncompress exported LMMS project file (mmp format).
* -v/--verbose	display more information about the tool actions.



Future Enhancements
-------------------

* Allow to re-import of exported LMMS project with full integration of external files into the
  LMMS environment (folder structure) of the destination machine.
* Determine appropriate destination samples subfolder name from the name of the sample/wave file (for factorize export mode).
* Proper graphical user interface


<EOF>
