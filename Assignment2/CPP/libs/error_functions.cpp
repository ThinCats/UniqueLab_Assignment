
#include "error_functions.h"

void outputError(int err, const char *format, va_list ap) {
    const int BUF_SIZE = 500;
    char userMsg[BUF_SIZE], buf[BUF_SIZE], errText[BUF_SIZE];

    snprintf(userMsg, BUF_SIZE, format, ap);

    // Refer to http://man7.org/tlpi/code/online/diff/lib/error_functions.c.html for his ename file
    // To print out error message
    snprintf(errText, BUF_SIZE, "[%s %s]", (err>0&&err<=MAX_ENAME)?ename[err]:"unknown", strerror(err));

    fflush(stdout);
    fflush(stderr);
    
}


// format means user edited messages
void errMsg(const char *format, ...) {
    
    // This is a typical use for variadic argument referred to https://en.wikipedia.org/wiki/Stdarg.h
    va_list argList;
    
    // To avoid change in errno
    int saveErrno = errno;

    va_start(argList, format);
    outputError(errno, format, argList);
    va_end(argList);

    errno = saveErrno;

}

void errExit(const char *format, ...) {
    // The same as errMsg
    va_list argList;
    int saveErrno = errno;

    va_start(argList, format);
    outputError(errno, format, argList);
    va_end(argList);

    errno = saveErrno;
    
    
    exit(EXIT_FAILURE);
}