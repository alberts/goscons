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
        # latest cgo doesn't seem to make this file
        #srcdir.File('_cgo_.o')
        ]
    for s in source:
        base = SCons.Util.splitext(s.name)[0]
        tlist.append(s.dir.File(base + '.cgo1.go'))
        tlist.append(s.dir.File(base + '.cgo2.c'))
    return tlist, source

CgoAction = SCons.Action.Action('$CGOCOM', '$CGOCOMSTR')

# TODO scan the C code in the comments using a C scanner
CgoBuilder = SCons.Builder.Builder(action=CgoAction,
                                   emitter=emit,
                                   source_scanner=GoScanner,
                                   source_factory=SCons.Node.FS.File,
                                   src_suffix='$GOFILESUFFIX')

def _cgo_os(flags, os, f=lambda x: x, target=None, source=None):
    if os == 'linux':
        return '${CGO_LINUX_%s}' % flags
    elif os == 'darwin':
        return '${CGO_DARWIN_%s}' % flags
    elif os == 'windows':
        return '${CGO_WINDOWS_%s}' % flags
    else:
        raise SCons.Errors.InternalError, \
            'Unsupported GOOS: %s' % os

def _cgo_arch(flags, arch, f=lambda x: x, target=None, source=None):
    if arch == 'amd64':
        return '${CGO_AMD64_%s}' % flags
    elif arch == '386':
        return '${CGO_386_%s}' % flags
    else:
        raise SCons.Errors.InternalError, \
            'Unsupported GOARCH: %s' % arch

def generate(env):
    env['_cgo_os'] = _cgo_os
    env['_cgo_arch'] = _cgo_arch
    env['BUILDERS']['Cgo'] = CgoBuilder
    env['CGO'] = 'cgo'
    # tried chdir instead of this, but it breaks parallel builds
    CDCOM = 'cd '
    if platform.system() == 'Windows':
        CDCOM = 'cd /D '
    # TODO find a way to set the environment on Windows
    # TODO environment stuff before $CGO prevents SCons from making
    # making cgo output depend on the cgo binary
    # GOOS must be set so that cgo includes @rpath on darwin
    env['CGOCOM'] = CDCOM + '${TARGET.dir} && CGOPKGPATH=$CGOPKGPATH GOOS=$GOOS GOARCH=$GOARCH $CGO -- $CGO_CFLAGS ${SOURCES.file}'
    env['CGOPKGPATH'] = ''

    env['CGO_CFLAGS'] = '-O2'
    env['CGO_OS_CFLAGS'] = '${_cgo_os("CFLAGS", GOOS)}'
    env['CGO_AMD64_CFLAGS'] = '-m64'
    env['CGO_386_CFLAGS'] = '-m32'
    env['CGO_ARCH_CFLAGS'] = '${_cgo_arch("CFLAGS", GOARCH)}'
    env['CGO_OSARCH_CFLAGS'] = '${CGO_OS_CFLAGS} ${CGO_ARCH_CFLAGS}'

    env['CGO_LINKFLAGS'] = ''
    env['CGO_AMD64_LINKFLAGS'] = '-m64'
    env['CGO_386_LINKFLAGS'] = '-m32'
    env['CGO_OS_LINKFLAGS'] = '${_cgo_os("LINKFLAGS", GOOS)}'
    env['CGO_DARWIN_LINKFLAGS'] = '-Wl,-undefined,dynamic_lookup'
    env['CGO_ARCH_LINKFLAGS'] = '${_cgo_arch("LINKFLAGS", GOARCH)}'
    env['CGO_OSARCH_LINKFLAGS'] = '${CGO_OS_LINKFLAGS} ${CGO_ARCH_LINKFLAGS}'

    env['CGOPKGPATH'] = ''

def exists(env):
    return env.Detect('cgo')
