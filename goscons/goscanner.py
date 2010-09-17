import SCons.Scanner
import goutils
import os.path
import struct
import subprocess

# TODO can make this better with FindFile
def resolve_pkg(pkg, env, path):
    if pkg == 'C': return []
    if pkg == 'unsafe': return []
    pkgfile = env.subst(os.path.join(*pkg.split('/'))+'$GOLIBSUFFIX')
    fs = SCons.Node.FS.get_default_fs()
    local_pkg_dir = fs.Dir(env['GOPROJPKGPATH'])
    for local_pkg in env['GOPACKAGES']:
        local_pkg_name = os.path.splitext(local_pkg_dir.rel_path(local_pkg))[0]
        if pkg==local_pkg_name:
            return [local_pkg]
    for p in path:
        fullpkgfile = p.File(pkgfile)
        if fullpkgfile.exists():
            return [fullpkgfile]
    # TODO import not found. raise a scons error here?
    return []

# TODO use gopack p filename __.PKGDEF
def goPkgScannerFunc(node, env, path, arg=None):
    if not node.exists(): return []
    deps = []
    for line in open(node.abspath):
        line = line.strip()
        if line.startswith('import '):
            pkg = line.split('"')[-2]
            deps += resolve_pkg(pkg, env, path)
    return deps

def goScannerFunc(node, env, path, arg=None):
    try:
        return node.attributes.go_deps
    except AttributeError:
        pass
    if not node.exists(): return []
    header = open(node.abspath).read(7)
    if header == '!<arch>':
        deps = goPkgScannerFunc(node, env, path, arg)
    else:
        deps = []
        for pkg in goutils.imports(node, env):
            deps += resolve_pkg(pkg, env, path)
    # Identify deps as Go packages so that the Golink scanner can add
    # them as dependencies too
    for dep in deps:
        dep.attributes.go_pkg = True
    node.attributes.go_deps = deps
    return deps

GoScanner = SCons.Scanner.Base(goScannerFunc,
                               name='GoScanner',
                               node_class=SCons.Node.FS.File,
                               node_factory=SCons.Node.FS.File,
                               path_function=SCons.Scanner.FindPathDirs('GOPKGPATH'),
                               recursive=1)
