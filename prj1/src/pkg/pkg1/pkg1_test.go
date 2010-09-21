package pkg1_test

import (
	. "pkg1"
	"testing"
)

func TestPkg1(t *testing.T) {
	Foo()
}

func BenchmarkPkg1(t *testing.B) {
	Foo()
}
