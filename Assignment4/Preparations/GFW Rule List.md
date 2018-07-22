# GFW Rule List

[Syntax](https://github.com/gfwlist/gfwlist/wiki/Syntax)

1. Pre handler:

   先过滤一遍

   * 去除所有注释

   * 去除所有`http://`与`https://`(简化操作).

   * 将白名单和黑名单分开为white_list, black_list

   * 加上头部， 表明已经预处理完毕

     ```python
     with open("gfwlist.txt", "r") as f:
         if f.readline() == "PRE_HANDLED":
             logger.info("Has yet been pre handled")
             f.close()
             return
         # Open white_list, black_list:
         white_f = open("white_list", "w")
         black_f = open("black_list", "w")
         
         for line in f.readlines():
             # Ignore
             if line[0] == "!":
                 continue
             elif line[1] == "@":
                 white_f.write(line)
             else:
                 black_f.write(line)
     	# Write header to gfwlist
         f.seek(0)
         old = f.read()
         f.seek(0)
         f.write("PRE_HANDLED")
         f.write(old)
     
     ```

     

2. Pre handler for `whitelist`

3. 