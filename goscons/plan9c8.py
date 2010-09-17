def generate(env):
    env['P9CC'] = '8c'

def exists(env):
    return env.Detect('8c')
