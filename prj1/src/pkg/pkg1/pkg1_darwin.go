package pkg1

//#include <stdlib.h>
import "C"

func Foo() {
	C.exit(1)
}
