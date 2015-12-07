#ifndef __DLMALLOC_H__
#define __DLMALLOC_H__ 1

#include "pyport.h"

PyAPI_FUNC(void*)  dlmalloc(size_t);
PyAPI_FUNC(void)   dlfree(void*);
PyAPI_FUNC(void*)  dlrealloc(void*, size_t);

#endif /* end __DLMALLOC_H__ */
