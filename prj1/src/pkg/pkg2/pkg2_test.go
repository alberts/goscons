package pkg2

import (
	"fmt"
	"os"
	"testing"
)

func TestPkg2(t *testing.T) {
	fmt.Printf("pkg2.TestPkg2\n")
	Foo()
	if len(os.Getenv("CRASH")) > 0 {
		os.Exit(1)
	}
}

func BenchmarkPkg2(t *testing.B) {
	Foo()
}
