import SCons.Errors
import SCons.Tool
import os
import platform

def godep(env, d, *args, **kw):
    if 'HUDSON' in env['ENV']:
        lastBuild = env['ENV']['HUDSON']
        env.Append(GOPKGPATH=env.Dir(os.path.join('#..','..',d,lastBuild,'archive','pkg','${GOOS}_$GOARCH')))
    else:
        env.Append(GOPKGPATH=env.Dir(os.path.join('#..',d,'pkg','${GOOS}_$GOARCH')))

def generate(env):
    if 'GOROOT' not in env:
        if 'GOROOT' not in os.environ:
            raise SCons.Errors.UserError, 'Set GOROOT in your environment'
        env['GOROOT'] = os.environ['GOROOT']

    if 'GOOS' not in env:
        if platform.system() == 'Linux':
            env['GOOS'] = 'linux'
        elif platform.system() == 'Darwin':
            env['GOOS'] = 'darwin'
        else:
            raise SCons.Errors.InternalError, \
                'Unsupported platform: %s' % platform.system()

    if 'GOARCH' not in env:
        if 'GOARCH' in os.environ:
            env['GOARCH'] = os.environ['GOARCH']
        else:
            if platform.machine() == 'x86_64':
                env['GOARCH'] = 'amd64'
            elif platform.machine() == 'i386':
                # TODO not a good guess on darwin
                env['GOARCH'] = '386'
            else:
                raise SCons.Errors.InternalError, \
                    'Unsupported arch: %s' % platform.machine()

    env['GOPROJBINPATH'] = env.Dir('#bin/${GOOS}_$GOARCH')
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

    if env['GOARCH'] == 'amd64':
        tools += ['goc6','golink6','plan9c6']
    elif env['GOARCH'] == '386':
        tools += ['goc8','golink8','plan9c8']
    else:
        raise SCons.Errors.InternalError, \
            'Unsupported GOARCH: %s' % env['GOARCH']

    for t in SCons.Tool.FindAllTools(tools,env):
        SCons.Tool.Tool(t)(env)

    env.AddMethod(godep, 'GoDep')

def exists(env):
    return 1
