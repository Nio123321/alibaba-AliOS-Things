/*
 * Copyright (C) 2015-2017 Alibaba Group Holding Limited
 */

#include <k_api.h>
#include <assert.h>
#include <stdio.h>
#include <sys/time.h>

#if (RHINO_CONFIG_HW_COUNT > 0)
void soc_hw_timer_init(void)
{
}

hr_timer_t soc_hr_hw_cnt_get(void)
{
    return 0;
}

lr_timer_t soc_lr_hw_cnt_get(void)
{
    return 0;
}
#endif /* RHINO_CONFIG_HW_COUNT */

#if (RHINO_CONFIG_INTRPT_GUARD > 0)
void soc_intrpt_guard(void)
{
}
#endif

#if (RHINO_CONFIG_INTRPT_STACK_REMAIN_GET > 0)
size_t soc_intrpt_stack_remain_get(void)
{
    return 0;
}
#endif

#if (RHINO_CONFIG_INTRPT_STACK_OVF_CHECK > 0)
void soc_intrpt_stack_ovf_check(void)
{
}
#endif
#if (RHINO_CONFIG_MM_TLF > 0)
void *aos_zalloc(unsigned int size)
{
    void *tmp = NULL;

    if (size == 0) {
        return NULL;
    }

#if (RHINO_CONFIG_MM_DEBUG > 0u && RHINO_CONFIG_GCC_RETADDR > 0u)
    if ((size & AOS_UNSIGNED_INT_MSB) == 0) {
        tmp = krhino_mm_alloc(size | AOS_UNSIGNED_INT_MSB);

#ifndef AOS_BINS
#if defined(__CC_ARM)
        krhino_owner_attach(g_kmm_head, tmp, __return_address());
#elif defined(__GNUC__)
        krhino_owner_attach(g_kmm_head, tmp,
                            (size_t)__builtin_return_address(0));
#endif /* __CC_ARM */
#endif
    } else {
        tmp = krhino_mm_alloc(size);
    }

#else
    tmp = krhino_mm_alloc(size);
#endif

    if (tmp) {
        memset(tmp, 0, size);
    }

    return tmp;
}

void *aos_malloc(unsigned int size)
{
    void *tmp = NULL;

    if (size == 0) {
        return NULL;
    }

#if (RHINO_CONFIG_MM_DEBUG > 0u && RHINO_CONFIG_GCC_RETADDR > 0u)
    if ((size & AOS_UNSIGNED_INT_MSB) == 0) {
        tmp = krhino_mm_alloc(size | AOS_UNSIGNED_INT_MSB);

#ifndef AOS_BINS
#if defined(__CC_ARM)
        krhino_owner_attach(g_kmm_head, tmp, __return_address());
#elif defined(__GNUC__)
        krhino_owner_attach(g_kmm_head, tmp,
                            (size_t)__builtin_return_address(0));
#endif /* __CC_ARM */
#endif
    } else {
        tmp = krhino_mm_alloc(size);
    }

#else
    tmp = krhino_mm_alloc(size);
#endif

    return tmp;
}

void *aos_calloc(unsigned int nitems, unsigned int size)
{
    void *tmp = NULL;
    size_t len = (unsigned int)nitems*size;

    if (len == 0) {
        return NULL;
    }

#if (RHINO_CONFIG_MM_DEBUG > 0u && RHINO_CONFIG_GCC_RETADDR > 0u)
    if ((len & AOS_UNSIGNED_INT_MSB) == 0) {
        tmp = krhino_mm_alloc(len | AOS_UNSIGNED_INT_MSB);

#ifndef AOS_BINS
#if defined(__CC_ARM)
        krhino_owner_attach(g_kmm_head, tmp, __return_address());
#elif defined(__GNUC__)
        krhino_owner_attach(g_kmm_head, tmp,
                            (size_t)__builtin_return_address(0));
#endif /* __CC_ARM */
#endif
    } else {
        tmp = krhino_mm_alloc(len);
    }

#else
    tmp = krhino_mm_alloc(len);
#endif

    if (tmp) {
        memset(tmp, 0, len);
    }

    return tmp;
}

