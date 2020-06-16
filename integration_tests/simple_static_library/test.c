#include <string.h>
#include <stdio.h>

#include "helloworlder.h"

int main(void) {
    printf("Hello from test!\n");
    return strncmp(getHello(), "Hello world!\n", 100);
}
