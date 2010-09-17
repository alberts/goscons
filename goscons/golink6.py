def generate(env):
    env['GOLINK'] = '6l'

def exists(env):
    return env.Detect('6l')
