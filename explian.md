## ORM 是什么？

### ORM = Object-Relational Mapping（对象-关系映射）

__让你用 操作对象 的方式，来 操作数据库，不用写 SQL 语句。__

1. 类 ↔ 表（Model 模型）

| Python | 数据库 |
|:--:|:--:|
| `class Book` | `CREATE TABLE books` |
| 类属性 | 表的列 |
| 类的实例 | 表的一行数据 |

```
class Book(Base):           # = 数据库表 "books"
    __tablename__ = "books"
    
    id = mapped_column(...)     # = 列 "id"
    title = mapped_column(...)  # = 列 "title"
    
book = Book(title="三体")   # = INSERT 一行数据
```

## Depends 是什么？

### 一句话：FastAPI 帮你自动调用函数，把结果注入到你的路由参数中，并且自动管理资源的生命周期。它是 FastAPI 实现依赖注入的核心机制，让代码更干净、更可复用、更易测试

## select(Book)  

= SQLAlchemy 的查询构造器
相当于 SQL： SELECT * FROM books

## .scalars()

提取第一列的 ORM 对象，去掉包装

```
result 原始数据:
    Row(id=1, title="三体", author="刘慈欣", Book对象)
    Row(id=2, title="流浪地球", author="刘慈欣", Book对象)
    
result.scalars():
    Book(id=1, title="三体", author="刘慈欣")
    Book(id=2, title="流浪地球", author="刘慈欣")

```

## .all()

所有结果变成 Python 列表,全部返回

## git

git的提交方式有很多，例如直接用vscode自带的源码管理就能提交上去，还是写一下命令吧，免得自己又忘
```
git init    #创git环境
git add .   #导文件
git commit -m "text"
git remote add origin https://github.com/username/project.git#push远程仓库
git branch -M main
git push -u origin main

```

## 创建虚拟环境

先说venv环境的创建吧，简单。

```
python -m venv venv     # 在项目后端根目录创建
.venv/bin/activate
pip install -r requirements.txt
deactivate
```

## 接口的实现？
1. 定义模块化路由（用规范接口文档，可以上传类似云雀等平台）
2. 定义模型类（数据库表）
3. 创建数据库连接，封装数据库（day2接下来要实现的功能，移植database中的orm操作）
4. 在router中调用crud封装好的方法来实现增删改查

### 模块化路由
比较简单，就是建立一个api接口

### 定义模型类
基类继承declarative_base()  
数据库表模型，继承基类

## 我目前希望后期弄懂的功能？

### day1

**前端中之前老师说的路由守卫是什么？怎么做？**  
**后端和前端怎样联动好跑通?(只有分开开发的经验)**  
**后端使用postman测试接口，如何使用？**  
慢慢来，不急，今天先把自己路由跑通再说
---