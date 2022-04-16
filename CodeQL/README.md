# 使用操作

## 环境配置

- 安装引擎：https://github.com/github/codeql-cli-binaries/releases
- 添加环境变量：`export PATH=/Home/CodeQL/codeql:$PATH`,terminal输入`codeql`检查环境变量是否设置成功
- 安装sdk：https://github.com/Semmle/ql
- VSCode安装插件：codeql
- 插件中配置codeql引擎路径
![](https://github.com/user-error-404/CodeAudit/blob/main/CodeQL/img/vccode配置codeql引擎.jpg)

## 工作区添加CodeQL标准库

VSCode - 文件 - 将文件夹加入工作区 - 选择在ql标准库(SDK)的文件夹。 

![](https://github.com/user-error-404/CodeAudit/blob/main/CodeQL/img/添加ql到工作区.jpg) 

## 生成Database：
```bash
codeql database create /数据生成路径
--language="java"  							#当前程序语言
--command="mvn clean install --file pom.xml" 	#java是编译，所以需要进行先编译，python和php不需要
--source-root=/项目路径						#默认是当前路径
```

## 导入Database：

选择上一步生成的Database目录：
VSCode -> QL -> DATABASE -> From a folder 

## 编写QL查询：

创建文件：`qlpack.yml` 和 `.ql` 后缀的文件  
qlpack.yml为配置文件，.ql 文件用来写查询语句
> ⚠️ qlpack.yml和.ql文件必须在同一个文件夹内
将该文件夹添加到VSCode工作区

qlpack.yml:
```xml
name: example-query
version: 0.0.0
libraryPathDependencies: codeql-java
```
- name：ql包名称，打开多个ql包时name需要唯一。
- version：ql包版本号。
- libraryPathDependencies：QL包的依赖  
  
.ql 文件中编写QL语句，右键 CodeQL:Run Query，运行  

> QL语法格式：
```java
import codeType(java)
class var{}
from [datatype] var
where condition(var = something)
select var
```

# 结构函数语法

## 谓词(函数)
```java
predicate isTaintedString(parameType parame){
   exists ( | )
}
```
predicate 表示当前方法没有返回  
exists子查询，是CodeQL谓词语法里非常常见的语法结构，它根据内部的子查询返回true or false，来决定筛选出哪些数据。  
格式：exists(Obj obj| somthing)  

## 三元组：source、sink、sanitizer
- source 是指漏洞污染链条的输入点。比如获取http请求的参数部分，就是非常明显的Source。
- sink 是指漏洞污染链条的执行点，比如SQL注入漏洞，最终执行SQL语句的函数就是sink。
- sanitizer 又叫净化函数，是指在整个的漏洞链条当中，如果存在一个方法阻断了整个传递链，那么这个方法就叫sanitizer。

‼️‼️‼️  
设置source：  
	`override predicate isSource(DataFlow::Node src){ src instanceof RemoteFlowSource }`  
	⚠️重点是，在审计的系统中，source（入口点）是什么，是哪个  
	# src instanceof RemoteFlowSource 表示src 必须是 RemoteFlowSource类型  
	# RemoteFlowSource，SDK自带的规则，里面官方提供很非常全的source定义，常用到的Springboot的Source就已经涵盖了。  
设置sink:  
	`override predicate isSink(DataFlow::Node sink){ sink.asExpr() = MethodAccess.getArgument(0)}`  
	`sink.asExpr() = `  
	# 将MethodAccess方法的第一个参数设置为sink  
设置sanitizer：  
	`override predicate isSanitizer(DataFlow::Node node){}`  
	# 解决误报
设置漏报
     `override predicate isAdditionalTaintStep(DataFlow::Node node1, DataFlow::Node node2) {}`
     将node1和node2按照规则链接  

⚠️isSource、isSink、isSanitizer都是 TaintTracking::Configuration 中的方法  
‼️‼️‼️ 
## Flow数据流

`config.hasFlowPath(source, sink)`  
CodeQL引擎自动判断是否首尾是否连通  
设置好`source`和`sink`，如果可以走通，中间没有阻断，就表示存在漏洞。  
config 是继承 extends 父类 `TaintTracking::Configuration` 的对象  
数据流分析的通用类，提供很多数据流分析相关的方法，比如isSource(定义source)，isSink(定义sink)  

## 解决误报
```java
override predicate isSanitizer(DataFlow::Node node) {
node.getType() instanceof PrimitiveType or
node.getType() instanceof BoxedType or
node.getType() instanceof NumberType or
exists(ParameterizedType pt | node.getType()=pt and pt.getTypeArgument(0) instanceof NumberType)
}
```
表示如果当前节点是上面提到的数据类型，那么此污染链将被净化阻断，漏洞将不存在。  
`ParameterizedType` : 表示一个有参数的类型  

## 解决漏报
```override predicate isAdditionalTaintStep(DataFlow::Node node1, DataFlow::Node node2) {}```  
将一个可控节点A强制(连通)传递给另外一个节点B，那么节点B也就成了可控节点。  

## 实例代码
```java
/**
 * @id java/examples/vuldemo
 * @name Sql-Injection
 * @description Sql-Injection
 * @kind path-problem
 * @problem.severity warning
 */
import java
import semmle.code.java.dataflow.FlowSources
import semmle.code.java.security.QueryInjection
import DataFlow::PathGraph

predicate isTaintedString(Expr expSrc, Expr expDest) {
     exists(Method method, MethodAccess call, MethodAccess call1 | 
          expSrc = call1.getArgument(0) and
          expDest=call and
          call.getMethod() = method and 
          method.hasName("get") and
          method.getDeclaringType().toString() = "Optional<String>" and 
          call1.getArgument(0).getType().toString() = "Optional<String>" )
}

class VulConfig extends TaintTracking::Configuration{
     VulConfig(){this = "SqllnjectionConfig"}

override predicate isSource(DataFlow::Node src){ 
     src instanceof RemoteFlowSource
}

override predicate isSanitizer(DataFlow::Node node) {
     node.getType() instanceof PrimitiveType or
     node.getType() instanceof BoxedType or
     node.getType() instanceof NumberType or
     exists(ParameterizedType pt | node.getType()=pt and pt.getTypeArgument(0) instanceof NumberType)
     }

override predicate isSink(DataFlow::Node sink){
     exists(Method method,MethodAccess call | 
          method.hasName("query") and 
          call.getMethod() = method and
          sink.asExpr() = call.getArgument(0) )
     }

override predicate isAdditionalTaintStep(DataFlow::Node node1, DataFlow::Node node2) {
     isTaintedString(node1.asExpr(), node2.asExpr())
     }

}

from VulConfig config,DataFlow::PathNode source,DataFlow::PathNode sink
where config.hasFlowPath(source, sink)
select source.getNode(),source,sink,"source"
```

## 其他
查询语句中的/***/注释中的相关信息在生成测试报告的时会被写入到审计报告中  
@id @name @description @kind @problem.severity  

引擎：CodeQl  
SDK：ql

AST语法树关键字解析	https://www.jianshu.com/p/d21c16b8953e