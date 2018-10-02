# 0 安装与初始化


## 0.1 创建虚拟环境

创建虚拟环境
``` python
conda create -n superset python=3.6
```

启动虚拟环境
``` python
activate superset
```


## 0.2 安装

使用豆瓣源安装
``` python
pip install superset -i https://pypi.douban.com/simple 
```
这里遇到了一个坑，某个依赖包没有被正确的安装，当时随手就解决了，没有记录下来。如果遇到同样的问题，就把报错信息复制出来，问问神奇的 [stackoverflow](https://stackoverflow.com/) 吧！


## 0.3 初始化

初始化的官方步骤如下：
``` python
# 创建管理员账号
fabmanager create-admin --app superset 

# 初始化数据库
superset db upgrade

# 载入案例数据
superset load_examples

# 初始化角色和权限
superset init

# 启动服务，端口号 8088，使用 -p 更改端口号
superset runserver
```

在命令行中直接运行 `superset`， 会提示“不是内部或外部命令”。要解决这个问题，可以直接通过 `cd` 命令进入 superset 安装目录（ E:\Anaconda3\envs\superset\Lib\site-packages\superset\bin ）。然后运行如下命令：
``` python
python superset db upgrade
python superset load_examples
python superset init
python superset runserver
```
这里直接运行 `python superset runserver` 会出错，需要一些小改动。


## 0.4 使用 waitress 运行

执行命令 `python superset runserver`,出错。原因是 superset 使用 gunicorn 作为应用程序服务器,而 gunicorn 不支持 windows。命令行中添加 `-d`,使用 development web server 运行。最终运行命令为：
``` python
python superset runserver -d
```

但是这种部署方式,官方不建议在生产环境中使用。在 superset 的 [issues 922](https://github.com/airbnb/superset/issues/922)，有人提供了一个分支,使用 waitress，步骤如下：
``` python
pip install waitress
```

改写前的 `debug_run()` 函数：
``` python
def debug_run(app, port, use_reloader):

    app.run(
        host='0.0.0.0',
        port=int(port),
        threaded=True,
        debug=True,
        use_reloader=use_reloader)
```

改写后的 `debug_run()` 函数：
``` python
def debug_run(app, port, use_reloader):
    from waitress import serve #使用 waitress 解决 gunicorn 不支持 windows 问题

    return serve(
        app,
        host='0.0.0.0',
        port=int(port))
```

运行 superset:
``` python
python superset runserver -d -p 8079
```

在浏览器输入 `http://localhost:8079` 访问


# 0.5 功能结构

- 安全
    - 用户列表
    - 角色列表
    - 用户统计
    - 基本权限
    - 视图/菜单
    - 视图/菜单权限
    - 操作日志
- 管理
    - 导入 dashboard
    - CSS 模板
    - 查询
    - 注解层
    - 注解
- 数据源
    - 数据库
    - CSV
    - 数据表
    - Druid 集群
    - Druid 数据源
    - 扫描新的数据源
    - 刷新 Druid 元数据
- 图表
- dashboard
- SQL 工具箱
    - SQL 编辑器
    - 查询搜索
    - 已保存查询


# 1 数据源