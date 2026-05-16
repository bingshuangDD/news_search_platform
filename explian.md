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

### sqlalchemy中的ORM
| 部分      | 含义    |
| -------------------------- | ---------------------------------- |
| `select(...)`    | SQLAlchemy 的查询构造器                  |
| `func.count(news.News.id)` | SQL 的 `COUNT(news.id)`，计数函数        |
| `.where(...)`    | SQL 的 `WHERE category_id = ?` 过滤条件 |

### 抛出异常为什么用HTTPexception不用return code 404?
结论：可以用，但是最好是方法是抛出HTTPException
为什么 HTTPException 更好
1. HTTP 语义正确  
404 应该体现在 HTTP 状态码 上，不是响应体里的一个字段  
客户端可以通过  response.status_code != 200  直接判断失败，无需解析 JSON  
2. 文档自动生成
Swagger/OpenAPI 会显示 404 响应模型  
return方式文档里看不到错误情况  
只有一种情况使用：就是公司强制要求抛出的错误需为code 404。

###为什么 and 在 where() 里不工作？

```
# ❌ 错误：Python 会先算 news.News.id != news_id
# 结果是 True/False，然后 SQLAlchemy 拿到的是：
# where(False and <Column对象>) → 变成 where(False)，完全不是你要的 SQL
.where(news.News.id != news_id and news.News.category_id == categoryid)

# ✅ 正确：逗号分隔，SQLAlchemy 自动转成 SQL 的 AND
.where(
    news.News.id != news_id,
    news.News.category_id == categoryid
)

# ✅ 也正确：显式用 and_()
.where(
    and_(news.News.id != news_id, news.News.category_id == categoryid)
)

```
### 工程化思维的构建
在news.py中我一直用的return方法是return一整个json包，其中在router函数中所占篇幅过于庞大。那么有没有一种可能我可以将他封装起来返回呢？  
**这就是工程化思维所要做的事情**

| 维度         | 松散 JSON 响应                 | Pydantic 工程化响应                |
| :--------- | :------------------------- | :---------------------------- |
| **类型安全**   | ❌ 无，字段名/类型错误运行时才暴露         | ✅ 构造时自动校验，IDE 实时报错            |
| **IDE 支持** | ❌ 无补全、无跳转、无重构              | ✅ 自动补全、点击跳转、安全重构              |
| **接口文档**   | ❌ FastAPI 显示 `object`，前端靠猜 | ✅ Swagger 自动生成完整字段结构          |
| **数据校验**   | ❌ 运行时才发现序列化失败              | ✅ `model_validate` 显式转换，失败即报错 |
| **维护成本**   | ❌ 改字段需全局搜索，易遗漏             | ✅ 改模型一处，类型错误全局可见              |
| **开发效率**   | ✅ 临时脚本/原型快速                | ❌ 需预先定义模型类                    |

不算难，但是这样写起来确实复杂。(例如user路由中的register函数)我需要先从user中拿到database响应回来的orm对象，然后用这个对象先解包出一个data的大类，然后再里面嵌套两个小类（可选填信息类+必填信息类），在通过工具里面的成功响应函数去返回一个json包。）


## 我目前希望后期弄懂的功能？

### week1

**前端中之前老师说的路由守卫是什么？怎么做？**  
**后端和前端怎样联动好跑通?(只有分开开发的经验)**  
**后端使用postman测试接口，如何使用？**  
慢慢来，不急，先把自己路由跑通再说
---