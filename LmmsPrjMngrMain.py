'''
    LMMS Project Manager

Dump and export external file references of a LMMS project

Created on Feb 28, 2013

@author: andi de chigora (andi ecker)
'''
import sys                  # sys.argv/exit/platform

from PyQt4 import Qt        # qCompress()/qUncompress()
from PyQt4 import QtCore    # QFile/QDir/QFileInfo/QXmlStreamReader...
from PyQt4 import QtXml     # QDomDocument

# constants (more hard-coding in LmmsEnv.__init__())
CM_KEEP = 'keepCompress'
CM_COMPRESS = 'compress'
CM_UNCOMPRESS = 'uncompress'

OEM_ABSOLUTIZE = 'absolutize'
OEM_BACKUP = 'backup'
OEM_FACTORIZE = 'factorize'
OEM_USERIZE = 'userize'

# public command line option flags and default values
optCompress = CM_KEEP       # set by -c (compress) and -u (uncompress) option
optVerbose = False          # set by -v command line option


class ExternalReference(QtCore.QObject):
    """ external references (plugin file/key names):
        - AFP wave file: track/instrumenttrack/instrument/audiofileprocessor+src
        - TrippleOsc 3 user wave/shape files: track/instrumenttrack/instrument/tripleoscillator+userwavefile0..2
        - Vestige VST instrument: track/instrumenttrack/instrument/vestige+plugin
        - Patman patch file: track/instrumenttrack/instrument/patman+src
        - SF2 file: track/instrumenttrack/instrument/sf2player+src
        - Instrument 3 Lfo wave/shape files: track/instrumenttrack/eldata/elvol|elcut|elres+userwavefile
        - Instrument 3 Lfo wave/shape files: track/instrumenttrack/eldata/elvol|elcut|elres+userwavefile
        - Sample track: track/sampletco+src
        - VST Fx plugins: effect/vsteffectcontrols+plugin
        - ladspa/Vst Fx plugins: effect/key/attribute+value (name attribute value is "file" for manufactor name and "plugin" for plugin name), e.g.:
           * Dj flanger(ladspaeffect): <attribute value="dj_flanger_1438" name="file"/> <attribute value="djFlanger" name="plugin"/>
           * Caps Eq(ladspaeffect): <attribute value="caps" name="file"/> <attribute value="Eq" name="plugin"/>  
           * Calf Reverb(ladspaeffect): <attribute value="calf" name="file"/> <attribute value="Reverb" name="plugin"/>  
    """
    def __init__(self, desc, xmlPath, elemName, attrName, filePath, usedBy = 'DR'):
        self.desc = desc
        self.xmlPath = xmlPath      # currently not fully used only right(1) == '+' flag for element lists (like for ladspa plugin attribute element)  
        self.elemName = elemName
        self.attrName = attrName
        self.filePath = filePath  # if relative then check this subfolder underneath the user and the factory dirs
        self.usedBy = usedBy        # 'D' == dump, 'R' == export/replace


