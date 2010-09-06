import SCons.Errors
import SCons.Tool
import os
import platform

def generate(env):
    if 'GOROOT' not in os.environ:
        raise SCons.Errors.UserError, 'Set GOROOT in your environment'
    env['GOROOT'] = os.environ['GOROOT']

    if platform.system() == 'Linux':
        env['GOOS'] = 'linux'
    else:
        raise SCons.Errors.InternalError, \
            'Unsupported platform: %s' % platform.system()

    if platform.machine() == 'x86_64':
        env['GOARCH'] = 'amd64'
    elif platform.machine() == 'i386':
        env['GOARCH'] = '386'
    else:
        raise SCons.Errors.InternalError, \
            'Unsupported arch: %s' % platform.machine()

    env['GOROOTPKGPATH'] = env.Dir('$GOROOT/pkg/${GOOS}_$GOARCH')
    env['GOPROJPKGPATH'] = env.Dir('#pkg/${GOOS}_$GOARCH')
    env['GOPKGPATH'] = [env['GOPROJPKGPATH'], env['GOROOTPKGPATH']]

    env['GOFILESUFFIX'] = '.go'
    tools = [
        'gopkg',
        'gocmd',
        'cgo',
        'goc',
        'golink',
        'plan9c',
        'gopack'
        ]
    for t in SCons.Tool.FindAllTools(tools,env):
        SCons.Tool.Tool(t)(env)

def exists(env):
    return 1
