"""Make unit test for addmul128() in multiply_32.c"""

class Count(object):
    def __init__(self):
        self.count = 0

    def next(self):
        self.count += 1
        return self.count
counter = Count()

def split64(long_int):
    """Split long_int into 64-bit words big-endian"""

    assert(long_int >= 0)

    if long_int == 0:
        return [ "0" ]

    result = []
    while long_int:
        result += [ "0x%xULL" % (long_int & (2**64-1)) ]
        long_int >>= 64
    return result

def make_test(a):

    # Turn a[] and the result into arrays of 64-bit words
    result = split64(a**2)
    a = split64(a)

    # Computation does not depend on zero terms
    result_len = 2 * len(a)

    # Pad the output vector with as many padding zeroes as needed
    for x in xrange(result_len - len(result)):
        result.append("0")

    # Fill output buffer with values that must be overwritten
    t = [ "0xCCCCCCCCCCCCCCCCULL" ] * result_len

    print ""
    print "void test_%d() {" % counter.next()
    print "    const uint64_t a[] = {" + ", ".join(a) + "};"
    print "    uint64_t t[] = {" + ", ".join(t) + ", 0xAAAAAAAAAAAAAAAAULL};"
    print "    const uint64_t expected_t[] = {" + ", ".join(result) + "};"
    print "    size_t result;"
    print ""
    print "    result = square_w(t, a, %d);" % len(a)
    print "    assert(memcmp(t, expected_t, 8*%d) == 0);" % result_len
    #print '    printf("t[{0}]=0x%016lX\\n", t[{0}]);'.format(result_len)
    print "    assert(t[%d] == 0xAAAAAAAAAAAAAAAAULL);" % result_len
    print "    assert(result == %d);" % result_len
    print "}"
    print ""

def make_main():
    print "int main(void) {"
    for i in xrange(1, counter.next()):
        print "    test_%d();" % i
    print "    return 0;"
    print "}"


print "#include <assert.h>"
print "#include <string.h>"
print "#include <stdint.h>"
print "#include <stdio.h>"
print '#include "multiply.h"'

make_test(0)
make_test(0xFF)
make_test(2738)
make_test(82738748374923632473)
make_test(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)

make_main()
