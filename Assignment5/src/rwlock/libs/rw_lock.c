#include "rw_lock.h"

int rwlock_init(rwlock_t *lock, void *attr) {

    int err = pthread_mutex_init(&lock->flag_lock, NULL);
    if(err != 0)
        return err;
    err = pthread_cond_init(&lock->writer_cond, NULL);
    if(err != 0)
        return err;
    err = pthread_cond_init(&lock->reader_cond, NULL);
    if(err != 0)
        return err;
    
    lock->readers = 0;
    lock->writers = 0;
    lock->writers_queue = 0;

    return 0;
}

int rwlock_rdlock(rwlock_t *lock) {

    int err = pthread_mutex_lock(&lock->flag_lock);
    if(err != 0)
        return err;
    // Means writer and writers waiting
    while(lock->writers != 0 || lock->writers_queue != 0) {
        err = pthread_cond_wait(&lock->reader_cond, &lock->flag_lock);
        if(err != 0)
            return err;
    }

    // It's reader's turn
    lock->readers++;

    // Release lock
    err = pthread_mutex_unlock(&lock->flag_lock);
    if(err != 0)
        return err;
    return 0;
}

int rwlock_wrlock(rwlock_t *lock) {
    int err = pthread_mutex_lock(&lock->flag_lock);
    if(err != 0)
        return err;

    // Means there is writer or readers
    lock->writers_queue++;
    while(lock->writers != 0 || lock->readers != 0) {
        err = pthread_cond_wait(&lock->writer_cond, &lock->flag_lock);
        if(err != 0)
            return err;
    }
    lock->writers_queue--;

    // It's writers turn
    lock->writers = 1;

    // Release
    err = pthread_mutex_unlock(&lock->flag_lock);
    if(err != 0)
        return err;

    return 0;
}

int rwlock_unlock(rwlock_t *lock) {

    if(lock->readers != 0) {
        int signal_state = 0;

        // It's readers' lock
        int err = pthread_mutex_lock(&lock->flag_lock);
        if(err != 0) 
            return err;

        lock->readers--;
        // The last one reader
        if(lock->readers == 0) 
            signal_state = 1;
        err = pthread_mutex_unlock(&lock->flag_lock);
        if(err != 0)    
            return err;
        
        // Send the signal
        if(signal_state == 1)
            pthread_cond_signal(&lock->writer_cond);

    } else {
        // Whether to brocast the cond
        // 1 ->call reader, not call writer. 2 -> call writer not reader
        int cond_state = 1;

        // It's writer's lock
        int err = pthread_mutex_lock(&lock->flag_lock);
        if(err != 0)
            return err;
        
        lock->writers = 0;
        // Judge the state 
        if(lock->writers_queue != 0)
            cond_state = 2;
        else
            cond_state = 1;

        // Release
        err = pthread_mutex_unlock(&lock->flag_lock);
        if(err != 0)
            return err;
        
        if(cond_state == 1)
            err = pthread_cond_broadcast(&lock->reader_cond);
        else if(cond_state == 2)
            err = pthread_cond_signal(&lock->writer_cond);
        if(err != 0)
            return err;
    }
    return 0;
}       

int rwlock_destroy(rwlock_t *lock) {
    int err = pthread_mutex_destroy(&lock->flag_lock);
    if(err != 0)
        return err;

    err = pthread_cond_destroy(&lock->reader_cond);
    if(err != 0)
        return err;

    err = pthread_cond_destroy(&lock->writer_cond);
    if(err != 0)
        return err;
        
    return 0;
}