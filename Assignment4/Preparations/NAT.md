# NAT

1. 类型

   1. 共同点: 内部主机的一个通信端口映射到一个外部地址(eip:port)

   2. 不同点: 类型不同， 对外部主机的要求不同， 由NAT设备进行筛选控制

      1. NAT1： 任意ip与端口都可通过

         > Full cone

      2. NAT2：固定ip与任意端口可通过

         > Address-Restricted

      3. NAT3：固定ip与固定端口可通过

         > Port-Restricted

      4. 对称型NAT：内部主机的映射随着目的地而变化

         > Symmertric NAT

# 内网穿透

1. STUN

   1. 查询自己的映射地址以及NAT类型

   2. 方式:

      1. 客户端：

      ```sequence
      Client->Server: Hello packet
      Note right of Server: Do sth to find out NAT
      Server->Client: Your exip and port, NAT
      ```

      2. 服务端：

         [算法](https://i.loli.net/2018/07/19/5b5080b66fe7d.bmp)


   3. 服务器中转

      1. 方式:

         1. 本地代理与远端代理相连接， 远端代理负责外部主机的通信并转发给本地代理， 本地代理负责与本机服务通信， 将数据包转发给本地服务

      2. 流程

         1. Handshake

            ```sequence
            
            localProxy->remoteProxy: b"Hello".encr
            Note right of remoteProxy: Verifying "Hello"
            remoteProxy->localProxy: b"Verfied"+b"Hello".encr
            localProxy -> remoteProxy: I want your port 80
            Note right of remoteProxy: Check port valid<br>open It
            remoteProxy->localProxy: [Got it](status) port 80
            localProxy --> remoteProxy: Keep connection
            localProxy -- remoteProxy: Forwarding packet
            localProxy -- remoteProxy: Keep connection
            ```

            * Protocol frame 

              

              ​	 xxxxxxxxxx # RequestVERSION | REQUEST | PORT# ResponseVERSION | STATUS | PORT

              


      ​      

         2. DATA Forwarding

         ```mermaid
         sequenceDiagram
         participant localHTTP
         participant localProxy
         participant remoteProxy
         participant externCli
       
         externCli->>remoteProxy: b"GET /"
         Note left of externCli: Port: 80
         remoteProxy-->>localProxy: b"GET /".encr
         Note left of remoteProxy: RANDOM_PORT
         localProxy ->>localHTTP: b"GET /"
         Note left of localProxy: Port: 80
         localHTTP->> localProxy: b"response: 404"
         localProxy-->>remoteProxy: b"response: 404".encr
         remoteProxy-->>externCli: b"response: 404"
         ```

         

      ```uml
      @startuml
      
      @enduml
      ```

      

