from subprocess import Popen, PIPE
from goutils import unique_files
import SCons.Node.FS
import glob
import goutils
import os.path

def gotest(env, pkg, srcdir, gofiles, cgo_obj, *args, **kw):
    pkgname = pkg.replace(os.sep, '/')
    source = unique_files(srcdir.glob('*_test.go'))
    if len(source)==0: return []
    obj = env.subst('_gotest_$GOOBJSUFFIX')
    objfiles = env.Goc(srcdir.File(obj), source + gofiles, *args, **kw)
    testpkgdir = srcdir.Dir('_test').Dir(pkg).dir
    testpkgfile = testpkgdir.File(env.subst('${GOLIBPREFIX}'+srcdir.name+'${GOLIBSUFFIX}'))
    testpkg = env.Gopack(testpkgfile, objfiles + cgo_obj, *args, **kw)
    gopkgpath = [srcdir.Dir('_test'), '$GOPKGPATH']
    testmain_obj = env.Goc(env.GoTestMain(source, GOPACKAGE=pkgname), GOPKGPATH=gopkgpath)
    bin = env.Golink(srcdir.File(env.subst('$GOTESTBIN')), testmain_obj, GOPKGPATH=gopkgpath)
    return bin

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

    pkg_path = basedir.rel_path(srcdir)
    pkgname_ = pkg_path.replace(os.sep, '_')

    gofiles = unique_files(gofiles)
    objfiles = []
    obj = env.subst('_go_$GOOBJSUFFIX')
    if len(gofiles) > 0:
        projprefix = os.path.split(fs.Dir('#').abspath)[-1]
        fgoprefix = '-fgo-prefix=' + projprefix + '_' + pkgname_
        objfiles += env.Goc(srcdir.File(obj), gofiles, FGOPREFIX=fgoprefix, *args, **kw)

    if len(cgofiles)>0:
        cflags = '-FVw -I"$GOROOT/src/pkg/runtime"'
        cgo_defun = filter(lambda x: x.name=='_cgo_defun.c', cgo_out)
        cgo_defun_obj = env.GoObject(cgo_defun, GOCFLAGS=cflags, *args, **kw)
        cgo2 = filter(lambda x: x.name.endswith('.cgo2.c'), cgo_out)
        cgo_shobj = env.SharedObject(cgo2, CFLAGS='${CGO_OSARCH_CFLAGS} ${CGO_CFLAGS}', *args, **kw)
        cgo_lib = env.SharedLibrary(target=srcdir.File(env.subst('_cgo1_$SHLIBSUFFIX')),
                                    source=cgo_shobj,
                                    LINKFLAGS='${CGO_OSARCH_LINKFLAGS} ${CGO_LINKFLAGS} -pthread -lm',
                                    *args, **kw)
        cgo_import = env.Command(srcdir.File('_cgo_import.c'), cgo_lib, '$CGO -dynimport $SOURCES > $TARGET')
        cgo_import_obj = env.GoObject(cgo_import, GOCFLAGS='-FVw', *args, **kw)
        cgo_obj = cgo_defun_obj + cgo_import_obj + cgo_shobj
        objfiles += cgo_obj
    else:
        cgo_obj = []

    cobjfiles = []
    if len(cgo_obj)>0:
        # compile any native code into object files
        cfiles = []
        for ext in 'c','cc','cpp':
            cfiles += srcdir.glob('*.' + ext)
        cfiles = set(cfiles)
        cgo_output = set(srcdir.glob('_cgo_*') + srcdir.glob('*.cgo*'))
        cfiles -= cgo_output
        for cfile in cfiles:
            cobjfiles += env.Object(cfile, *args, **kw)
    objfiles += cobjfiles

    test = gotest(env, pkg_path, srcdir, gofiles, cgo_obj + cobjfiles)
    if env['GODEP_BUILD']: test = []
    for t in test:
        alias = 'test_%s' % pkgname_
        a = env.Alias(alias, t, '$GOTESTRUNNER ${SOURCES.abspath} $GOTESTARGS')
        env.AlwaysBuild(a)
        env.AlwaysBuild(env.Alias('test', a))
        alias = 'bench_%s' % pkgname_
        a = env.Alias(alias, t, '$GOTESTRUNNER ${SOURCES.abspath} -benchmarks=. -match="Do not run tests" $GOTESTARGS')
        env.AlwaysBuild(a)
        env.AlwaysBuild(env.Alias('bench', a))

    if len(objfiles) == 0: return []

    local_pkg_dir = fs.Dir(env['GOPROJPKGPATH'])
    goroot_pkg_dir = fs.Dir(env['GOROOTPKGPATH'])
    pkgfile = os.path.join(basedir.rel_path(srcdir.dir), env.subst('${GOLIBPREFIX}'+srcdir.name +'${GOLIBSUFFIX}'))
    local_path = local_pkg_dir.File(pkgfile)
    pkg = srcdir.Dir('_obj').File(env.subst('${GOLIBPREFIX}'+srcdir.name+'${GOLIBSUFFIX}'))
    pkg = env.Gopack(pkg, objfiles, *args, **kw)
    installed_pkg = env.InstallAs(local_path, pkg[0], *args, **kw)
    goroot_path = goroot_pkg_dir.File(pkgfile)
    env.Alias('goinstall', env.InstallAs(goroot_path, pkg[0], *args, **kw))
    return installed_pkg

def gopackages(env, topdir, basedir=None, *args, **kw):
    if not basedir: basedir = topdir
    fs = SCons.Node.FS.get_default_fs()
    pkgdirs = []
    for root, dirs, files in os.walk(topdir, True):
        alldirs = set(dirs)
        skipdirs = set()
        for d in dirs:
            if d=='_obj': skipdirs.add(d)
            elif d=='_test': skipdirs.add(d)
            elif d.lower()=='testdata': skipdirs.add(d)
        dirs[:] = list(alldirs-skipdirs)
        root = fs.Dir(root)
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
