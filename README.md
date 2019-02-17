# 基于python3和grpc的简单计算服务，使用ZooKeeper作为服务协调，nginx反向代理
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
