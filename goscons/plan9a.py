def exists(env):
    env['GOASCOM'] = '$GOAS -o $TARGET $GOASFLAGS $SOURCES'

def generate(env):
    pass

def exists(env):
    return 1
