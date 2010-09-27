package pkg1

import (
	"testing"
)

func TestMorePkg1(t *testing.T) {
	Foo()
}

func BenchmarkMorePkg1(t *testing.B) {
	Foo()
}
