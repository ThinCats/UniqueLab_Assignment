# Linux

1. Firewall Configure

   1. `firewalld` in `CentOs`

      1. 流程

         ```mermaid
         graph TD
         服务维护["服务维护(systemctrl):start, staus, stop, disable"]
         信息查看["信息查看(firewall-cmd --):version, state..."]
         基本配置["基本配置:-add-interface, --add-port"]
         更新["更新: --reload"]
         服务维护 --> 信息查看
         信息查看 --> 基本配置
         基本配置 --> 更新
         ```

         2. 基本概念：
            1. `Zone`: 一套规则集， 规定interface在Zone里面开方那些端口
            2. 