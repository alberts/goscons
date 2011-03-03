from subprocess import Popen, PIPE
import SCons.Errors
import SCons.SConf
import os.path

# TODO might not work with older versions of SCons
# use SCons.Script.Main.options.clean then
scons_clean = SCons.SConf.build_type=='clean'

cmp_abspath = lambda x, y: cmp(x.abspath, y.abspath)

def unique_files(files):
    return sorted(list(set(files)), cmp=cmp_abspath)

def createObjBuilders(env):
    try:
        goobj = env['BUILDERS']['GoObject']
    except KeyError:
        goobj = SCons.Builder.Builder(action={},
                                      emitter={},
                                      prefix='$GOOBJPREFIX',
                                      suffix='$GOOBJSUFFIX',
                                      src_builder=['CFile'],
                                      source_scanner=SourceFileScanner)
        env['BUILDERS']['GoObject'] = static_obj
    return static_obj

def helper_impl(source, env):
    if env['GOSCONSHELPER'] is None or not source.exists() or source.getsize()==0:
        return False, '', [], [], []
    cgo = False
    go_package = ''
    go_imports = set()
    go_tests = []
    go_benchmarks = []
    if 'GOBIN' in env['ENV']:
        helper = os.path.join(env['ENV']['GOBIN'], env.subst('${GOSCONSHELPER}${PROGSUFFIX}'))
    else:
        helper = env.subst(os.path.join('$GOROOT', 'bin', '${GOSCONSHELPER}${PROGSUFFIX}'))
    if not os.path.isfile(helper):
        raise SCons.Errors.UserError, '%s is missing' % helper
    if source.path.endswith('_test.go'):
        mode = 'package_imports_tests'
    else:
        mode = 'package_imports'
    p = Popen([helper, '-mode=%s' % mode, source.abspath], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        if scons_clean: return False, '', [], [], []
        raise SCons.Errors.UserError, err.strip()
    lines = out.strip().split('\n')
    line = lines.pop(0)
    go_package = line.split(' ',1)[1]
    for line in lines:
        parts = line.split(' ',1)
        if len(parts)>1:
            go_imports.add(parts[1])
        else:
            funcname = line.split('.')[-1]
            if funcname.startswith('Test'):
                go_tests.append(line)
            elif funcname.startswith('Bench'):
                go_benchmarks.append(line)
    go_imports -= set(['unsafe'])
    cgo = 'C' in go_imports
    return cgo, go_package, go_imports, go_tests, go_benchmarks

def helper(source, env):
    attrs = helper_impl(source, env)
    source.attributes.cgo, \
        source.attributes.go_package, \
        source.attributes.go_imports, \
        source.attributes.go_tests, \
        source.attributes.go_benchmarks = attrs

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

GOARCH = set(['386','amd64','arm'])
GOOS = set(['bsd','unix','linux','windows','darwin','nacl','freebsd'])
GOOS_BSD = set(['freebsd','darwin'])
GOOS_UNIX = set(['freebsd','darwin','linux','nacl'])

def goos_goarch():
    for goos in GOOS:
        for goarch in GOARCH:
            yield goos, goarch

GOOS_GOARCH = set([x for x in goos_goarch()])

def is_os_arch_source(source):
    parts = source.name.split('_')
    if len(parts)<2: return False
    os_arch = parts[-2], parts[-1].split('.',1)[0]
    if os_arch in GOOS_GOARCH:
        return os_arch
    return None

def is_arch_source(source):
    if not source.name.find('_')>=0:
        return False
    arch = source.name.split('_')[-1].split('.',1)[0]
    if arch in GOARCH:
        return arch
    return None

def is_os_source(source):
    if not source.name.find('_')>=0:
        return False
    os = source.name.split('_')[-1].split('.',1)[0]
    if os in GOOS:
        return os
    return None

def is_source(source, env):
    if source.name.endswith('_test.go'): return False
    if source.name=='_testmain.go': return False
    arch = is_arch_source(source)
    if arch:
        os_arch = is_os_arch_source(source)
        if os_arch:
            os = os_arch[0]
            if os=='bsd' and env['GOOS'] in GOOS_BSD:
                return True
            elif os=='unix' and env['GOOS'] in GOOS_UNIX:
                return True
            return os_arch==(env['GOOS'], env['GOARCH'])
        return arch==env['GOARCH']
    os = is_os_source(source)
    if os:
        if os=='bsd' and env['GOOS'] in GOOS_BSD:
            return True
        elif os=='unix' and env['GOOS'] in GOOS_UNIX:
            return True
        return os==env['GOOS']
    return True
