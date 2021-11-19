# pixiv图片小说批下载

随手写的一个pixiv批下载工具，可批下载用户收藏或创作的图片、小说，通过数据库对下载内容进行匹配和记录（默认使用文件数据库SQLite），从而避免相同文件重复下载，主要用以对个人收藏进行管理

Python版本：3.7.9

**目前没有实现自动登录，需要通过cookie登录**

**建议在虚拟环境下运行本项目**

## 项目结构

```
pixiv_download
│
│   main.py            -- 主函数
|   gui.py             -- 可视化客户端程序
|   check.py           -- 核验数据库记录与文件系统是否匹配
|   migrate.py         -- 用以不同数据库之间记录迁移
|   config.json        -- 配置文件，会覆盖项目中默认的配置信息
|   create.sql         -- 数据库结构，仅供参考
|   requirements.txt   -- python依赖包
|
└───config             -- 管理配置文件
|   |   ...
│
└───database           -- 数据库类，提供不同类型数据库的接口
│   │   ...
|
└───spider             -- 爬虫
│   │   ...
|
└───component          -- 可视化组件
│   │   ...
|
└───tool               -- 工具
│   │   ...
|
└───logs               -- 默认日志目录
|   |   ...
|
└───downloaded         -- 默认下载文件存储位置
    |   ...
```

## 快速运行

1. 在项目根目录下新建`config.json`文件，复制如下内容到其中并保存
   ```json
   {
     "spider": {
       "cookie": ""
     }
   }
   ```
   
2. 注册[pixiv](https://www.pixiv.net/)账号并登录

3. 按`f12`打开开发者模式，点击网络（Network），找到`https://www.pixiv.net/`这个Get请求并点击，点右侧的标头（Headers），复制下面请求头（Request Headers）栏中的Cookie项到`config.json`中的`cookie`项中

   ***注意：在Chrome和Edge中直接复制即可，在Firefox中需要先点击右上角的原始再复制才能复制到完整的cookie信息***

4. 安装必须的依赖包
   ```shell
   pip install -r requirements.txt
   ```

5. 可下载的内容包括用户创作的插画、用户创作的小说、用户收藏的插画、用户收藏的小说四种，打开对应页面然后复制网址即可，四种类型网址分别形如：

   ```
   UID用户创作的插画：https://www.pixiv.net/users/UID/illustrations
   UID用户创作的小说：https://www.pixiv.net/users/UID/novels
   UID用户收藏的插画：https://www.pixiv.net/users/UID/bookmarks/artworks
   UID用户收藏的小说：https://www.pixiv.net/users/UID/bookmarks/novels
   ```

   两种方法批下载：

   * 方法1：通过命令行给`main.py`传递参数：

     ```shell
     python main.py url
     ```

   * 方法2：在`config.json`的`根`项中加入如下项：

     ```json
     "__main__": {
      "main": {
        "download_list": [
          "url1",
          "url2"
        ]
      }
     }
     ```

     然后执行：

     ```shell
     python main.py
     ```

## 使用MySQL数据库存储记录

**注意：因为pixiv存在4字节utf8编码，因此MySQL的默认编码格式应为`utf8mb4`，如果不是，则需要在MySQL中手动创建`utf8mb4`编码的库并填写到下面的配置项中。**

默认使用sqlite存储文件记录，可以改用MySQL存储，步骤如下：

1. 确保本地MySQL服务运行中

2. 在`config.json`的`spider`项中加入如下项：

   ```json
   "database": {
     "type": "mysql",
     "mysql": {
       "host": "localhost",
       "port": 3306,
       "user": "",
       "password": "",
       "db": ""
     }
   }
   ```

   填充user(用户名)、password(密码)、db(数据库名)三项

## 数据库记录迁移

当切换数据库存储文件记录时，可以运行`migrate.py`进行迁移：

1. 在`config.json`的`__main__`项中加入如下项：

   ```json
   "migrate": {
     "source": {
       "type": "mysql",
       "mysql": {
         "host": "localhost",
         "port": 3306,
         "user": "",
         "password": "",
         "db": ""
       }
     },
     "target": {
       "type": "sqlite",
       "sqlite": {
         "db": ""
       }
     }
   }
   ```

   `source`为源数据库，`target`为目标数据库，目前两者只能是mysql或者sqlite，根据数据库信息填写对应项，若用到了MySQL需要确保本地MySQL服务运行中

2. 执行：

   ```shell
   python migrate.py
   ```

## 其他配置修改

* 方法一：查看`config/config.py`，在`config.json`中更改会覆盖`config/config.py`中的默认项
  
* 方法二：执行：

   ```shell
   python gui.py
   ```

   在设置选项中进行修改

## 进度计划

- [x] 确定并更新可视化客户端界面风格
- [ ] 补充可视化客户端的日志模块
- [x] 将所有可配置项加入设置功能中
- [x] 在可视化客户端账户功能
- [ ] 在可视化客户端增加下载管理功能
- [ ] 在可视化客户端增加阅览功能
- [ ] Linux与Mac平台的适配性

## 目前存在的问题

- [x] 把头像改成button的icon，同步side的账户按钮和里面的图形一致
- [x] 账户状态改变时通知父亲
- [ ] 用户界面打开时会出现一个小窗口闪动一下
- [ ] 未对用户界面输入的前后空白符号做处理
- [ ] check.py main.py migrate.py重写
- [ ] 当account保存成功时，setting将不能正确判断状态是否变化，此时保存将覆盖account所作的保存
- [ ] setting模块应该是逐项修改，而不是全部覆盖
- [x] setting日志选项提示必须重启才能生效
- [x] 当spider初始化时应该将config存储于对象变量中，此时config更改对于已经创建的对象无影响，但是对于以后创建的对象有影响
- [x] 定时器失效：多线程通知主线程开关定时器
- [x] 当修改时recheck应该不可用：可用应该也是可以的
- [x] cookie输入框换成多行的：还是单行更好一些，因为请求头不能有回车
- [x] QObject::setParent: Cannot set parent, new parent is in a different thread
- [x] account切换提示
- [ ] 关闭时若account依旧在验证应该将其杀死
- [ ] 查询时允许用户修改
