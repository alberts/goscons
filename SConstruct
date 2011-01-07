from goscons import GoEnvironment
env = GoEnvironment(GOSCONSHELPER=None)
helper = env.Golink('goscons-helper', env.Goc('helper.go'))
if 'GOBIN' in env['ENV']:
    env.Default(env.Install(env['ENV']['GOBIN'], helper))
else:
    env.Default(env.Install('$GOROOT/bin', helper))
