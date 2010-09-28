from subprocess import Popen, PIPE
import SCons.Node.FS
import glob
import goutils
import os.path

GOARCH = set(['386','amd64','arm'])
GOOS = set(['bsd','unix','linux','windows','darwin','nacl','freebsd'])
GOOS_BSD = set(['freebsd','darwin'])
GOOS_UNIX = set(['freebsd','darwin','linux','nacl'])

def goos_goarch():
    for goos in GOOS:
        for goarch in GOARCH:
            yield goos, goarch

GOOS_GOARCH = set([x for x in goos_goarch()])

def is_os_arch_source(source):
    parts = source.name.split('_')
    if len(parts)<2: return False
    os_arch = parts[-2], parts[-1].split('.',1)[0]
    if os_arch in GOOS_GOARCH:
        return os_arch
    return None

def is_arch_source(source):
    if not source.name.find('_')>=0:
        return False
    arch = source.name.split('_')[-1].split('.',1)[0]
    if arch in GOARCH:
        return arch
    return None

def is_os_source(source):
    if not source.name.find('_')>=0:
        return False
    os = source.name.split('_')[-1].split('.',1)[0]
    if os in GOOS:
        return os
    return None

def is_source(source, env):
    if source.name=='_cgo_gotypes.go': return False
    if source.name.endswith('.cgo1.go'): return False
    if source.name.endswith('_test.go'): return False
    if source.name=='_testmain.go': return False
    arch = is_arch_source(source)
    if arch:
        os_arch = is_os_arch_source(source)
        if os_arch:
            os = os_arch[0]
            if os=='bsd' and env['GOOS'] in GOOS_BSD:
                return True
            elif os=='unix' and env['GOOS'] in GOOS_UNIX:
                return True
            return os_arch==(env['GOOS'], env['GOARCH'])
        return arch==env['GOARCH']
    os = is_os_source(source)
    if os:
        if os=='bsd' and env['GOOS'] in GOOS_BSD:
            return True
        elif os=='unix' and env['GOOS'] in GOOS_UNIX:
            return True
        return os==env['GOOS']
    return True

def gotest(env, pkg, srcdir, gofiles, cgo_obj, cgolib, *args, **kw):
    pkgname = pkg.replace(os.sep, '/')
    source = sorted(srcdir.glob('*_test.go'))
    if len(source)==0: return
    obj = env.subst('_gotest_$GOOBJSUFFIX')
    objfiles = env.Goc(srcdir.File(obj), source + gofiles, *args, **kw)
    testpkgdir = srcdir.Dir('_test').Dir(pkg).dir
    testpkgfile = testpkgdir.File(env.subst('${GOLIBPREFIX}'+srcdir.name+'${GOLIBSUFFIX}'))
    testpkg = env.Gopack(testpkgfile, objfiles + cgo_obj, *args, **kw)
    gopkgpath = [srcdir.Dir('_test'), '$GOPKGPATH']
    testmain_obj = env.Goc(env.GoTestMain(source, GOPACKAGE=pkgname), GOPKGPATH=gopkgpath)
    bin = env.Golink(srcdir.File(env.subst('$GOTESTBIN')), testmain_obj, GOPKGPATH=gopkgpath)
    # explicitly depend on the package's cgo lib, if any
    env.Depends(bin, cgolib)
    return bin