void *aos_realloc(void *mem, unsigned int size)
{
    void *tmp = NULL;

#if (RHINO_CONFIG_MM_DEBUG > 0u && RHINO_CONFIG_GCC_RETADDR > 0u)
    if ((size & AOS_UNSIGNED_INT_MSB) == 0) {
        tmp = krhino_mm_realloc(mem, size | AOS_UNSIGNED_INT_MSB);

#ifndef AOS_BINS
#if defined(__CC_ARM)
        krhino_owner_attach(g_kmm_head, tmp, __return_address());
#elif defined(__GNUC__)
        krhino_owner_attach(g_kmm_head, tmp,
                            (size_t)__builtin_return_address(0));
#endif /* __CC_ARM */
#endif
    } else {
        tmp = krhino_mm_realloc(mem, size);
    }

#else
    tmp = krhino_mm_realloc(mem, size);
#endif

    return tmp;
}

void aos_alloc_trace(void *addr, size_t allocator)
{
#if (RHINO_CONFIG_MM_DEBUG > 0u && RHINO_CONFIG_GCC_RETADDR > 0u)
#ifndef AOS_BINS
    krhino_owner_attach(g_kmm_head, addr, allocator);
#endif
#endif
}

void aos_free(void *mem)
{
    if (mem == NULL) {
        return;
    }

    krhino_mm_free(mem);
}
#endif

#if (RHINO_CONFIG_MM_TLF > 0)

#if defined (__CC_ARM) /* Keil / armcc */

#define HEAP_BUFFER_SIZE (MIN_FREE_MEMORY_SIZE+RHINO_CONFIG_MM_TLF_BLK_SIZE)
int           g_region_num = 1;

uint8_t g_heap_buf[HEAP_BUFFER_SIZE];
//k_mm_region_t g_mm_region[1] = {{g_heap_buf, HEAP_BUFFER_SIZE}};
k_mm_region_t g_mm_region[1];
void aos_heap_set()
{
    g_mm_region[0].start = g_heap_buf;
    g_mm_region[0].len   = HEAP_BUFFER_SIZE;
}



#elif defined (__ICCARM__)/* IAR */

#define HEAP_BUFFER_SIZE 1024*20
int           g_region_num = 1;

uint8_t g_heap_buf[HEAP_BUFFER_SIZE];
k_mm_region_t g_mm_region[] = {{g_heap_buf, HEAP_BUFFER_SIZE}};
void aos_heap_set()
{
    g_mm_region[0].start = g_heap_buf;
    g_mm_region[0].len   = HEAP_BUFFER_SIZE;
}

#else /* GCC */
extern void         *_estack;
extern void         *__bss_end__;
/* __bss_end__ and _estack is set by linkscript(*.ld)
   heap and stack begins from __bss_end__ to _estack */
k_mm_region_t g_mm_region[1];
int           g_region_num = 1;
void aos_heap_set()
{
    g_mm_region[0].start = (uint8_t*)&__bss_end__;
    g_mm_region[0].len   = 
        ((uint8_t*)&_estack - (uint8_t*)&__bss_end__) - RHINO_CONFIG_SYSTEM_STACK_SIZE;
}
#endif
#endif

#if (RHINO_CONFIG_MM_LEAKCHECK > 0 )

extern int __bss_start__, __bss_end__, _sdata, _edata;

void aos_mm_leak_region_init(void)
{
#if (RHINO_CONFIG_MM_DEBUG > 0)
    krhino_mm_leak_region_init(&__bss_start__, &__bss_end__);
    krhino_mm_leak_region_init(&_sdata, &_edata);
#endif
}

#endif


#if (RHINO_CONFIG_TASK_STACK_CUR_CHECK > 0)
size_t soc_get_cur_sp()
{
    size_t sp = 0;
#if defined (__GNUC__)&&!defined(__CC_ARM)
    asm volatile(
        "mov %0,sp\n"
        :"=r"(sp));
#endif
    return sp;
}
static void soc_print_stack()
{
    void    *cur, *end;
    int      i=0;
    int     *p;

    end   = krhino_cur_task_get()->task_stack_base + krhino_cur_task_get()->stack_size;
    cur = (void *)soc_get_cur_sp();
    p = (int*)cur;
    while(p < (int*)end) {
        if(i%4==0) {
            printf("\r\n%08x:",(uint32_t)p);
        }
        printf("%08x ", *p);
        i++;
        p++;
    }
    printf("\r\n");
    return;
}
#endif

void soc_err_proc(kstat_t err)
{
    (void)err;
    
    #if (RHINO_CONFIG_TASK_STACK_CUR_CHECK > 0)
    soc_print_stack();
    #endif
    assert(0);
}

krhino_err_proc_t g_err_proc = soc_err_proc;


