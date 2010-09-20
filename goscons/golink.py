import SCons.Builder
import SCons.Node.FS
import SCons.Scanner
import SCons.Util

# Make executable directly dependant on its packages so that it gets
# relinked when they change
def scanner_function(node, env, path):
    f = lambda x: hasattr(x.attributes,'go_pkg')
    deps = filter(f, node.all_children())
    return deps

GoLinkAction = SCons.Action.Action('$GOLINKCOM', '$GOLINKCOMSTR')

GoObjectScanner = SCons.Scanner.Scanner(scanner_function)

GoLinkBuilder = SCons.Builder.Builder(action=GoLinkAction,
                                      source_factory=SCons.Node.FS.File,
                                      source_scanner=GoObjectScanner,
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
    # TODO get rid of weird "" argument to _go_rpath
    env['GOLINKCOM'] = '$GOLINK $( ${_concat("-L ", GOPKGPATH, "", __env__)} $) -r ${_go_rpath(GORPATH,"")} $GOLINKFLAGS -o $TARGET $SOURCES'

def exists(env):
    return 1
