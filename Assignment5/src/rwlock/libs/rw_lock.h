#ifndef _RW_LOCK_H
#define _RW_LOCK_H

#include <pthread.h>
#include <errno.h>

typedef struct rwlock_t_1 {
    pthread_mutex_t writer_lock;
    pthread_mutex_t reader_lock;
    pthread_cond_t writer_cond;
    pthread_cond_t reader_cond;
    int readers;
    int writers;
} rwlock_t_1;

typedef struct rwlock_t {
    pthread_mutex_t flag_lock;
    pthread_cond_t writer_cond;
    pthread_cond_t reader_cond;
    int readers;
    int writers;
    int writers_queue;
} rwlock_t;

int rwlock_init(rwlock_t *lock, void* attr);

int rwlock_destroy(rwlock_t *lock);

int rwlock_rdlock(rwlock_t *lock);

int rwlock_wrlock(rwlock_t *lock);

int rwlock_unlock(rwlock_t *lock);

#endif