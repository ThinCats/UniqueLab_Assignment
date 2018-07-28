#include "rw_lock.h"
#include <stdio.h>
int rwlock_init(rwlock_t *lock, void *attr) {
    int err;

    // init lock
    err = pthread_mutex_init(&lock->reader_lock, NULL);
    if(err != 0)
        return err;
    err = pthread_mutex_init(&lock->writer_lock, NULL);
    if(err != 0)
        return err;
    // init cond
    err = pthread_cond_init(&lock->writer_cond, NULL);
    if(err != 0)
        return err;
    err = pthread_cond_init(&lock->reader_cond, NULL);
    if(err != 0)
        return err;
    // init readers
    lock->readers = 0;
    lock->writers = 0;

}
int rwlock_wrlock(rwlock_t *lock) {
    int err = 0;
    printf("Writor locking\n");

    // Block reader to prevent them from reading books    
    // err = pthread_mutex_lock(&lock->reader_lock);
    err = pthread_mutex_lock(&lock->writer_lock);
    if(err != 0)
        return err;

    pthread_mutex_lock(&lock->reader_lock);
    // Block until readers reduce
    while(lock->readers != 0) {
        // Onece it has cond, try lock writer.2000
        // This is pervent other writers actions
        printf("Waiting\n");
        pthread_mutex_unlock(&lock->reader_lock);
        err = pthread_cond_wait(&lock->writer_cond, &lock->writer_lock);
        if(err != 0)
            return err;
        pthread_mutex_unlock(&lock->reader_lock);
    }
    // Set writers status
    lock->writers = 1;
    // Successful
    printf("Writor locked\n");
    return 0;
}

int rwlock_rdlock(rwlock_t *lock) {
    int err;

    printf("Reader locking\n");
    // Stops get in if writor get lock
    while(lock->writers != 0) {
        err = pthread_cond_wait(&lock->reader_cond, &lock->reader_lock);
        if(err != 0)
            return err;
    }


    // Block writer pervent from wrting
    // If occur ebusy, means it already locked.
    // Therefore ignore it 
    err = pthread_mutex_trylock(&lock->writer_lock);
    if(err != 0 && err != EBUSY)
        return err;

   
    lock->readers++;
    err = pthread_mutex_unlock(&lock->reader_lock);
    if(err != 0)
        return err;
    printf("Reader locked\n");
    return 0;
}

int rwlock_unlock(rwlock_t *lock) {
    int err;
    // Judge whether it's reader or writer
    if(lock->readers != 0) {
        printf("Reader unlocking\n");
        // It's reader
        err = pthread_mutex_lock(&lock->reader_lock);
        if(err != 0)
            return err;
        lock->readers--;
        err = pthread_mutex_unlock(&lock->reader_lock);
        if(err != 0)
            return err;
        err = pthread_mutex_unlock(&lock->writer_lock);
        if(err != 0)
            return err;
        
        // Send cond if last One
        if(lock->readers == 0) {
            // Wake up one writer
            err = pthread_cond_signal(&lock->writer_cond);
            if(err != 0)
                return err;
        }
        printf("Reader unlocked\n");
    }
    else {
        printf("Writor unlocking\n");
        // err = pthread_mutex_lock(&lock->writer_lock);
        if(err != 0)
            return err;
        lock->writers = 0;
        printf("Writor unlocked\n");
        err = pthread_mutex_unlock(&lock->writer_lock);
        if(err != 0)
            printf("ERROR: %d\n", err);
            return err;
        
        // Send cond to announce I finish
        err = pthread_cond_broadcast(&lock->reader_cond);
        if(err != 0)
            printf("ERROR: %d", err);
            return err;
        
    }
    return 0;
}   

int rwlock_destroy(rwlock_t *lock) {
    int err;
    err = pthread_mutex_destroy(&lock->reader_lock);
    if(err != 0)
        return err;
    err = pthread_mutex_destroy(&lock->writer_lock);
    if(err != 0)
        return err;
    err = pthread_cond_destroy(&lock->writer_cond);
    if(err != 0)
        return err;
    err = pthread_cond_destroy(&lock->reader_cond);
    if(err != 0)
        return err;

    return 0;
} 