#include <pthread.h>
#include <math.h>
#include <stdlib.h>
#include <stdio.h>

#define THREAD_NUM 4
void *thread_prime(void *args);

typedef struct prime_args {
    long long start;
    long long end;
    long long *prime_list;
} prime_args;

int main(void) {

    long long n;
    scanf("%ld", &n);
    n = n + 1;

    long long *prime_list = (long long *)malloc(sizeof(long long)*(n+2));

    pthread_t threads[THREAD_NUM];
    prime_args args[THREAD_NUM];
    int i;

    // Init prime_list

    long long l = n / THREAD_NUM;
    for(i=0;i < THREAD_NUM;i++) {
        args[i].start = l*i + 2; // Start from 2;

        args[i].end = l*(i+1) - 1 + 2;
        printf("Start=%d, end=%d\n", args[i].start, args[i].end);

        args[i].prime_list = prime_list;

        int err = pthread_create(&threads[i], NULL, thread_prime, (void *)&args[i]);
        printf("THREAD %d starts\n", i+1);
        if(err != 0)
            printf("CREATE id: %d, err: %d\n", i, err);
    }

    // Join thread
    for(i = 0;i < THREAD_NUM;i++) {
        int err = pthread_join(threads[i], NULL);
        if(err != 0)
            printf("JOIN id: %d, err: %d\n", i, err);

        printf("THREAD %d finished\n", i+1);
    }
    return 0;
    // Print
    long long j;
    for(j=2;j < n;j++)
        if(prime_list[j] == 1)
            printf("%ld\n", j);

    return 0;

}

void *thread_prime(void *args) {

    prime_args *info= (prime_args *)args;

    long long i, j, m;
    long end_sqrt = sqrt(info->end);
    // init prime
    for(i = info->start/2*2;i <= info->end;i+=2)
        info->prime_list[i] = 1;

    for(i = 3; i <= end_sqrt; i++) {

        if(info->prime_list[i] == 0)
            // not prime
            continue;
        // Find m*i near start
        
        m = i * i;
        if(m >= info->start)
            j = m;
        else {
            m = (info->start / i) * i;
            j = (info->start == m) ? info->start: m + i;
        }
        
        for(; j <= info->end;j+=i) {
            info->prime_list[j] = 0;
        }

    }

}