class LmmsEnv(QtCore.QObject):
    # use paths from LMMS resource configuration file (at QDir.home().absolutePath() + QDir::separator() + '.lmmsrc.xml') for to determine external file paths
    # .. taken from Win7 installation: <paths workingdir="C:/Users/aecker\lmms\" fldir="C:/Users/aecker\" stkdir="C:/Program Files/LMMS\data\stk/rawwaves/\" vstdir="C:\Program Files\LMMS\vst\"
    # ..                                      artwork="C:/Program Files/LMMS\data\themes/default/\" defaultsf2="" backgroundartwork="" laddir="C:/Program Files/LMMS\plugins\ladspa\"/>
    # .. FactoryDir and WorkingDir are needed for to get full path of sample/preset/vst files. The subfolders are hardcoded within config_mgr.h like:
    # .. const QString PROJECTS_PATH = "projects/";
    # .. const QString PRESETS_PATH = "presets/";
    # .. const QString SAMPLES_PATH = "samples/";
    # .. const QString DEFAULT_THEME_PATH = "themes/default/";
    # .. const QString LOCALE_PATH = "locale/";
    def __init__(self):
        super(LmmsEnv, self).__init__()
        # fix/hard-coded relative lmms home paths (either under /usr or /home)
        self.lmmsDir = QtCore.QString('.')     
        self.sampleDir = QtCore.QString('samples')
        self.presetDir = QtCore.QString('presets')
        #self.projectDir = QtCore.QString('projects')
        # dynamic fields: frist set to default values then try to find/read from lmms configuration file and OS
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):  # Mac OsX
            dInst = QtCore.QDir('/usr/local/share/lmms')
            if dInst.exists():
                self.instDir = QtCore.QString('/usr/local/share/lmms') 
            else:
                self.instDir = QtCore.QString('/usr/share/lmms') 
            self.workDir = QtCore.QString('~/lmms')
        else:                                    # Windows
            self.instDir = QtCore.QString('C:/Program Files/LMMS')
            self.workDir = QtCore.QString('$(HOME)/LMMS')     # c:/users/<name>/LMMS  ?!?!? 
        self.vstDir = QtCore.QString('')
        self.sf2Dir = QtCore.QString('')
        self.ladDir = QtCore.QString('')
        self.stkDir = QtCore.QString('')
        self.flDir = QtCore.QString('')
        if optVerbose:
            print("Checking LMMS Environment.") 
        rcFile = QtCore.QFile(QtCore.QDir.home().absolutePath() + QtCore.QDir.separator() + '.lmmsrc.xml')
        if not rcFile.exists():
            print("Error finding LMMS resource configuration/settings file .lmmsrc.xml")
            return
        if optVerbose:
            print("Found LMMS resource configuration/settings file %(fileDesc)s." % {'fileDesc' : rcFile.fileName()})
        if not rcFile.open(QtCore.QIODevice.ReadOnly):  ## | QtCore.QIODevice.Text):
            print("Error opening LMMS resource configuration file %(fileDesc)s!" % {'fileDesc' : rcFile.fileName()}) 
            return
        xtree = QtCore.QXmlStreamReader(rcFile.readAll())
        while not xtree.atEnd():
            xtree.readNext()
            if xtree.isStartElement() and xtree.name() == 'paths':
                self.workDir = xtree.attributes().value('workingdir').toString()
                self.vstDir = xtree.attributes().value('vstdir').toString()
                self.sf2Dir = xtree.attributes().value('defaultsf2').toString()
                self.ladDir = xtree.attributes().value('laddir').toString()
                self.stkDir = xtree.attributes().value('stkdir').toString()
                self.flDir = xtree.attributes().value('fldir').toString()
        rcFile.close()
        # check installation path (used for to find external factory files/samples, not available in .lmmsrc.xml)
        dInst = QtCore.QDir(self.instDir)
        if self.instDir == '' or not dInst.exists():
            self.instDir = QtCore.QString('')
            # try to get the installation path from stkDir
            nPos = str(self.stkDir).upper().find('LMMS')  #?!?!? QString has no method find
            if nPos >= 0:
                dInst = QtCore.QDir(self.stkDir[:nPos+4])
                if dInst.exists():
                    self.instDir = dInst.absolutePath()
        if optVerbose:
            print("Determined directories: instDir=%(instDir)s workDir=%(workDir)s vstDir=%(vstDir)s sf2Dir=%(sf2Dir)s ladDir=%(ladDir)s stkDir=%(stkDir)s flDir=%(flDir)s sampleDir=%(sampleDir)s presetDir=%(presetDir)s" 
                  % {'instDir' : self.instDir, 'workDir' : self.workDir, 'vstDir' : self.vstDir, 'sf2Dir' : self.sf2Dir, 'ladDir' : self.ladDir, 'stkDir' : self.stkDir, 'flDir' : self.flDir, 'sampleDir' : self.sampleDir, 'presetDir' : self.presetDir})
        


