from subprocess import Popen, PIPE
import SCons.Errors
import os.path

def helper(source, env):
    source.attributes.cgo = False
    source.attributes.go_package = ''
    source.attributes.go_imports = []
    source.attributes.go_tests = []
    source.attributes.go_benchmarks = []
    # if no helper is defined, don't continue
    if env['GOSCONSHELPER'] is None: return
    helper = env.subst(os.path.join('$GOROOT', 'bin', '$GOSCONSHELPER'))
    if not os.path.isfile(helper):
        raise SCons.Errors.UserError, '%s is missing' % helper
    if source.path.endswith('_test.go'):
        mode = 'package_imports_tests'
    else:
        mode = 'package_imports'
    p = Popen([helper, '-mode=%s' % mode, source.abspath], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise SCons.Errors.UserError, err.strip()
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
        else:
            if line.split('.')[-1].startswith('Test'):
                source.attributes.go_tests.append(line)
            elif line.split('.')[-1].startswith('Test'):
                source.attributes.go_benchmarks.append(line)

def is_cgo_input(source, env):
    try:
        return source.attributes.cgo
    except AttributeError:
        helper(source, env)
    return source.attributes.cgo

def package_name(source, env):
    try:
        return source.attributes.go_package
    except AttributeError:
        helper(source, env)
    return source.attributes.go_package

def imports(source, env):
    try:
        return source.attributes.go_imports
    except AttributeError:
        helper(source, env)
    return source.attributes.go_imports

def tests(source, env):
    try:
        return source.attributes.go_tests
    except AttributeError:
        helper(source, env)
    return source.attributes.go_tests

def benchmarks(source, env):
    try:
        return source.attributes.go_benchmarks
    except AttributeError:
        helper(source, env)
    return source.attributes.go_benchmarks
