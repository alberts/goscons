import SCons.Builder
import SCons.Node.FS
import SCons.Util
import goutils

TEMPLATE = """package main

%(imports)s
import "testing"
import __regexp__ "regexp"

var tests = []testing.Test {
%(tests)s
}
var benchmarks = []testing.Benchmark {
%(benchmarks)s
}

func main() {
\ttesting.Main(__regexp__.MatchString, tests)
\ttesting.RunBenchmarks(__regexp__.MatchString, benchmarks)
}"""

def GenerateTestMain(target, source, env):
    tests = []
    benchmarks = []
    for s in source:
        for t in goutils.tests(s, env):
            tests.append('\ttesting.Test{"%s", %s},' % (t,t))
        for b in goutils.benchmarks(s, env):
            benchmarks.append('\ttesting.Benchmark{"%s", %s},' % (b,b))
    if len(tests) > 0 or len(benchmarks) > 0:
        imports = 'import "%s"' % env['GOPACKAGE']
    else:
        imports = ''
    fp = open(target[0].abspath, 'wb')
    params = {
        'imports' : imports,
        'tests' : '\n'.join(tests),
        'benchmarks' : '\n'.join(benchmarks)
        }
    print >>fp, TEMPLATE % params
    fp.close()

def emitter(target, source, env):
    return [source[0].dir.File('_testmain.go')], source

GoTestMainAction = SCons.Action.Action(GenerateTestMain, None)

GoTestMainBuilder = SCons.Builder.Builder(action='$GOTESTMAINCOM',
                                          src_suffix='.go',
                                          suffix='.go',
                                          emitter=emitter)

def generate(env):
    env['BUILDERS']['GoTestMain'] = GoTestMainBuilder
    env['GOTESTMAINCOM'] = GoTestMainAction
    env['GOTESTARGS'] = SCons.Util.CLVar('-v=true')
    env['GOPACKAGE'] = None

def exists(env):
    return 1
