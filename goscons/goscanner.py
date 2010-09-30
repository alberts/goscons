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
        raise SCons.Errors.UserError, 'File for package "%s" not found' % pkg
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
                #print node, line
                for importspec in line.split('..'):
                    importspec = importspec.split(' ')
                    if len(importspec)==3:
                        pkg = importspec[1]
                    elif len(importspec)==4:
                        pkg = importspec[2]
                    else:
                        continue
                    #print node, pkg
                    #deps += resolve_pkg(pkg, env, path)
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
    header = open(node.abspath).read(7)
    if header == '!<arch>':
        deps = goPkgScannerFunc(node, env, path, arg)
    else:
        deps = []
        imports = goutils.imports(node, env)
        for pkg in imports:
            deps += resolve_pkg(pkg, env, path)
    # Identify deps as Go packages so that the Golink scanner can add
    # them as dependencies too
    for dep in deps:
        dep.attributes.go_pkg = True
    deps = unique_files(deps)
    node.attributes.go_deps = deps
    return deps

GoScanner = SCons.Scanner.Base(goScannerFunc,
                               name='GoScanner',
                               node_class=SCons.Node.FS.File,
                               node_factory=SCons.Node.FS.File,
                               path_function=SCons.Scanner.FindPathDirs('GOPKGPATH'),
                               recursive=1)