class LmmsProject(QtCore.QObject):
    def __init__(self, prjFileName, env, extRefs):
        super(LmmsProject, self).__init__()
        self.prjFileName = prjFileName
        self.env = env
        self.extRefs = extRefs
        self.fileCnt = 0
        self.prjPacked = (self.prjFileName[-4:].lower() == 'mmpz') 
        # load project file
        pfile = QtCore.QFile(self.prjFileName)
        if not pfile.open(QtCore.QIODevice.ReadOnly):  ## | QtCore.QIODevice.Text):
            print("Error opening LMMS Project file %(fileDesc)s!" % {'fileDesc' : self.prjFileName}) 
            self.prjContent = None
            return
        self.prjContent = pfile.readAll()
        if self.prjPacked:
            self.prjContent = Qt.qUncompress(self.prjContent)
        pfile.close()
        if optVerbose:
            print("Project file %(fileDesc)s loaded." % {'fileDesc' : self.prjFileName})
        

    def completeSourceFileInfo(self, fnam, extRef): 
        # check and possible complete path of external source file (passed in fnam)
        fiComplete = QtCore.QFileInfo(fnam)
        if fiComplete.isRelative() and not fiComplete.exists() and extRef.filePath:
            dirSep = QtCore.QDir.separator()
            subPath = QtCore.QDir(extRef.filePath)
            if subPath.isAbsolute():
                fiTemp = QtCore.QFileInfo(subPath.absolutePath() + dirSep + fnam)
            else:
                fiTemp = QtCore.QFileInfo(self.env.workDir + dirSep + subPath.path() + dirSep + fnam)
                if not fiTemp.exists() and self.env.instDir:
                    fiTemp = QtCore.QFileInfo(self.env.instDir + dirSep + subPath.path() + dirSep + fnam)
            if fiTemp.exists():
                fiComplete = fiTemp
        return fiComplete
    
    
    def composeDestDir(self, fnam, fiSource, extRef):
        fiOri = QtCore.QFileInfo(fnam)
        isAbs = fiOri.isAbsolute()
        dirSep = QtCore.QDir.separator()
        folderName = QtCore.QDir(extRef.filePath).dirName()
        subDirNames = QtCore.QFileInfo(self.prjFileName).baseName() + '_files' 
        if self.optExportMode <> OEM_ABSOLUTIZE:
            subDirNames += dirSep
            if isAbs:
                subDirNames += 'absolute' + dirSep + fiSoure.absoluteFilePath().replace(':', '_')
            else:
                if fiSource.absolutePath().startsWith(self.env.instDir) and self.optExportMode <> OEM_USERIZE:
                    subDirNames += 'factory'
                else:
                    subDirNames += 'user'
                subDirNames += dirSep + folderName
                if fiOri.path():
                    subDirNames += dirSep + fiOri.path()
        return QtCore.QDir(self.dExpFolder.absolutePath() + dirSep + subDirNames)


    def composeDestFileInfo(self, dDest, fiSource):
        fnam = fiSource.fileName()
        self.fileCnt += 1
        if self.optExportMode == OEM_ABSOLUTIZE:
            fnam = self.fileCnt.__str__() + '_' + fnam
        return QtCore.QFileInfo(dDest.absolutePath() + QtCore.QDir.separator() + fnam)

    
    def copyAndModifyExtFilePaths(self, extRef):
        extElements = self.doc.elementsByTagName(extRef.elemName)
        for nI in range(extElements.size()):
            elem = extElements.at(nI).toElement()
            fnam = elem.attribute(extRef.attrName)
            if fnam and fnam <> 'samples/empty.wav':
                # check and possible complete path of external source file
                fiSource = self.completeSourceFileInfo(fnam, extRef)
                # check if destination sub-folder exists already and create it if not
                dDest = self.composeDestDir(fnam, fiSource, extRef)
                if not dDest.exists():
                    if not dDest.mkpath("."):
                        print("Error creating destination folder %(folderName)s!" % {'folderName' : dDest.absolutePath()}) 
                        continue
                fiDest = self.composeDestFileInfo(dDest, fiSource)
                # update attribute with new file path
                if self.optExportMode == OEM_ABSOLUTIZE:
                    elem.setAttribute(extRef.attrName, fiDest.absoluteFilePath())
                if fiSource.absoluteFilePath() <> fiDest.absoluteFilePath():
                    # open sample file for to copy
                    sfile = QtCore.QFile(fiSource.absoluteFilePath())
                    if not sfile.open(QtCore.QIODevice.ReadOnly):
                        print("Error opening %(desc)s file %(fileDesc)s for copying!" % {'desc' : extRef.desc, 'fileDesc' : sfile.fileName()})
                    else:
                        # copy file and overwrite destination file if exists
                        if fiDest.exists() and not QtCore.QFile.remove(fiDest.absoluteFilePath()):   # lazy AND
                            print("Error overwriting %(desc)s file %(fileDesc)s!" % {'desc' : extRef.desc, 'fileDesc' : fiDest.absoluteFilePath()})
                        else:
                            if not sfile.copy(fiDest.absoluteFilePath()):
                                print("Error copying %(desc)s file to %(fileDesc)s!" % {'desc' : extRef.desc, 'fileDesc' : fiDest.absoluteFilePath()})
                            elif optVerbose:
                                print("Copied %(desc)s file to %(fileDesc)s!" % {'desc' : extRef.desc, 'fileDesc' : fiDest.absoluteFilePath()})
                        sfile.close()
            
        
    def exportToFolder(self, exportFolder, exportMode):
        # check/prepare/create destination folder
        self.dExpFolder = QtCore.QDir(exportFolder)
        self.optExportMode = exportMode
        if not self.dExpFolder.exists():
            if not self.dExpFolder.mkpath("."):    # using dExpFolder.path() or exportFolder instead of "." creates a duplicate folder with the same name within the just created folder
                print("Error creating destination folder %(folderName)s!" % {'folderName' : self.dExpFolder.cleanPath(exportFolder)}) 
                return
        # create project file info objects
        fiPrjSource = QtCore.QFileInfo(self.prjFileName)
        fnam = self.dExpFolder.absolutePath() + QtCore.QDir.separator() + fiPrjSource.completeBaseName()
        if self.dExpFolder.absolutePath() == fiPrjSource.absolutePath():
            fnam += 'Export'
        if self.prjPacked and optCompress == CM_UNCOMPRESS:
            fnam += '.mmp'
        elif not self.prjPacked and optCompress == CM_COMPRESS:
            fnam += '.mmpz'
        else:
            fnam += '.' + fiPrjSource.suffix()
        fiPrjDest = QtCore.QFileInfo(fnam)
        # read project file into xml dom
        self.doc = QtXml.QDomDocument();
        if not self.doc.setContent(self.prjContent):
            print("Malformed XML within LMMS Project file %(fileDesc)s!" % {'fileDesc' : fiPrjSource.absoluteFilePath()}) 
            return
        # copy files of this extRef type and modify their external file paths within the xml doc object
        for extRef in self.extRefs:
            if extRef.usedBy.find('R') >= 0: 
                self.copyAndModifyExtFilePaths(extRef)
        # save changed content back to new project file
        pfile = QtCore.QFile(fiPrjDest.absoluteFilePath())
        if not pfile.open(QtCore.QIODevice.Truncate | QtCore.QIODevice.WriteOnly):
            print("Error opening LMMS Project export file %(fileDesc)s for writing!" % {'fileDesc' : pfile.fileName()}) 
        else:
            xml = self.doc.toByteArray()
            if (self.prjPacked and optCompress <> CM_UNCOMPRESS) or optCompress == CM_COMPRESS:
                xml = Qt.qCompress(xml)
            pfile.write(xml)
            pfile.close()
            if optVerbose:
                print("Created new LMMS Project file %(fileDesc)s." % {'fileDesc' : pfile.fileName()})   ##fiPrjDest.absoluteFilePath()})
                        

    def determineExternalFiles(self):
        filenames = []
        xtree = QtCore.QXmlStreamReader(self.prjContent)
        lastElemName = None 
        while not xtree.atEnd():
            xtree.readNext()
            if xtree.isStartElement():
                extRefs = [extRef for extRef in self.extRefs 
                           if extRef.elemName == xtree.name() and (extRef.usedBy.find('D') >= 0 or optVerbose)]
                if lastElemName and (len(extRefs) == 0 or extRefs[0].elemName <> lastElemName):
                    # not works only if compound element is the last start element in the xml doc (will not happen)
                    filenames.append((compoundDesc + '=' if optVerbose else "" ) + compoundNames)
                    lastElemName = None
                for extRef in extRefs:
                    fnam = xtree.attributes().value(extRef.attrName).toString()
                    if fnam:
                        if extRef.xmlPath[-1:] == '+':      # collection/list of elements
                            if extRef.elemName == lastElemName:
                                compoundNames += ',' + fnam
                            else:
                                compoundDesc = extRef.desc
                                compoundNames = fnam
                                lastElemName = extRef.elemName
                        elif optVerbose: 
                            filenames.append(extRef.desc + '=' + fnam \
                                             + (" (" + completeSourceFileInfo(fnam, extRef).absoluteFilePath() \
                                                + ")" if QtCore.QFileInfo(fnam).isRelative() else ""))
                        else: 
                            filenames.append(completeSourceFileInfo(fnam, extRef).absoluteFilePath())
                                                                                      
        if xtree.hasError():
            print("Error parsing XML at line:col %(line)d:%(col)d (offset +%(charOffset)d): %(errText)s" \
                  % {'line' : xtree.lineNumber(), 'col' : xtree.columnNumber(), 
                     'charOffset' : xtree.characterOffset(), 'errText' : xtree.error()})
        #xtree.clear()        
        return filenames
        

