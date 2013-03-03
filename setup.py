'''
    app builder and installer

Build binaries by running the command 'python setup.py py2exe'

Created on Feb 28, 2013

@author: andi de chigora (andi ecker)
'''
import sys, glob
#sys.path.append("C:\\WINDOWS\\WinSxS\\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.30729.1_x-ww_6f74963e")            ## work on my home WinXP VM
sys.path.append("C:\\WINDOWS\\WinSxS\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.4148_none_5090ab56bcba71c2")  ## works on my Win7 dev VM
#sys.path.append("C:\\WINDOWS\\WinSxS\\x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.30729.1_none_e163563597edeada")    ## also works on my Win7 dev VM

from distutils.core import setup
import py2exe
# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")

from app_const import APP_TITLE, APP_VERSION


setup(name = APP_TITLE,
      version = APP_VERSION,
      console = [ dict(script = "LmmsPrjMngrMain.py", dest_base = "LmmsProjectManager") ], 
      options = dict(py2exe = dict(includes = [ "sip" ])),
      data_files = [ ("imageformats", glob.glob(sys.prefix + "/Lib/site-packages/PyQt4/plugins/imageformats/*.dll")) ],
      )

