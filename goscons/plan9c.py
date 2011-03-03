import SCons.Builder
import SCons.Node.FS
import SCons.Util

GoCCAction = SCons.Action.Action('$GOCCCOM', '$GOCCCOMSTR')

GoObjectBuilder = SCons.Builder.Builder(action=GoCCAction,
                                        source_factory=SCons.Node.FS.File,
                                        src_suffix='$CFILESUFFIX',
                                        suffix='$GOOBJSUFFIX')

def _go_ifarch(arch, v, env, f=lambda x: x, target=None, source=None):
    if arch == env['GOARCH']: return v
    return ''
    
def generate(env):
    env['_go_ifarch'] = _go_ifarch
    env['BUILDERS']['GoObject'] = GoObjectBuilder
    env['GOCFLAGS'] = SCons.Util.CLVar('')
    env['GOCCCOM'] = '$GOCC -o $TARGET $GOCFLAGS $_CPPINCFLAGS $SOURCES'
    env['INCPREFIX'] = '-I'

def exists(env):
    return 1