def appVersion():
    from app_const import APP_TITLE, APP_VERSION
    print("%(appTitle)s - V %(appVersion)s --- check, dump and export LMMS project including external files" \
          % {'appTitle' : APP_TITLE, 'appVersion' : APP_VERSION})        

    
def usage():
    print("Usage:")
    print("%(appName)s [-h][-v] <LmmsProjectFileName>" % {'appName' : sys.argv[0]})
    print("  -or-")
    print("%(appName)s [-c][-h][-u][-v] <LmmsProjectFileName> <DestinationFolder> [<ExportMode>]" % {'appName' : sys.argv[0]})
    print
    print("Pass only the project file name as command line parameter if you want to dump a list of referrenced external files.")
    print
    print("If you also pass the path of the destination folder as the second command line parameter then the external files" \
          + " will be copied to the destination folder together with a new version of the LMMS project file.")
    print
    print('The optional ExportMode parameter affects the path of the external files.')
    print('Supported export mode parameter values (defaults to "' + OEM_BACKUP + '" if omitted; case insensitive):')
    print(' ' + OEM_ABSOLUTIZE + '  use absolute path (also changes path in lmms project file)')
    print(' ' + OEM_BACKUP + '      references to external files keep unchanged')
    print(' ' + OEM_FACTORIZE + '   copy user files into factory destination subfolder')
    print(' ' + OEM_USERIZE + '     copy factory files into user subfolder (working or data directory)')
    print
    print('Options:')
    print(' -c|--compress    store exported/destination lmms project file in compressed mmpz format')
    print(' -h|--help        display this help screen on console and quit')
    print(' -u|--uncompress  store exported/destination lmms project file in uncompressed mmp format')
    print(' -v|--verbose     protocol application actions more detailed on console')


