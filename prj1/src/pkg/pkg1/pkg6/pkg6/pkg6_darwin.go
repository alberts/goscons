package pkg6

//#include <stdlib.h>
import "C"

func Foo() {
	C.exit(1)
}
