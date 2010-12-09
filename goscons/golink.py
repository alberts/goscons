from goscanner import GoScanner
import SCons.Builder
import SCons.Node.FS
import SCons.Scanner
import SCons.Util

GoLinkAction = SCons.Action.Action('$GOLINKCOM', '$GOLINKCOMSTR')

GoLinkBuilder = SCons.Builder.Builder(action=GoLinkAction,
                                      source_factory=SCons.Node.FS.File,
                                      source_scanner=GoScanner,
                                      prefix='$PROGPREFIX',
                                      suffix='$PROGSUFFIX',
                                      src_suffix='$GOOBJSUFFIX')

def _go_rpath(lst, env, f=lambda x: x, target=None, source=None):
    if not lst: return lst
    l = f(SCons.PathList.PathList(lst).subst_path(env, target, source))
    if l is not None: lst = l
    if len(lst)==0: return ''
    return '-r ' + ':'.join([env.Dir(p).abspath for p in lst])

def generate(env):
    env['_go_rpath'] = _go_rpath
    env['BUILDERS']['Golink'] = GoLinkBuilder
    env['GORPATH'] = []
    env['GOLINKFLAGS'] = SCons.Util.CLVar('')
    env['GOLINKCOM'] = '$GOLINK $( ${_concat("-L ", GOPKGPATH, "", __env__)} $) ${_go_rpath(GORPATH, __env__)} $GOLINKFLAGS -o $TARGET $SOURCES'

def exists(env):
    return 1
