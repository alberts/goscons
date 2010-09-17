from goscanner import GoScanner
import SCons.Builder
import SCons.Node.FS
import SCons.Util

GocAction = SCons.Action.Action('$GOCCOM', '$GOCCOMSTR')

GocBuilder = SCons.Builder.Builder(action=GocAction,
                                   source_factory=SCons.Node.FS.File,
                                   source_scanner=GoScanner,
                                   src_suffix='$GOFILESUFFIX',
                                   suffix='$GOOBJSUFFIX')

def generate(env):
    env['BUILDERS']['Goc'] = GocBuilder
    env['GOCFLAGS'] = SCons.Util.CLVar('')
    env['GOCCOM'] = '$GOC $( ${_concat("-I ", GOPKGPATH, "", __env__)} $) $GOCFLAGS -o $TARGET $SOURCES'

def exists(env):
    return 1
