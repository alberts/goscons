import SCons.Util

def generate(env):
    env['GOC'] = 'gccgo'
    env['GOOBJSUFFIX'] = '.o'
    env['GOCCOM'] = '$GOC $GOCFLAGS -c -o $TARGET $SOURCES'
    env['GOPACK'] = 'ar'
    env['GOPACKFLAGS'] = SCons.Util.CLVar('cru')

def exists(env):
    return 1
