from SCons.Script import Environment
import SCons.Tool
import os

module_dir = os.path.abspath(os.path.dirname(__file__))
SCons.Tool.DefaultToolpath.append(module_dir)

def GoEnvironment(*args, **kwargs):
    return Environment(*args, ENV=os.environ, tools=['golang','default'], **kwargs)
