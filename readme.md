# pixiv图片小说批下载

一个pixiv批下载工具，可批下载用户收藏或创作的图片、小说，通过数据库对下载内容进行匹配和记录（默认使用文件数据库SQLite），从而避免相同文件重复下载，主要用以对个人收藏进行管理

* **目前没有实现账号密码登录，需要通过cookie登录**

* **Python版本：3.7.9**

## 项目结构

```
pixiv_download
│
│   main.py            -- 命令行运行
|   client.py          -- 可视化客户端运行
|   check.py           -- 核验数据库记录与文件系统是否匹配
|   migrate.py         -- 用以不同数据库之间记录迁移
|   config.json        -- 配置文件，会覆盖项目中默认的配置信息
|   create.sql         -- 数据库结构，无需使用，供参考
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
└───gui                -- 可视化组件
│   │   ...
|
└───icons              -- 图标
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

## 配置环境

1. 创建虚拟环境并进入

2. 安装依赖包

   ```shell
   pip install -r requirements.txt
   ```

## 客户端运行

1. 打开客户端

   > 或在建立的虚拟环境下执行
   >
   > ```shell
   > python client.py
   > ```

   ![pixiv_download/1.png at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/1.png)

2. 注册[pixiv](https://www.pixiv.net/)账号并登录

3. 按`f12`打开开发者模式，点击网络（Network），找到`https://www.pixiv.net/`这个Get请求并点击，点右侧的标头（Headers），复制下面请求头（Request Headers）栏中的Cookie项

   ***注意：在Chrome和Edge中直接复制即可，在Firefox中需要先点击右上角的原始再复制才能复制到完整的cookie信息***

4. 将复制到的Cookie信息输入到客户端账户的Cookie位置并保存，等待查询结果为账户可用，若查询结果为账户不可用说明Cookie信息错误

   ![pixiv_download/2.png at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/2.png)

   ![pixiv_download/3.png at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/3.png)

5. 点击设置可以修改**文件存放位置**、**请求等待时间**、**数据库等配置**信息

   ![pixiv_download/4.png at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/4.png)

6. 点击下载后创建若干下载项，可自定义下载项名称、用户UID和类型，用户UID为用户主页网址中的数字部分，类型可选`bookmarks/artworks`、`bookmarks/novels`、`illustrations`和`novels`，分别对应用户收藏的插画、用户收藏的小说、用户创作的插画和用户创作的小说

   ![pixiv_download/5.jpg at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/5.jpg)

7. 选中若干个下载项后点击开始按钮，右边可以查看下载日志，点击可查看图片、小说、网址或打开文件所在位置，文件目标存储位置可见设置中的**文件存放位置**选项

   ![pixiv_download/6.jpg at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/6.jpg)

   ![pixiv_download/7.jpg at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/7.jpg)

## 命令行运行

1. 在项目根目录下新建`config.json`文件，复制如下内容到其中并保存
   
   > 若已运行过客户端，则会自动生成该文件，无需创建
   
   ```json
   {
     "spider": {
       "cookie": ""
     }
   }
   ```
   
