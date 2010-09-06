import SCons.Node.FS
import goutils
import os.path

def is_source(source):
    test = source.name.endswith('_test.go')
    return not test

def gocommand(env, srcdir, *args, **kw):
    source = sorted(env.Glob(os.path.join(srcdir, '*.go')))
    fs = SCons.Node.FS.get_default_fs()
    srcdir = fs.Dir(srcdir)
    gofiles = filter(is_source, source)
    obj = env.subst('_go_$GOOBJSUFFIX')
    objfiles = env.Goc(srcdir.File(obj), gofiles, *args, **kw)
    return env.Golink(srcdir.File(srcdir.name), objfiles)

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

def exists(env):
    return 1
