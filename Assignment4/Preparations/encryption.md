## RC4

​	流密码



1. `MD5`长度: 128bits

2. Keywords:

   1. 明文 R: 

      * 待加密的数据集

   2. 密钥流 C： 

      * 加密密文的直接密钥

      * 产生密钥流

        ```python
        i = 0, j = 0
        for r in range(len(R)): # Iter data R
            i = (i+1) % 256
            j = (j+S[i]) % 256
            S[i], S[j] = S[j], S[i]
            t = (S[i] + S[j]) % 256
            R[r] = S[t]
        ```

        

        

   3. 状态向量 S：

      * 为0-255的排列组合（长度256）

      * 初始化S

        ```python
        # Init 顺序排列
        S = [i for i in range(255)]
        ```

      * 初始排列S

        ```python
        # 乱序排列
        for i in range(255):
            j = (j + S[i] + T[i]) % 256
            S[i], S[j] = S[j], S[i]
        ```

        

   4. 临时向量 T：

      * 把密钥K轮换复制给T(长度256)

        ```python
        T[i] = K[i % len(K)]
        ```

        

   5. 密钥K：

      * 用户的密钥， 可使用md5摘要得到128bits长度密钥

        ```python
        md5 = hashlib.md5()
        md5.update(user_key)
        K = md5.digest()  # Return bytes
        ```

3. 流程：

   1. 生成密钥流
      1. 思想:
         * 不定长密钥生成与密文长度一样的密钥： 通过mod+复制进行
         * 生成的密钥有混淆：通过S的排列组合进行