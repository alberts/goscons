import SCons.Util

def generate(env):
    env['GOC'] = 'gccgo'
    env['GOLINK'] = 'gccgo'
    env['GOOBJSUFFIX'] = '.o'
    env['GOLIBSUFFIX'] = '.gox'
    env['GOCCOM'] = '$GOC -pipe $GOCFLAGS ${_concat("-I ", GOPKGPATH, "", __env__)} -c -o $TARGET $SOURCES'
    env['GOLINKCOM'] = '$GOC -pipe $GOLINKFLAGS ${_concat("-I ", GOPKGPATH, "", __env__)} ${_concat("-Wl,-rpath ", GORPATH, "", __env__)} -o $TARGET $SOURCES'
    env['GOPACK'] = 'objcopy'
    env['GOPACKFLAGS'] = SCons.Util.CLVar('')
    env['GOPACKCOM'] = '$GOPACK -j .go_export $GOPACKFLAGS $SOURCES $TARGET'

def exists(env):
    return 1
