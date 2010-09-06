import SCons.Builder
import SCons.Node.FS
import SCons.Util

GopackAction = SCons.Action.Action('$GOPACKCOM', '$GOPACKCOMSTR')

GopackBuilder = SCons.Builder.Builder(action=GopackAction,
                                      source_factory=SCons.Node.FS.File,
                                      src_suffix='$GOOBJSUFFIX',
                                      suffix='$GOLIBSUFFIX')

def generate(env):
    env['BUILDERS']['Gopack'] = GopackBuilder
    env['GOPACK'] = 'gopack'
    env['GOPACKFLAGS'] = SCons.Util.CLVar('grc')
    env['GOPACKCOM'] = '$GOPACK $GOPACKFLAGS $TARGET $SOURCES'
    env['GOLIBSUFFIX'] = '.a'

def exists(env):
    return env.Detect('gopack')
