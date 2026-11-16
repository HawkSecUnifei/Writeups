#ifndef EASY_RUNTIME_H
#define EASY_RUNTIME_H

#include <stddef.h>

void *rt_array_alloc(long long nelems);
void  rt_array_setlen(void *arr, long long len);
void  rt_concat_copy(void *c, void *a, void *b, long long cap, long long la);
void  rt_register(void (*fn)(void));
void  rt_print(long long v);
void  rt_oob(void);
void  rt_finish(void);

void  win(void);
#endif
