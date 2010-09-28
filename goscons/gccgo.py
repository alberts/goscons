import SCons.Util
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

def _go_prefix(source):
    # TODO figure out why this attribute sometimes has more than one
    # element in its list
    return source.attributes.go_package[0]

def generate(env):
    env['_go_prefix'] = _go_prefix
    env['GCCGOPREFIX'] = '/usr/local'
    env['GOC'] = 'gccgo'
    env['GOLINK'] = 'gccgo'
    env['GOOBJSUFFIX'] = '.o'
    env['GOLIBPREFIX'] = 'lib'
    env['GOLIBSUFFIX'] = '.a'
    env['GOCCOM'] = '$GOC -fgo-prefix=${GOPREFIX}${_go_prefix(SOURCES)} -pipe $GOCFLAGS ${_concat("-I ", GOPKGPATH, "", __env__)} -c -o $TARGET $SOURCES'
    # TODO use abspath for rpath
    env['GOLINKCOM'] = '$GOC -pipe -static -pthread $GOLINKFLAGS ${_concat("-I ", GOPKGPATH, "", __env__)} ${_concat("-Wl,-rpath,", GORPATH, "", __env__)} -o $TARGET $SOURCES -lgobegin -lgo'
    env['GOPACK'] = 'ar'
    env['GOPACKFLAGS'] = SCons.Util.CLVar('cru')
    env['GOPACKCOM'] = '$GOPACK $GOPACKFLAGS $TARGET $SOURCES'
    # TODO pkgpath depends on arch
    env['GOPKGPATH'] = ['$GOPROJPKGPATH', '$GCCGOPREFIX/lib64']
    env['GORPATH'] = ['$GOPROJPKGPATH']
    env.AddMethod(find_package, 'FindGoPackage')

def exists(env):
    return 1
