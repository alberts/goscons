package pkg6

import (
	"fmt"
	"testing"
)

func TestPkg6(t *testing.T) {
	fmt.Printf("pkg1/pkg6.TestPkg6\n")
	Foo()
}

func BenchmarkPkg6(t *testing.B) {
	Foo()
}
