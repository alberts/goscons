package pkg3

import "pkg1"

import (
	"testing"
)

func TestPkg3(t *testing.T) {
	pkg1.Foo()
	foo()
}
