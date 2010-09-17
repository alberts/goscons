import SCons.Builder
import SCons.Node.FS
import SCons.Util

GoLinkAction = SCons.Action.Action('$GOLINKCOM', '$GOLINKCOMSTR')

GoLinkBuilder = SCons.Builder.Builder(action=GoLinkAction,
                                      source_factory=SCons.Node.FS.File,
                                      src_suffix='$GOOBJSUFFIX')

def _go_rpath(lst, env, f=lambda x: x, target=None, source=None):
    if not lst: return lst
    l = f(SCons.PathList.PathList(lst).subst_path(env, target, source))
    if l is not None: lst = l
    return ':'.join([p.abspath for p in lst])

def generate(env):
    env['_go_rpath'] = _go_rpath
    env['BUILDERS']['Golink'] = GoLinkBuilder
    env['GORPATH'] = [env['GOPROJPKGPATH'], env['GOROOTPKGPATH']]
    env['GOLINKFLAGS'] = SCons.Util.CLVar('')
    env['GOLINKCOM'] = '$GOLINK $( ${_concat("-L ", GOPKGPATH, "", __env__)} $) -r ${_go_rpath(GORPATH,"")} $GOLINKFLAGS -o $TARGET $SOURCES'

def exists(env):
    return 1
