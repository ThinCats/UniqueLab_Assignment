# File Indexer

This is a simple and slow file indexer used for searching words in various files written based on C++.

It will facilitate in building index and search from index

---

## Features

1. Search word in files
2. Search multi words in files
3. Search words and display the lines in the files where words occur
4. Using Redis, So that it's easy for future reusing

## Install and Run on POSIX

Just move `searcher ` and `indexer`  two binaries files into a same directory

```shell
$ ./search /usr/include main if else
```



## Compile

1. Use `cmake` to manage the project

2. Command

   ```shell
   $ cd indexer/ && mkdir build && cd build
   $ cmake ..
   $ make
   $ cd ../../searcher && mkdir build && cd build
   $ cmake ..
   $ make
   $ cp ../../indexer/build/indexer ./indexer
   ```

   ​

## Usage

1. type `--help` to see the usage
2. just use `$ ./search path word1[word2...]` to search word1, word2 in path

## Output

Output is like this

```shell
$ /usr/include/c++/7.3.1/parallel/quicksort.h: if(4): line 109,117,122,167 main(1): line 145 
$ /usr/include/c++/7.3.1/parallel/random_shuffle.h: if(14): line 250,279,284,297,303,317,323,330,422,431,437,451,456,462 main(2): line 148,205
```

