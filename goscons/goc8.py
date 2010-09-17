def generate(env):
    env['GOC'] = '8g'
    env['GOOBJSUFFIX'] = '.8'

def exists(env):
    return env.Detect('8g')
