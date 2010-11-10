package pkg3

import (
	p16 "pkg1/pkg6"
)

// only test in same package can see this
func foo() {
	p16.Foo()
}
