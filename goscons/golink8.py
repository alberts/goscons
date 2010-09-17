def generate(env):
    env['GOLINK'] = '8l'

def exists(env):
    return env.Detect('8l')
