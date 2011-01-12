from goutils import unique_files
import SCons.Scanner
import goutils
import os.path
import struct
import subprocess

def resolve_pkg(pkg, env, path, node):
    if pkg == 'C': return []
    if pkg == 'unsafe': return []
    pkgpath = env.FindGoPackage(pkg, path)
    if pkgpath is None:
        if goutils.scons_clean: return []
        # TODO workaround until we have a proper scanner
        if 'GCCGOPREFIX' in env: return []
        raise SCons.Errors.UserError, 'Package "%s" not found while scanning %s' % (pkg, node)
    return [pkgpath]

def goPkgScannerFunc(node, env, path, arg=None):
    if not node.exists(): return []
    fp = open(node.abspath)
    magic = fp.readline().strip()
    if magic != '!<arch>': return []
    start = False
    deps = []
    for line in open(node.abspath):
        line = line.strip()
        if line=='$$':
            if start: break
            start = True
        if not start: continue
        if line.startswith('import ') and line.find('"') >= 0:
            pkg = line.split('"')[-2]
            deps += resolve_pkg(pkg, env, path, node)
    return deps

def goScannerFunc(node, env, path, arg=None):
    try:
        return node.attributes.go_deps
    except AttributeError:
        pass
    if not node.exists(): return []
    if not 'GOLIBSUFFIX' in env:
        raise SCons.Errors.UserError, 'GOLIBSUFFIX undefined. Check your GOROOT and PATH.'
    if node.name.endswith(env.subst('$GOLIBSUFFIX')):
        deps = goPkgScannerFunc(node, env, path, arg)
    elif node.name.endswith(env.subst('$GOFILESUFFIX')):
        deps = []
        imports = goutils.imports(node, env)
        for pkg in imports:
            deps += resolve_pkg(pkg, env, path, node)
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
