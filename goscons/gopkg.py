from subprocess import Popen, PIPE
from goutils import unique_files
import SCons.Node.FS
import glob
import goutils
import os.path

def gotest(env, pkg, srcdir, gofiles, cgo_obj, cgolib, *args, **kw):
    pkgname = pkg.replace(os.sep, '/')
    source = unique_files(srcdir.glob('*_test.go'))
    if len(source)==0: return
    obj = env.subst('_gotest_$GOOBJSUFFIX')
    objfiles = env.Goc(srcdir.File(obj), source + gofiles, *args, **kw)
    testpkgdir = srcdir.Dir('_test').Dir(pkg).dir
    testpkgfile = testpkgdir.File(env.subst('${GOLIBPREFIX}'+srcdir.name+'${GOLIBSUFFIX}'))
    testpkg = env.Gopack(testpkgfile, objfiles + cgo_obj, *args, **kw)
    gopkgpath = [srcdir.Dir('_test'), '$GOPKGPATH']
    testmain_obj = env.Goc(env.GoTestMain(source, GOPACKAGE=pkgname), GOPKGPATH=gopkgpath)
    bin = env.Golink(srcdir.File(env.subst('$GOTESTBIN')), testmain_obj, GOPKGPATH=gopkgpath)
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

    source = srcdir.glob('*.go')
    source = filter(lambda x: goutils.is_source(x, env), source)
    cgofiles = filter(lambda x: goutils.is_cgo_input(x, env), source)
    gofiles = list(set(source)-set(cgofiles))

    if len(cgofiles)>0:
        cgofiles = unique_files(cgofiles)
        pkgparts = env.subst(basedir.rel_path(srcdir)).split(os.path.sep)
        cgo_out = env.Cgo(cgofiles, CGOPKGPATH=os.sep.join(pkgparts[:-1]), *args, **kw)
        gofiles += filter(lambda x: x.name.endswith('.go'), cgo_out)

    gofiles = unique_files(gofiles)

    objfiles = []
    obj = env.subst('_go_$GOOBJSUFFIX')
    # calculate a prefix for gccgo
    projprefix = os.path.split(fs.Dir('#').abspath)[-1] + '_'
    if len(gofiles) > 0:
        objfiles += env.Goc(srcdir.File(obj), gofiles, GOPREFIX=projprefix, *args, **kw)

    if len(cgofiles)>0:
        cflags = '-FVw -I"$GOROOT/src/pkg/runtime" ${_go_ifarch("amd64","-D_64BIT",__env__)}'
        cgo_defun = filter(lambda x: x.name=='_cgo_defun.c', cgo_out)
        cgo_obj = env.GoObject(cgo_defun, GOCFLAGS=cflags, *args, **kw)
        objfiles += cgo_obj
    else:
        cgo_obj = []

    local_pkg_dir = fs.Dir(env['GOPROJPKGPATH'])
    goroot_pkg_dir = fs.Dir(env['GOROOTPKGPATH'])

    installed = []
    if len(cgofiles)>0:
        cgo2 = filter(lambda x: x.name.endswith('.cgo2.c'), cgo_out)
        cgolib = env.SharedLibrary(target=srcdir.File(env.subst('_cgo_$SHLIBSUFFIX')),
                                   source=cgo2,
                                   CFLAGS='${CGO_OSARCH_CFLAGS} ${CGO_CFLAGS}',
                                   LINKFLAGS='${CGO_OSARCH_LINKFLAGS} ${CGO_LINKFLAGS} -pthread -lm',
                                   *args, **kw)
        cgofile = env.subst('cgo_%s$SHLIBSUFFIX' % '_'.join(pkgparts))

        local_path = local_pkg_dir.File(cgofile)
        installed_cgolib = env.InstallAs(local_path, cgolib, *args, **kw)
        installed += installed_cgolib

        goroot_path = goroot_pkg_dir.File(cgofile)
        env.Alias('goinstall', env.InstallAs(goroot_path, cgolib, *args, **kw))
    else:
        installed_cgolib = []

    pkg_path = basedir.rel_path(srcdir)
    test = gotest(env, pkg_path, srcdir, gofiles, cgo_obj, installed_cgolib)
    if test:
        for t in test:
            pkgname_ = basedir.rel_path(srcdir).replace(os.sep, '_')
            alias = 'test_%s' % pkgname_
            a = env.Alias(alias, t, '${SOURCES.abspath} $GOTESTARGS')
            env.AlwaysBuild(a)
            env.AlwaysBuild(env.Alias('test', a))
            alias = 'bench_%s' % pkgname_
            a = env.Alias(alias, t, '${SOURCES.abspath} -benchmarks=. -match="Do not run tests" $GOTESTARGS')
            env.AlwaysBuild(a)
            env.AlwaysBuild(env.Alias('bench', a))

    if len(objfiles) == 0: return installed

    pkgfile = os.path.join(basedir.rel_path(srcdir.dir), env.subst('${GOLIBPREFIX}'+srcdir.name +'${GOLIBSUFFIX}'))
    local_path = local_pkg_dir.File(pkgfile)
    pkg = srcdir.Dir('_obj').File(env.subst('${GOLIBPREFIX}'+srcdir.name+'${GOLIBSUFFIX}'))
    pkg = env.Gopack(pkg, objfiles, *args, **kw)
    installed_pkg = env.InstallAs(local_path, pkg[0], *args, **kw)
    installed += installed_pkg

    goroot_path = goroot_pkg_dir.File(pkgfile)
    env.Alias('goinstall', env.InstallAs(goroot_path, pkg[0], *args, **kw))

    return installed

def gopackages(env, basedir, *args, **kw):
    fs = SCons.Node.FS.get_default_fs()
    pkgdirs = []
    for root, dirs, files in os.walk(basedir):
        root = fs.Dir(root)
        # don't scan test data, as it might contain Go code
        if root.name.lower()=='testdata': continue
        ispkg = False
        for f in files:
            if not f.endswith(env['GOFILESUFFIX']): continue
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
