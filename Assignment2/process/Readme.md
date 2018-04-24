# updatedb 想法

## 目录遍历

> 参考 [Efficiently Traverse Directory Tree with opendir(), readdir() and closedir()](https://stackoverflow.com/questions/2312110/efficiently-traverse-directory-tree-with-opendir-readdir-and-closedir)

>  使用`opendir() ` `readdir()` 族进行文档遍历, 采用将子目录放入优先队列中循环遍历来代替递归， 同时优先队列能让文件按名字排序

1. 进入`a`文件夹， 将`a`文件夹的`meta`作为值与`root_depth`值 存入数据库中

   `root_depth` : 遍历深度

   1. `meta` 包含完整文件路径， 时间戳， 目录大小等特征(等下去参考一下mlocate.db)

2. 遍历`a`

3. 遍历过程中， 若遇到`plain text`文件， 使用`pirority`函数获取优先值`pri_val`， 将该文件的`inode` 与 `pri`放到一个键值字典中(key: `inode`,  val:`pri_val`)

   1. `priority()` 返回 以文件名前三个的字母的ASCII码补全三位数(首位加0)组成的一个优先数， 如absolute 优先数为 097 098 115
   2. 对于多线程程序， 现在已经开始对文件自身建立索引

4. 遍历过程中， 若遇到`DIR`目录， 则将目录按`priority()`的返回值放入一个优先队列中

   1. 上述与此例的`priority`都是为了让文件名按大小排序

5. 遍历完a后， `root_depth` + 1， father_path设置为 a/

   1. 即遍历深度加1, 方便统计
   2. 同样， 与a相同， 只是path要加一个father_path

## 建立索引

### 1 原理

1. 在数据库A中， 
2. 在数据库`node_id -- pri_val`中， 取出优先级最大的node_id， 对node_id对应的文件进行如下遍历
   1. 在对应的`plain text`中， 对每一个满足正则表达式的单词， 建立一个`key-value`记录， `key: word`, `value` 是一个`vector`， 每一个`vector`的	元素是一个`node_id`, 	`node_id`代表新的`key`对应着另一个数据库， 其中 该数据库的 `key`是`node_id`