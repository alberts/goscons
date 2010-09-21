package pkg1

//#include <uuid/uuid.h>
import "C"
import "unsafe"

func Foo() {
	var i int
	_ = unsafe.Pointer(&i)
	var uuid C.uuid_t
	C.uuid_generate(&uuid[0])
}
