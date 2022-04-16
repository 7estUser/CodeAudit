## 基础类库
### Method 	项目中的所有方法(静)
- method.hasName()				限定方法名称
- method.getName() 				获取当前方法的名称
- method.getDeclaringType()		获取方法变量的类型
- method.getAnAnnotation()		获取应用于此元素的注解
	.getValue(string name)		获取具有指定“name”的注释元素的值。
- method.getDeclaringType()		获取声明此成员的类	🚩

### MethodAccess 	项目中的所有方法调用(动)
- MethodAccess.getArgument(0) 	获取方法的第一个参数
- MethodAccess.getMethod()		获取调用指定方法的所在方法 = Method
- MethodAccess.getCaller		方法调用所在的方法，换句话说是哪个方法体中调用的

### Expr 	表达式(expression 各种类、方法、对象、参数等等，类似于java中的Object)
- Expr.getAChildExpr			返回指定的expression的子expression

### Parameter 	项目中的所有参数

### ReturnStmt 	所有return 🚩
- ReturnStmt.getResult()		result整体
	.getAChildExpr()			result中的对象,`getAChildExpr*()`:result中的方法和对象

### Stmt 	声明(statements)

## 模块
### DataFlow
- DataFlow::PathNode   
带有调用上下文（接收器除外）、访问路径和配置的Node。仅生成那些可以从源访问的PathNode。
- DataFlow::Node
一个元素，在数据流图中被视为节点。要么是表达式、参数，要么是隐式varargs数组的创建。s

## Map
- MapType			用来表示Map类型 🚩
- MapMethod			Map类型的对象所有的方法
- MapMutator		Map类型里面赋值相关的方法
- MapQueryMethod	Map类型里面查询相关的方法
- MapSizeMethod		Map类型的Size方法
- MapMutation		查看所有调用了Map对象任意方法的表达式
- MapPutCall		查看所有调用了Map对象put方法的表达式 🚩

事例：return语句中调用了Map类型的变量mapVar，获取mapVal所有value的类型
```sql
import java
import semmle.code.java.Maps

from ReturnStmt returnStmt,MapType mapType
where 
	returnStmt.getResult().getAChildExpr*().getType() = mapType
select mapType.getValueType()
```
