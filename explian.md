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
