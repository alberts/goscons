import SCons.Builder
import SCons.Node.FS
import SCons.Util

P9CCAction = SCons.Action.Action('$P9CCCOM', '$P9CCCOMSTR')

P9ObjectBuilder = SCons.Builder.Builder(action=P9CCAction,
                                        source_factory=SCons.Node.FS.File,
                                        src_suffix='$GOFILESUFFIX',
                                        suffix='$GOOBJSUFFIX')

def generate(env):
    env['BUILDERS']['P9Object'] = P9ObjectBuilder
    env['P9CC'] = '6c'
    env['P9CFLAGS'] = SCons.Util.CLVar('')
    env['P9CCCOM'] = '$P9CC -o $TARGET $P9CFLAGS $SOURCES'

def exists(env):
    return 1
