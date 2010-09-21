from goscons import GoEnvironment
env = GoEnvironment(GOSCONSHELPER=None)
helper = env.Golink('goscons-helper', env.Goc('helper.go'))
env.Default(env.Install('$GOROOT/bin', helper))
