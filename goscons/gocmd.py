from goutils import unique_files
import SCons.Node.FS
import goutils
import os.path

def is_source(source):
    test = source.name.endswith('_test.go')
    return not test

# TODO need to propogate args, kw into env
def gocommand(env, srcdir, *args, **kw):
    fs = SCons.Node.FS.get_default_fs()
    srcdir = fs.Dir(srcdir)
    source = srcdir.glob('*.go')
    gofiles = unique_files(filter(is_source, source))
    obj = env.subst('_go_$GOOBJSUFFIX')
    objfiles = env.Goc(srcdir.File(obj), gofiles, *args, **kw)
    name = '%s%s%s' % (env.subst('$GOCMDPREFIX'), srcdir.name, env.subst('$GOCMDSUFFIX'))
    bin = env.Golink(srcdir.File(name), objfiles)
    local_bin_dir = fs.Dir(env['GOPROJBINPATH'])
    return env.InstallAs(local_bin_dir.File(name), bin[0], *args, **kw)

def gocommands(env, srcdir, *args, **kw):
    fs = SCons.Node.FS.get_default_fs()
    cmddirs = []
    for root, dirs, files in os.walk(srcdir):
        root = fs.Dir(root)
        iscmd = False
        for f in files:
            if not f.endswith('.go'): continue
            if goutils.package_name(root.File(f), env)=='main':
                iscmd = True
                break
        if iscmd: cmddirs.append(root.abspath)
    return map(lambda x: env.GoCommand(x, *args, **kw), cmddirs)

def generate(env):
    env.AddMethod(gocommand, 'GoCommand')
    env.AddMethod(gocommands, 'GoCommands')
    env['GOCMDPREFIX'] = '$PROGPREFIX'
    env['GOCMDSUFFIX'] = '$PROGSUFFIX'

def exists(env):
    return 1
