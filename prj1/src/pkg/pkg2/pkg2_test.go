package pkg2

import (
	"testing"
)

func TestPkg2(t *testing.T) {
	Foo()
}

func BenchmarkPkg2(t *testing.B) {
	Foo()
}