# TODO need to propogate args, kw into env
def gopackage(env, srcdir, basedir=None, *args, **kw):
    fs = SCons.Node.FS.get_default_fs()
    srcdir = fs.Dir(srcdir)
    if basedir is None:
        basedir = srcdir.dir
    else:
        basedir = fs.Dir(basedir)

    source = sorted(srcdir.glob('*.go'))
    source = filter(lambda x: is_source(x, env), source)
    cgofiles = filter(lambda x: goutils.is_cgo_input(x, env), source)
    gofiles = sorted(list(set(source)-set(cgofiles)))

    if len(cgofiles)>0:
        cgo_out = env.Cgo(cgofiles, *args, **kw)
        gofiles += filter(lambda x: x.name.endswith('.go'), cgo_out)

    objfiles = []
    obj = env.subst('_go_$GOOBJSUFFIX')
    # calculate a prefix for gccgo
    projprefix = os.path.split(fs.Dir('#').abspath)[-1] + '_'
    objfiles += env.Goc(srcdir.File(obj), gofiles, GOPREFIX=projprefix, *args, **kw)

    if len(cgofiles)>0:
        cflags = '-FVw -I"$GOROOT/src/pkg/runtime" ${_go_ifarch("amd64","-D_64BIT",__env__)}'
        cgo_defun = filter(lambda x: x.name=='_cgo_defun.c', cgo_out)
        cgo_obj = env.GoObject(cgo_defun, GOCFLAGS=cflags, *args, **kw)
        objfiles += cgo_obj
    else:
        cgo_obj = []

    pkg = srcdir.Dir('_obj').File(env.subst('${GOLIBPREFIX}'+srcdir.name+'${GOLIBSUFFIX}'))
    pkg = env.Gopack(pkg, objfiles, *args, **kw)

    local_pkg_dir = fs.Dir(env['GOPROJPKGPATH'])

    installed = []
    if len(cgofiles)>0:
        cgo2 = filter(lambda x: x.name.endswith('.cgo2.c'), cgo_out)
        cgolib = env.SharedLibrary(target=srcdir.File(env.subst('_cgo_$SHLIBSUFFIX')),
                                   source=cgo2,
                                   CFLAGS='${CGO_ARCH_CFLAGS} ${CGO_CFLAGS}',
                                   LINKFLAGS='${_cgo_arch("LINKFLAGS", GOARCH)} ${CGO_LINKFLAGS} -pthread -lm',
                                   *args, **kw)
        pkgparts = env.subst(basedir.rel_path(srcdir)).split(os.path.sep)
        cgolib_path = local_pkg_dir.File(env.subst('cgo_%s$SHLIBSUFFIX' % '_'.join(pkgparts)))
        installed_cgolib = env.InstallAs(cgolib_path, cgolib, *args, **kw)
        installed += installed_cgolib
    else:
        installed_cgolib = []

    pkgfile = os.path.join(basedir.rel_path(srcdir.dir), env.subst('${GOLIBPREFIX}'+srcdir.name +'${GOLIBSUFFIX}'))
    installed_pkg = env.InstallAs(local_pkg_dir.File(pkgfile), pkg[0], *args, **kw)
    installed += installed_pkg

    pkg = basedir.rel_path(srcdir)
    test = gotest(env, pkg, srcdir, gofiles, cgo_obj, installed_cgolib)
    if test:
        for t in test:
            alias = 'test_%s' % basedir.rel_path(srcdir).replace(os.sep, '_')
            a = env.Alias(alias, t, '${SOURCES.abspath}')
            env.AlwaysBuild(a)
            env.AlwaysBuild(env.Alias('test', a))
    else:
        env.AlwaysBuild(env.Alias('test'))

    return installed

def gopackages(env, basedir, *args, **kw):
    fs = SCons.Node.FS.get_default_fs()
    pkgdirs = []
    for root, dirs, files in os.walk(basedir):
        root = fs.Dir(root)
        # don't scan test data, as it might contain Go code
        if root.name=='testdata': continue
        ispkg = False
        for f in files:
            if not f.endswith(env['GOFILESUFFIX']): continue
            if f.endswith('_test.go'): continue
            if root.name==goutils.package_name(root.File(f), env):
                ispkg = True
                break
        if ispkg: pkgdirs.append(root.abspath)
    return map(lambda x: env.GoPackage(x, basedir, *args, **kw), pkgdirs)

def generate(env):
    env.AddMethod(gopackage, 'GoPackage')
    env.AddMethod(gopackages, 'GoPackages')

def exists(env):
    return 1
