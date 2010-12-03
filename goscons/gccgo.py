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

def _go_prefix(source, env):
    prefix = env.subst('${GOPREFIX}') + goutils.package_name(source[0], env)
    if len(prefix) > 0:
        return '-fgo-prefix=' + prefix
    return ''

def _go_rpath(lst, env, f=lambda x: x, target=None, source=None):
    if not lst: return lst
    l = f(SCons.PathList.PathList(lst).subst_path(env, target, source))
    if l is not None: lst = l
    return ' '.join(['-Wl,-rpath,' + p.abspath for p in lst])

def generate(env):
    env['_go_prefix'] = _go_prefix
    env['_go_rpath'] = _go_rpath
    env['GCCGOPREFIX'] = '/usr/local'
    env['GOC'] = 'gccgo'
    env['GOLINK'] = 'gccgo'
    env['GOOBJSUFFIX'] = '.o'
    env['GOLIBPREFIX'] = 'lib'
    env['GOLIBSUFFIX'] = '.a'
    env['GOCCOM'] = '$GOC ${_go_prefix(SOURCES, __env__)} -pipe $GOCFLAGS ${_concat("-I ", GOPKGPATH, "", __env__)} -c -o $TARGET $SOURCES'
    #env['GOLINKCOM'] = '$GOC -pipe -static -pthread $GOLINKFLAGS ${_concat("-I ", GOPKGPATH, "", __env__)} ${_go_rpath(GORPATH, __env__)} -o $TARGET $SOURCES -lgobegin -lgo'
    env['GOLINKCOM'] = '$GOC -pipe -static -pthread $GOLINKFLAGS ${_go_rpath(GORPATH, __env__)} -o $TARGET $SOURCES -lgobegin -lgo'
    env['GOPACK'] = 'ar'
    env['GOPACKFLAGS'] = SCons.Util.CLVar('cru')
    env['GOPACKCOM'] = '$GOPACK $GOPACKFLAGS $TARGET $SOURCES'
    # TODO pkgpath depends on arch
    env['GOPKGPATH'] = ['$GOPROJPKGPATH', '$GCCGOPREFIX/lib64']
    env['GORPATH'] = ['$GOPROJPKGPATH']
    env.AddMethod(find_package, 'FindGoPackage')

def exists(env):
    return 1
