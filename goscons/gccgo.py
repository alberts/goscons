import SCons.Util
import goutils
import os

IMPORTS = (('', '.gox'), ('', '.o'), ('lib', '.so'), ('lib', '.a'))

def find_package(env, pkg, path):
    pkgparts = pkg.split('/')
    for prefix, suffix in IMPORTS:
        pkgfile = os.path.join(*(pkgparts[:-1]+[prefix+pkgparts[-1]+suffix]))
        pkgpath = env.FindFile(pkgfile, path)
        if pkgpath is not None:
            return pkgpath
    return None

def generate(env):
    env['GCCGOPREFIX'] = '/usr/local'
    env['GOC'] = 'gccgo'
    env['GOLINK'] = 'gccgo'
    env['GOOBJSUFFIX'] = '.o'
    env['GOLIBPREFIX'] = 'lib'
    env['GOLIBSUFFIX'] = '.a'
    env['GOCCOM'] = '$GOC $FGOPREFIX -pipe $GOCFLAGS ${_concat("-I ", GOPKGPATH, "", __env__)} -c -o $TARGET $SOURCES'
    env['GOLINKCOM'] = '$GOC -pipe -static -pthread $GOLINKFLAGS -o $TARGET $SOURCES -lgobegin -lgo'
    env['GOPACK'] = 'ar'
    env['GOPACKFLAGS'] = SCons.Util.CLVar('cru')
    env['GOPACKCOM'] = '$GOPACK $GOPACKFLAGS $TARGET $SOURCES'
    # TODO pkgpath depends on arch
    env['GOPKGPATH'] = ['$GOPROJPKGPATH', '$GODEPPKGPATH', '$GCCGOPREFIX/lib64']
    env.AddMethod(find_package, 'FindGoPackage')
    env['GOTESTBIN'] = 'a.out'

def exists(env):
    return 1
