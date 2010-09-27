package pkg1

import (
	"fmt"
	"testing"
)

func TestPkg1(t *testing.T) {
	fmt.Printf("pkg1.TestPkg1\n")
	Foo()
}

func BenchmarkPkg1(t *testing.B) {
	Foo()
}
