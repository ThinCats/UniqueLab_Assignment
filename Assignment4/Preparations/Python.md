## Python 

1. `Socket`

   1. 基本操作

      1.  创建socket

      ```python
      # socket.socket([ADDR_FAMILY], [TYPE])
      sok_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      soc_srv = ...
      ```

      1. 关闭socket

      ```python
      soc_cli.close()
      ```

   2. TCP服务器

      1. 绑定端口

         ```python
         # ADDR总是以二元组形式出现
         soc_srv.bind(("127.0.0.1", 9999))
         ```

      2. 监听端口

         ```python
         # bind 后soc_srv 性质变了
         soc_srv.listen(5)
         # soc_srv.listen([最大等待连接数量])
         ```

      3. 等待并接受连接

         ```python
         while True:
             sock, addr = s.accept()
             # do something to handle (Threading)
         # accept()会阻塞直到有连接接入， 返回一个(conn, address)元组， 其中conn是一个新的socket用来与客户端进行数据交换（建立了一条通道）
         # 使用while来无限接收请求
         ```

      4. 处理连接

         ```python
         # 处理连接时使用accept得到的socket和addr进行
         sock.send([...])
         sock.recv([...])
         sock.close()
         ```

         * 隧道socket的发送与接收

           ```python
           # send, recv 均使用Bytes流
           # send 将返回成功传输的字节数， 应当检测是否完全传输完成
           # 可使用sendall()来确保传输完成， sendall()返回None说明全部传输
           # sock.send([BYTES])
           sock.send(b"Hello!")
           # [BYTES]=sock.recv([DATA_LENGTH])
           data = sock.recv(1024)
           print(data.decode("utf-8"))
           ```

      5. 流程

         ```mermaid
         graph LR
         建立[建立 socket.socket]-->绑定[绑定服务器端口 bind]
         绑定 --> 监听[监听端口 listen]
         监听 --> 接受[等待接受请求]
         接受 -->|循环| 接受
         接受 --> 接受成功
         接受成功[接受成功] --> 处理[处理连接]
         ```

   3. TCP客户端

      1. 建立socket

      2. 建立连接

         ```python
         # 需要服务器地址
         soc_cli.connect(("baidu.con", 80))
         ```

      3. 发送

         ```python
         soc_cli.send([BYTES])
         ```

      4. 接收

         ```python
         while True:
             data = soc_cli.recv(1024)
             if data:
                 # data valid, do something
             else:
                 break
         # 一次只能接收有限字节， 需要使用循环接收所有字节
         # 当data为空则说明接收完毕
         ```

   4. UDP服务器

      1. 建立socket

      2. 绑定端口

      3. 等待接收数据

         ```python
         # UDP 服务器不需要listen()与accept()， 一个原因是因为UDP不需要建立专用的隧道， 由此直接使用recvfrom()来接受数据， 但recvfrom不同的是， 它还将返回发送者的addr
         # Return (bytes, address)
         data, addr = soc_srv.recvfrom(1024)
         
         ```

      4. 发送数据

         ```python
         # UDP没有建立隧道， 所以需要使用sendto来指示接收地址addr(它是一个二元组)
         # 这里是两个参数， 而不是一个元组
         soc_srv.sendto(b"hello", addr)
         ```

   5. UDP客户端

      1. 建立socket

      2. 发送数据

         ```python
         soc_cli.sendto(b"hi", ("127.0.0.1", 9999))
         ```

      3. 接收数据

         ```python
         # 这里不需要发送者的地址， 使用recv即可
         data = soc_cli.recv(1024)
         ```

2. `Encode` and `Decode`

   ```python
   # encode => 将str编码成bytes, bytes可以为任意编码
   data = "Hello, world".encode('utf-8')
   
   # decode => 将bytes解码为str， str一般为utf-8编码
   sim_str = data.decode('utf-8')
   ```

   ​        

3. `SocketServer`

   1. 流程

      ```mermaid
      graph TD
      A[继承BaseRequestHandler创建Handler]
      B[传入server_addr和Handler创建socketserver]
      C[调用server的handle_request或server_forever处理request]
      D[关闭server]
      A --> B
      B --> C
      C --> D
      ```

      

   2. 一些东西

      1. request

         每接受到一个请求将实例化一个新的handler来处理

         * Server 通过以下流程来处理request

           ```python
           # get_requst() -> verify_request() -> process_request()
           ```

           

         * request 通过 server的`get_request()`来获取， 根据服务器不同而不同

           ```python
           # request 构成
           # 传递给handler， 又所改变
           # 在TCP中， self.request是隧道socket
           # 在UDP中， self.request是二元组（data， socket）
           ```

         * `verify_request()`可以来判断`request`是否应该被调用， 用来给server增加控制与访问权限

         * `process_request()` 调用`finish_requst()`来处理request， 先将`RequestHandlerClass`实例化， 再调用里面的`handle()`来处理request

      2. constructor

         constructor 为实例化socketserver进行的操作

         * 对TCP server来说

           ```python
           # Call server_bind() to bind addr to socket
           # like bind()
           # call server_activate() to listen on the socket
           # like listen()
           ```

      3. Handler Class

         * Some attributions:
           1. self.request
           2. self.client_address
           3. self.server

