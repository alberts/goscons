from subprocess import Popen, PIPE
import SCons.Node.FS
import glob
import goutils
import os.path

def is_source(source):
    cgo_generated = source.name=='_cgo_gotypes.go' or source.name.endswith('.cgo1.go')
    test = source.name.endswith('_test.go')
    return not cgo_generated and not test

def gopackage(env, srcdir, *args, **kw):
    source = sorted(env.Glob(os.path.join(srcdir, '*.go')))
    fs = SCons.Node.FS.get_default_fs()
    srcdir = fs.Dir(srcdir)

    source = filter(is_source, source)
    cgofiles = filter(lambda x: goutils.is_cgo_input(x, env), source)
    gofiles = sorted(list(set(source)-set(cgofiles)))

    if len(cgofiles)>0:
        cgo_out = env.Cgo(cgofiles, *args, **kw)
        gofiles += filter(lambda x: x.name.endswith('.go'), cgo_out)

    objfiles = []
    obj = env.subst('_go_$GOOBJSUFFIX')
    objfiles += env.Goc(srcdir.File(obj), gofiles, *args, **kw)

    if len(cgofiles)>0:
        cgo_defun = filter(lambda x: x.name=='_cgo_defun.c', cgo_out)
        objfiles += env.P9Object(cgo_defun,
                                 P9CFLAGS='-FVw -I"$GOROOT/src/pkg/runtime" -D_64BIT',
                                 *args, **kw)

    pkg = srcdir.Dir('_obj').File(env.subst(srcdir.name+'$GOLIBSUFFIX'))
    pkg = env.Gopack(pkg, objfiles, *args, **kw)

    local_pkg_dir = fs.Dir(env['GOPROJPKGPATH'])

    installed = []
    if len(cgofiles)>0:
        cgo2 = filter(lambda x: x.name.endswith('.cgo2.c'), cgo_out)
        cgolib = env.SharedLibrary(target=srcdir.File(env.subst('_cgo_$SHLIBSUFFIX')),
                                   source=cgo2,
                                   CFLAGS='-m64 -fPIC -O2 $CGO_CFLAGS',
                                   LINKFLAGS='$CGO_LDFLAGS -lpthread -lm',
                                   *args, **kw)
        pkgparts = env.subst(fs.Dir('#src/pkg').rel_path(srcdir)).split(os.path.sep)
        installed_cgolib = local_pkg_dir.File(env.subst('cgo_%s$SHLIBSUFFIX' % '_'.join(pkgparts)))
        installed += env.InstallAs(installed_cgolib, cgolib, *args, **kw)

    pkgfile = env.subst(fs.Dir('#src/pkg').rel_path(srcdir)+'$GOLIBSUFFIX')
    installed_pkg = env.InstallAs(local_pkg_dir.File(pkgfile), pkg[0], *args, **kw)
    env.Append(GOPACKAGES=installed_pkg)
    installed += installed_pkg
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
    env.AddMethod(gopackage, 'GoPackage')
    env.AddMethod(gopackages, 'GoPackages')
    env['GOPACKAGES'] = []

def exists(env):
    return 1
