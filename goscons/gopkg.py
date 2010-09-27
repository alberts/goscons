from subprocess import Popen, PIPE
import SCons.Node.FS
import glob
import goutils
import os.path

def is_source(source):
    if source.name=='_cgo_gotypes.go': return False
    if source.name.endswith('.cgo1.go'): return False
    if source.name.endswith('_test.go'): return False
    if source.name=='_testmain.go': return False
    return True

def gotest(env, srcdir, gofiles, cgo_obj, cgolib, *args, **kw):
    source = sorted(srcdir.glob('*_test.go'))
    if len(source)==0: return
    obj = env.subst('_gotest_$GOOBJSUFFIX')
    objfiles = env.Goc(srcdir.File(obj), source + gofiles, *args, **kw)
    testpkg = srcdir.Dir('_test').File(env.subst('${GOLIBPREFIX}'+srcdir.name+'${GOLIBSUFFIX}'))
    testpkg = env.Gopack(testpkg, objfiles + cgo_obj, *args, **kw)
    gopkgpath = [srcdir.Dir('_test'), '$GOPKGPATH']
    testmain_obj = env.Goc(env.GoTestMain(source), GOPKGPATH=gopkgpath)
    bin = env.Golink(srcdir.File(env.subst('$GOTESTBIN')), testmain_obj, GOPKGPATH=gopkgpath)
    # explicitly depend on the package's cgo lib, if any
    env.Depends(bin, cgolib)
    return bin

# TODO need to propogate args, kw into env
def gopackage(env, srcdir, *args, **kw):
    fs = SCons.Node.FS.get_default_fs()
    srcdir = fs.Dir(srcdir)
    source = sorted(srcdir.glob('*.go'))

    source = filter(is_source, source)
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
        cgo_defun = filter(lambda x: x.name=='_cgo_defun.c', cgo_out)
        cgo_obj = env.P9Object(cgo_defun,
                               P9CFLAGS='-FVw -I"$GOROOT/src/pkg/runtime" -D_64BIT',
                               *args, **kw)
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
        pkgparts = env.subst(fs.Dir('#src/pkg').rel_path(srcdir)).split(os.path.sep)
        cgolib_path = local_pkg_dir.File(env.subst('cgo_%s$SHLIBSUFFIX' % '_'.join(pkgparts)))
        installed_cgolib = env.InstallAs(cgolib_path, cgolib, *args, **kw)
        installed += installed_cgolib
    else:
        installed_cgolib = []

    pkgfile = os.path.join(fs.Dir('#src/pkg').rel_path(srcdir.dir), env.subst('${GOLIBPREFIX}'+srcdir.name +'${GOLIBSUFFIX}'))
    installed_pkg = env.InstallAs(local_pkg_dir.File(pkgfile), pkg[0], *args, **kw)
    installed += installed_pkg

    test = gotest(env, srcdir, gofiles, cgo_obj, installed_cgolib)
    if test:
        test_aliases = []
        for t in test:
            i = env['_GOTEST_COUNT']
            env['_GOTEST_COUNT'] += 1
            a = env.Alias('test-%d' % i, t, '${SOURCES.abspath}')
            env.AlwaysBuild(a)
            test_aliases += a
        env.AlwaysBuild(env.Alias('test', test_aliases))
    else:
        env.AlwaysBuild(env.Alias('test'))

    return installed

def gopackages(env, srcdir, *args, **kw):
    fs = SCons.Node.FS.get_default_fs()
    pkgdirs = []
    for root, dirs, files in os.walk(srcdir):
        root = fs.Dir(root)
        ispkg = False
        for f in files:
            if not f.endswith('.go'): continue
            if f.endswith('_test.go'): continue
            if root.name==goutils.package_name(root.File(f), env):
                ispkg = True
                break
        if ispkg: pkgdirs.append(root.abspath)
    return map(lambda x: env.GoPackage(x, *args, **kw), pkgdirs)

def generate(env):
    env['_GOTEST_COUNT'] = 0
    env.AddMethod(gopackage, 'GoPackage')
    env.AddMethod(gopackages, 'GoPackages')

def exists(env):
    return 1
