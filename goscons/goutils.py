from subprocess import Popen, PIPE
import SCons.Errors
import os.path

def helper(source, env):
    helper = env.subst(os.path.join('$GOROOT', 'bin', 'scons-go-helper'))
    if not os.path.isfile(helper):
        raise SCons.Errors.UserError, '$GOROOT/bin/scons-go-helper is missing'
    p = Popen([helper, '-mode=both', source.abspath], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise SCons.Errors.UserError, err.strip()
    source.attributes.cgo = False
    source.attributes.go_imports = []
    for line in out.split('\n'):
        line = line.strip()
        if line.startswith('package '):
            source.attributes.go_package = line.split(' ',1)[1]
        elif line.startswith('import '):
            pkg = line.split(' ',1)[1]
            if pkg == 'C':
                source.attributes.cgo = True
            else:
                if pkg == 'unsafe': continue
                source.attributes.go_imports.append(pkg)

def is_cgo_input(source, env):
    try:
        return source.attributes.cgo
    except AttributeError:
        helper(source, env)
    return source.attributes.cgo

def imports(source, env):
    try:
        return source.attributes.go_imports
    except AttributeError:
        helper(source, env)
    return source.attributes.go_imports

def package_name(source, env):
    try:
        return source.attributes.go_package
    except AttributeError:
        helper(source, env)
    return source.attributes.go_package
