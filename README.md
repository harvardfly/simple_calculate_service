# 基于python3和grpc的简单计算服务

## 应用grpc的四种接口类型
```
Unary RPC （一元RPC）：计算服务(加减乘除)
Server Streaming RPC （ 服务器流式RPC）：通过学科获取对应的题型
Client Streaming RPC （ 客户端流式RPC）：累加服务
Bidirectional Streaming RPC （双向流式RPC）：竞猜服务
```

## 各组件及其版本
```
Protocol Buffers：proto3
zookeeper：3.4.13
grpcio-tools：1.18.0
kazoo：2.6.0
ORM：peewee
反向代理：nginx
部署：Docker
```

# 操作步骤

### 编译生成代码
```
$ cd protos
$ python3 -m grpc_tools.protoc -I. --python_out=.. --grpc_python_out=.. simple_calculate.proto
```

### 配置settings_local
```
$ cd simple_calculate_service
$ cp settings_local.py.example settings_local.py
```

### server image
```
$ cd simple_calculate_service
$ sudo docker build -t simple_calculate -f Dockerfile .
```

### nginx image
```
$ cd simple_calculate_service
$ sudo docker build -t simple_calculate_nginx -f common/nginx/Dockerfile .
```

### 部署
```
$ cp docker-compose.yml.example docker-compose.yml

$ sudo docker-compose up -d
```
