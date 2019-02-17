import sys
import time
import json
import grpc
import simple_calculate_pb2 as calculate_pb2
import simple_calculate_pb2_grpc as calculate_grpc
from kazoo.client import KazooClient
from concurrent import futures

from settings_local import settings_info


class SimpleRpcServerServicer(calculate_grpc.SimpleRpcServerServicer):
    """
    实现被调用方法的具体代码
    """

    def __init__(self):
        self.subject_question_type_db = {
            'Chinese': ['单选', '多选', '填空', '解答', '问答', '作文'],
            'Math': ['单选', '填空', '解答'],
            'English': ['单选', '填空', '作文'],
            'Physics': ['单选', '多选', '填空', '解答'],
            'Chemistry': ['单选', '多选', '填空', '解答'],
            'Biology': ['单选', '多选', '填空', '解答'],
            'History': ['单选', '多选', '填空', '解答', '问答']
        }
        self.answers = list(range(10))

    def Calculate(self, request, context):
        """
        计算服务  加减乘除
        Unary RPC 最简单的RPC类型，客户端发送单个请求并返回单个响应
        :param request:
        :param context:
        :return:
        """
        if request.op == calculate_pb2.Work.ADD:
            result = request.num1 + request.num2
            return calculate_pb2.Result(val=result)
        elif request.op == calculate_pb2.Work.SUBTRACT:
            result = request.num1 - request.num2
            return calculate_pb2.Result(val=result)
        elif request.op == calculate_pb2.Work.MULTIPLY:
            result = request.num1 * request.num2
            return calculate_pb2.Result(val=result)
        elif request.op == calculate_pb2.Work.DIVIDE:
            if request.num2 == 0:
                # 通过设置响应状态码和描述字符串来达到抛出异常的目的
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("分母不能为0")
                return calculate_pb2.Result()
            result = request.num1 // request.num2
            return calculate_pb2.Result(val=result)
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('invalid operation')
            return calculate_pb2.Result()

    def GetSubjectQuestionTypes(self, request, context):
        """
        服务器流式RPC调用 根据subject获取question_types
        :param request:
        :param context:
        :return:
        """
        subject = request.name
        question_types = self.subject_question_type_db.get(subject)
        for question_type in question_types:
            yield calculate_pb2.QuestionType(name=question_type)

    def Accumulate(self, request_iterator, context):
        """
        客户端流式RPC调用  客户端发送多个请求，服务端累计返回
        遍历迭代器 执行累加操作
        :param request_iterator:
        :param context:
        :return:
        """
        sum = 0
        for num in request_iterator:
            sum += num.val

        return calculate_pb2.Sum(val=sum)

    def GuessNumber(self, request_iterator, context):
        """
        客户端和服务端双向流式RPC调用
        客户端向服务端发送多个数据 如果服务端有认可的则响应
        :param request_iterator:
        :param context:
        :return:
        """
        for num in request_iterator:
            if num.val in self.answers:
                yield calculate_pb2.Answer(
                    val=num.val, desc='grate!'
                )


def register_zk(host, port):
    """
    注册到zookeeper
    """
    zk = KazooClient(hosts='{host}:{port}'.format(
        host=settings_info["zookeeper"]["host"],
        port=settings_info["zookeeper"]["port"])
    )
    zk.start()
    zk.ensure_path('/rpc_calc')  # 创建根节点
    value = json.dumps({'host': host, 'port': port})

    # 创建服务子节点
    zk.create(
        '/rpc_calc/calculate_server',
        value.encode(),
        ephemeral=True,
        sequence=True
    )


# 开启服务器，对外提供rpc调用
def server(host, port):

    # 创建服务器对象
    rpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 注册实现的服务方法到服务器对象中
    calculate_grpc.add_SimpleRpcServerServicer_to_server(
        SimpleRpcServerServicer(), rpc_server
    )
    # 为服务器设置地址 开启监听地址'
    rpc_server.add_insecure_port('{}:{}'.format(host, port))

    # 开启服务 开始接收请求进行服务
    rpc_server.start()

    register_zk(host, port)

    # 关闭服务使用 ctrl+c 可以退出服务
    try:
        time.sleep(1000)
    except KeyboardInterrupt:
        rpc_server.stop(0)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage:python server.py [host] [port]")
        exit(1)
    host = sys.argv[1]
    port = sys.argv[2]
    server(host, port)
