from goscanner import GoScanner
import SCons.Builder
import SCons.Node.FS
import SCons.Util
import platform

def emit(target, source, env):
    if len(source)==0:
        return target, source
    srcdir = source[0].dir
    tlist = [
        srcdir.File('_cgo_defun.c'),
        srcdir.File('_cgo_gotypes.go'),
        srcdir.File('_cgo_.o')
        ]
    for s in source:
        base = SCons.Util.splitext(s.name)[0]
        tlist.append(s.dir.File(base + '.cgo1.go'))
        tlist.append(s.dir.File(base + '.cgo2.c'))
    return tlist, source

CgoAction = SCons.Action.Action('$CGOCOM', '$CGOCOMSTR')

CgoBuilder = SCons.Builder.Builder(action=CgoAction,
                                   emitter=emit,
                                   source_scanner=GoScanner,
                                   source_factory=SCons.Node.FS.File,
                                   src_suffix='$GOFILESUFFIX')

def generate(env):
    env['BUILDERS']['Cgo'] = CgoBuilder
    env['CGO'] = 'cgo'
    # tried chdir instead of this, but it breaks parallel builds
    CDCOM = 'cd '
    if platform.system() == 'Windows':
        CDCOM = 'cd /D '
    # TODO find a way to set the environment on Windows
    env['CGOCOM'] = CDCOM + '${TARGET.dir} && CGOPKGPATH=$CGOPKGPATH GOARCH=$GOARCH $CGO -- $CGO_CFLAGS ${SOURCES.file}'
    env['CGOPKGPATH'] = ''
    env['CGO_CFLAGS'] = ''
    env['CGO_LDFLAGS'] = ''
    env['CGOPKGPATH'] = ''

def exists(env):
    return env.Detect('cgo')
