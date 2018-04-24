
#ifndef ERROR_FUNCTIONS_H
#define ERROR_FUNCTIONS_H

#include <cstdarg>
#include "ename.c.inc"
#include "basic_libs.h"  // for basic printf and snprintf


void errMsg(const char* format, ...);

void errExit(const char* format, ...);




#endif // ERROR