if __name__ == '__main__':
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'chuv', ['compress', 'help', 'uncompress' 'verbose'])
    except getopt.GetoptError, err:
        appVersion()
        print str(err)    # unrecognized options
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-v', '--verbose'):
            optVerbose = True
        elif opt in ('-c', '--compress'):
            optCompress = CM_COMPRESS
        elif opt in ('-u', '--uncompress'):
            optCompress = CM_UNCOMPRESS
        else:    # elif opt in ('-h', "--help"):
            appVersion()
            usage()
            sys.exit()
    if len(args) < 1 or len(args) > 3:
        appVersion()
        usage()
        sys.exit(1)
    
    if optVerbose:
        appVersion()    

    # determine LMMS environment on this machine
    env = LmmsEnv()
    # specify types of external references
    extRefs = [
               ExternalReference('Audiofileprocessor wave',  'track/instrumenttrack/instrument', 'audiofileprocessor', 'src', env.sampleDir),
               ExternalReference('TrippleOsc 1st user wave/shape', 'track/instrumenttrack/instrument', 'tripleoscillator', 'userwavefile0', env.lmmsDir),
               ExternalReference('TrippleOsc 2nd user wave/shape', 'track/instrumenttrack/instrument', 'tripleoscillator', 'userwavefile1', env.lmmsDir),
               ExternalReference('TrippleOsc 3rd user wave/shape', 'track/instrumenttrack/instrument', 'tripleoscillator', 'userwavefile2', env.lmmsDir),
               ExternalReference('Vestige VST instrument dll', 'track/instrumenttrack/instrument', 'vestige', 'plugin', env.vstDir),
               ExternalReference('Patman patch', 'track/instrumenttrack/instrument', 'patman', 'src', env.sampleDir),
               ExternalReference('Soundfound 2', 'track/instrumenttrack/instrument', 'sf2player', 'src', env.sampleDir),   # ?!?!? soundfont resource configuration setting is not used (only used by MidiImport.cpp) ?!?!?
               ExternalReference('Instrument vol Lfo wave/shape', 'track/instrumenttrack/eldata', 'elvol', 'userwavefile', env.sampleDir),
               ExternalReference('Instrument cutoff Lfo wave/shape', 'track/instrumenttrack/eldata', 'elcut', 'userwavefile', env.sampleDir),
               ExternalReference('Instrument res Lfo wave/shape', 'track/instrumenttrack/eldata', 'elres', 'userwavefile', env.sampleDir),
               ExternalReference('Sample track', 'track', 'sampletco', 'src', env.sampleDir),
               ExternalReference('VST Fx plugin/dll', 'effect', 'vsteffectcontrols', 'plugin', env.vstDir),
               ExternalReference('Fx plugin', 'effect/key+', 'attribute', 'value', env.ladDir, '')   ## attribute is used for ladspa and VST fx plugins (although for VST the same value is in vsteffectcontrols+plugin)
            ]
    # load LMMS project
    prj = LmmsProject(args[0], env, extRefs)
    if prj.prjContent == None:
        sys.exit(3)
    
    # either dump or export/replace all the external references
    if len(args) >= 2:
        prj.exportToFolder(args[1], args[2].lower() if len(args) >= 3 else OEM_BACKUP)
        if optVerbose:
            print("Exported %(numFiles)d external files to %(expDir)s" % {'numFiles' : prj.fileCnt, 'expDir' : prj.dExpFolder.absolutePath()})
    else:
        fileDescs = prj.determineExternalFiles()
        if optVerbose:
            print("Found %(numFiles)d external file references:" % {'numFiles' : len(fileDescs)})
        for fileDesc in fileDescs:
            print(fileDesc)
    
# EOF
