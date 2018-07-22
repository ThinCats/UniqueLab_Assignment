# Python 

1. `Filestream`

   1. Open `fd`

      ```python
      with open("./pac", "r") as f:
          print(f.readlines())
      # With encoding
      with open("./a.txt", "r", encoding="gbk") as f:
          f.read(4)
      ```

   2. read

      ```python
      # read(size)
      # readline()
      # readlines() --> Return []
      ```

      

2. EPOLL

3. Socket

4. 