2. 注册[pixiv](https://www.pixiv.net/)账号并登录

3. 复制Cookie到到`config.json`中的`cookie`项中，方法同上

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

2. 在设置中将数据库选择切换为mysql并配置user(用户名)、password(密码)、db(数据库名)三项

   ![pixiv_download/8.png at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/8.png)

2. 也可直接在`config.json`的`spider`项中配置MySQL并将`type`改为`mysql`

   ```json
   "database": {
     "mysql": {
       "db": "",
       "host": "localhost",
       "password": "",
       "port": "3306",
       "user": ""
     },
     "sqlite": {
       "db": "pixiv_download"
     },
     "type": "sqlite"
   }
   ```
   

## 数据库记录迁移

当切换数据库存储文件记录时，可以运行`migrate.py`进行迁移：

1. 在设置中配置源数据库和目标数据库

   ![pixiv_download/9.png at main · BINGOGO123/pixiv_download (github.com)](https://github.com/BINGOGO123/pixiv_download/blob/main/readme_file/9.png)
   
2. 也可在`config.json`的`__main__`项中加入如下项：

   ```json
   "migrate": {
     "output": "migrate.txt",
     "source": {
       "mysql": {
         "db": "",
         "host": "localhost",
         "password": "",
         "port": "3306",
         "user": ""
       },
       "sqlite": {
         "db": "pixiv_download"
       },
       "type": "mysql"
     },
     "target": {
       "mysql": {
         "db": "",
         "host": "localhost",
         "password": "",
         "port": "3306",
         "user": ""
       },
       "sqlite": {
         "db": "pixiv_download"
       },
       "type": "sqlite"
     }
   }
   ```

   `source`为源数据库，`target`为目标数据库，目前两者只能是mysql或者sqlite，根据数据库信息填写对应项，若用到了MySQL需要确保本地MySQL服务运行中

2. 执行：

   ```shell
   python migrate.py
   ```

## 其他配置修改

* 方法一：在客户端设置中更改对应项
* 方法二：查看`config/config.py`，在`config.json`中更改会覆盖`config/config.py`中的默认项

## 打包EXE文件

* 多文件打包

  ```shell
  pyinstaller -D -w -i ./icons/pixiv.ico client.py -y
  cp -Path ./icons -Destination ./dist/client/icons/ -Recurse
  ```

* 单文件打包

  ```shell
  pyinstaller -F -w -i icons/pixiv.ico client.py -y
  cp -Path ./icons -Destination ./dist/icons/ -Recurse
  ```


## 进度计划

- [x] 确定并更新可视化客户端界面风格
- [x] 补充可视化客户端的日志模块
- [x] 将所有可配置项加入设置功能中
- [x] 在可视化客户端账户功能
- [x] 在可视化客户端增加下载管理功能
- [ ] 在可视化客户端增加阅览功能
- [ ] Linux与Mac平台的适配性

## 问题修复

- [x] 把头像改成button的icon，同步side的账户按钮和里面的图形一致
- [x] 账户状态改变时通知父亲
- [ ] 用户界面打开时会出现一个小窗口闪动一下
- [x] 未对用户界面输入的前后空白符号做处理：cookie不以空白符号开头但是末尾可以跟空白符号，LineEdit则不能输入空白符号
- [ ] check.py main.py migrate.py重写
- [x] setting保存成功不弹出单独页面，改为在主页面中的某个位置显示：目前改为成功不提示，失败才提示
- [x] 当account保存成功时，setting将不能正确判断状态是否变化，此时保存将覆盖account所作的保存
- [x] setting模块应该是逐项修改，而不是全部覆盖
- [x] setting数字转换不合法问题：当timeout和request_max_count不合法时将使用代码中指定的参数
- [x] 当选择mysql数据库时提示mysql不存在：由于没有安装DBUtils导致
- [x] setting日志选项提示必须重启才能生效
- [x] 当spider初始化时应该将config存储于对象变量中，此时config更改对于已经创建的对象无影响，但是对于以后创建的对象有影响
- [x] 定时器失效：多线程通知主线程开关定时器
- [x] 当修改时recheck应该不可用：可用应该也是可以的
- [x] cookie输入框换成多行的：还是单行更好一些，因为请求头不能有回车
- [x] QObject::setParent: Cannot set parent, new parent is in a different thread
- [x] account切换提示
- [x] 动画线程因意外终止：保证不会异常关闭
- [x] 关闭时若account依旧在验证应该将其杀死
- [x] 查询时允许用户修改，即需要能终止正在进行的查询
- [x] account区分网络错误和账户错误
- [x] component改名
- [x] 当Account和Setting保存的时候写一下日志即可，其他有报错的地方写一下日志即可
- [x] 事件处理的过程中不会更新界面，导致`adjustSize`失效，解决方法：`QApplication.processEvents()`
- [x] 下载开始和结束标志
- [x] 序号编号方式更改
- [x] 新增记录后自动滑到底部
- [x] 新增删除记录按钮
- [x] 测试写入失败的情况测试
- [x] 右边显示数量少时高度问题
- [x] DownloadItem宽度以父亲宽度优先
- [x] 增加小说显示
- [x] 下载方式位置调整
- [x] 滚动条变宽
- [x] 下载方式增加多种颜色
- [x] mousePressEvent = None是否正确的问题
- [x] 尚未下载完成更改
- [x] 小说和图片下载记录背景颜色更改
- [x] 单次下载多个项目时每个项目的序号需要重置
- [x] 路径计算改为库方法
- [ ] 图片不显示：qt.gui.imageio: QImageIOHandler: Rejecting image as it exceeds the current allocation limit of 128 megabytes
- [ ] 打包后的exe点击打开图片后会弹出命令行一闪而过
- [x] pixiv.ico图标应该是圆形的，即圆之外应该是空像素
- [ ] 对于下载失败的项，增加一个重新下载按钮
- [ ] 手动终止下载后，下载项的状态可能依然是正在下载
- [x] 下载项不应该允许重复添加
- [x] 设置通知查看
- [x] 下载设置通知查看
- [x] 下载内容通知查看，需要备注路径，通知side修改，包括新建文件夹（根下载文件夹和子下载文件夹），通知content修改，新增图片
- [x] 设置修改文件存放位置之后，点击查看中的选项，报错
- [x] 下载存储路径非法时，查看界面的显示问题


## 小技巧记录

### 使`QScrollArea`中的`QWidget`与父亲等宽或等高（即与普通组件一样自适应父亲的高度和宽度）

```python
scroll = QScrollArea()
scroll.setWidgetResizable(True)
```