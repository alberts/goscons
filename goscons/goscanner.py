from goutils import unique_files
import SCons.Scanner
import goutils
import os.path
import struct
import subprocess

# TODO can make this better with FindFile
def resolve_pkg(pkg, env, path):
    if pkg == 'C': return []
    if pkg == 'unsafe': return []
    pkgpath = env.FindGoPackage(pkg, path)
    if pkgpath is None:
        raise SCons.Errors.UserError, 'Package "%s" not found' % pkg
    return [pkgpath]

def goPkgScannerFunc(node, env, path, arg=None):
    if not node.exists(): return []
    deps = []
    # TODO use gopack p filename __.PKGDEF
    for line in open(node.abspath):
        line = line.strip()
        if line.startswith('import '):
            if line.find('"') >= 0:
                pkg = line.split('"')[-2]
                deps += resolve_pkg(pkg, env, path)
            elif line.endswith(';'):
                for importspec in line.split('..'):
                    importspec = importspec.split(' ')
                    if len(importspec)==3:
                        pkg = importspec[1]
                    elif len(importspec)==4:
                        pkg = importspec[2]
                    else:
                        continue
                break
            else:
                raise SCons.Errors.InternalError, \
                    'Unsupported import spec: "%s"' % line
    return deps

def goScannerFunc(node, env, path, arg=None):
    try:
        return node.attributes.go_deps
    except AttributeError:
        pass
    if not node.exists(): return []
    if node.name.endswith(env.subst('$GOLIBSUFFIX')):
        deps = goPkgScannerFunc(node, env, path, arg)
    elif node.name.endswith(env.subst('$GOFILESUFFIX')):
        deps = []
        imports = goutils.imports(node, env)
        for pkg in imports:
            deps += resolve_pkg(pkg, env, path)
    else:
        deps = []
    for c in node.all_children():
        deps += goScannerFunc(c, env, path, arg)
    deps = unique_files(deps)
    node.attributes.go_deps = deps
    return deps

GoScanner = SCons.Scanner.Base(goScannerFunc,
                               name='GoScanner',
                               node_class=SCons.Node.FS.File,
                               node_factory=SCons.Node.FS.File,
                               path_function=SCons.Scanner.FindPathDirs('GOPKGPATH'),
                               recursive=1)
