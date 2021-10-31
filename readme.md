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
       "your_uid": "",
       "cookie": ""
     }
   }
   ```
   
2. 注册[pixiv](https://www.pixiv.net/)账号并登录

3. 打开个人主页，此时网址应该形如`https://www.pixiv.net/users/账号ID`，从网址中复制`账号ID`到`config.json`中的`your_uid`项中

4. 按`f12`打开开发者模式，点击网络（Network），找到`https://www.pixiv.net/`这个Get请求并点击，点右侧的标头（Headers），复制下面请求头（Request Headers）栏中的Cookie项到`config.json`中的`cookie`项中

   ***注意：在Chrome和Edge中直接复制即可，在Firefox中需要先点击右上角的原始再复制才能复制到完整的cookie信息***

5. 安装必须的依赖包
   ```shell
   pip install -r requirements.txt
   ```

6. 可下载的内容包括用户创作的插画、用户创作的小说、用户收藏的插画、用户收藏的小说四种，打开对应页面然后复制网址即可，四种类型网址分别形如：

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

   填入数据库用户、密码以及数据库名，若数据库不存在默认会创建

## 数据库记录迁移

1. 在`config.json`的`__main__`项中加入如下项：

   ```json
   "migrate": {
     "source": {
       "type": "mysql",
       "params": {
         "host": "localhost",
         "port": 3306,
         "user": "",
         "password": "",
         "db": ""
       }
     },
     "target": {
       "type": "sqlite",
       "params": {
         "db": ""
       }
     }
   }
   ```

   `source`为源数据库，`target`为目标数据库，目前两者只能是MySQL或者SQLite，根据数据库信息填写对应项，若目标数据库名不存在默认会创建，若用到了MySQL需要确保本地MySQL服务运行中

2. 执行：

   ```shell
   python migrate.py
   ```

## 其他配置修改

参考`config/config.py`，在`config.json`中更改会覆盖`config/config.py`中的默认项

## 进度计划

- [x] 确定并更新可视化客户端界面风格
- [ ] 补充可视化客户端的日志模块
- [ ] 将所有可配置项加入设置功能中
- [ ] 在可视化客户端增加下载管理功能
- [ ] 在可视化客户端增加阅览功能
- [ ] Linux与Mac平台的适配性