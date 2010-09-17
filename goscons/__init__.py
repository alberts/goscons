from SCons.Script import Environment
import SCons.Tool
import os

module_dir = os.path.abspath(os.path.dirname(__file__))
SCons.Tool.DefaultToolpath.append(module_dir)

def GoEnvironment(*args, **kwargs):
    # set kwargs to keep Python 2.4 happy
    kwargs.setdefault('ENV', os.environ)
    kwargs.setdefault('tools', ['golang','default'])
    return Environment(*args, **kwargs)

def GoEnvironment6(*args, **kwargs):
    kwargs.setdefault('GOARCH', 'amd64')
    return GoEnvironment(*args, **kwargs)

def GoEnvironment8(*args, **kwargs):
    kwargs.setdefault('GOARCH', '386')
    return GoEnvironment(*args, **kwargs)