4. `Struct`

   1. 基本操作 `pack`， `unpack`

      ```python
      # pack 类似encode， 将数据打包成bytes
      struct.pack(">I", 123)
      # 这里 '>' 代表网络序， 也就是大端
      
      # unpack 类似decode， 将bytes解包成相应的数据
      struct.unpack(">IH", b"\xf0")
      ```

   2. 常用格式符

      ```c
      ">": big-endian
      "c": char bytes of 1
      "b": signed char integer of 1
      "h": short 2
      "i": int 4
      "s": char[] bytes ==> Usage 4s
      // 以及大写， 表示unsigned
      // 主要 b 和 c 的区别
      ```

      

   3. 参考表

   4. 特殊用法

      ```python
      # struct.unpack_from(fmt, buffer, offset=0)
      根据格式化字符串fmt，从位置offset开始解包
      # struct.pack_into(fmt, buffer, offset, v1, v2)
      根据格式化字符串fmt，封装v1，v2等值，并从位置offset开始，将封装的字节写入可写缓冲区buffer中。注意，offset是必需的参数。
      # fmt 格式
      可以在格式化字符之前使用整数表示重复次数。例如，“4h”完全等价于“hhhh”
      ```

      

5. `Threading`

   1. 创建thread 实例

      ```python	
      # target是启动函数， name是该实例名称， 使用threading.current_thread().name可以获得
      task1 = threading.Thread(target=loop, name='LoopThread')
      ```

   2. 启动thread

      ```python
      task1.start()
      ```

   3. 主线程或者调用线程join， 等待线程结束

      ```python
      # 线程task1被mainThread join， 那么mainThread会阻塞直到task1结束
      task1.join()
      ```

   4. 流程

     ```mermaid
     graph LR
     Create["建立 Thread(target=loop)"]
     Start["启动 task1.start()"]
     Join["等待 task1.join()"]
     Create --> Start
     Start --> Join
     ```

   5. `Lock`

      1. 生成锁实例

         ```python
         lock = threading.lock()
         ```

      2. 获取锁

         ```python
         # 执行操作前先获取锁
         lock.acquire()
         # do somethon
         ```

      3. 释放锁

         ```python
         # 操作完成释放锁， 为避免锁没有被释放
         # 需要使用try... finally...来强行要求其释放
         try:
             # do something
         finally:
             lock.release()
         ```

      4. 

         ```mermaid
         graph TD
         Create["生成锁实例 lock = threading.lock()"]
         Acquire["获得锁 lock.acquire()"] --> Release["释放锁 lock.release()"]
         ```

   6. `Local`

      方便Thread使用局部变量的好东西, 相当于各thread的全局变量，不同函数可以使用， 但是各thread不会影响

      1. 创建local

         ```python
         # local()像一个dict， 存放这不同thread的锁需要的变量
         local_data = threading.local()
         ```

      2. 绑定变量

         ```python
         # 需要使用的变量
         local_data.money = 100
         # 这样在thread内部的函数都可以使用
         ```

      3. 使用变量

         ```python
         print(local_data.money)
         ```

         这样可以为每一个线程绑定一个连接信息， 供这个线程的所有函数使用该信息（变量）

       

6. `Str`

   关于`str`的常用方法

   1. `split()`

      ```python
      # str.split(str=".", num=1)
      # "."是分隔符， 1 是分割子串的个数 如
      # 返回 字符串列表
      str1 = "Line1-abcdef \nLine2-abc \nLine4-abcd";
      print(str1.split( ));
      print(str1.split(' ', 1 ));
      
      # ['Line1-abcdef', 'Line2-abc', 'Line4-abcd']
      # ['Line1-abcdef', '\nLine2-abc \nLine4-abcd']
      ```

   2. `strip()`

      ```python
      # 移除字符串头尾指定的字符序列
      # str.strip([chars])
      
      str1 = "*****this is **string** example....wow!!!*****"
      print (str1.strip( '*' ))  # 指定字符串 *
      
      # this is **string** example....wow!!!
      ```

      以上不带参数时， 默认为空白符

7. `IP`地址转换

   1. 相关函数`inet_aton`, `inet_ntoa`  For `IPV4`

      ```python
      # a: ascill string => 主机序
      # n: numberic => 网络序
      ip_packed = socket.inet_aton("1.1.1.1")
      ip = socket.inet_ntoa(ip_packed)
      ```

      