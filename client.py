import random
import json
import grpc
import simple_calculate_pb2 as calculate_pb2
import simple_calculate_pb2_grpc as calculate_grpc
from kazoo.client import KazooClient

from settings_local import settings_info


def invoke_calculate(stub):
    """
    计算服务客户端
    Unary RPC
    :param stub:
    :return:
    """
    work = calculate_pb2.Work()
    work.num1 = 100
    work.num2 = 50

    work.op = calculate_pb2.Work.ADD
    result = stub.Calculate(work)
    print('100+50={}'.format(result.val))

    work.op = calculate_pb2.Work.SUBTRACT
    result = stub.Calculate(work)
    print('100-50={}'.format(result.val))

    work.op = calculate_pb2.Work.MULTIPLY
    result = stub.Calculate(work)
    print('100*50={}'.format(result.val))

    work.op = calculate_pb2.Work.DIVIDE
    result = stub.Calculate(work)
    print('100//50={}'.format(result.val))

    work.num2 = 0
    work.op = calculate_pb2.Work.DIVIDE
    try:
        result = stub.Calculate(work)
        print('100//0={}'.format(result.val))
    except grpc.RpcError as e:
        print(e)


def invoke_get_subject_question_types(stub):
    """
    根据学科获取题型
    Server Streaming RPC 服务器流式RPC  客户端发送，服务器响应多个
    :param stub:
    :return:
    """
    subject = calculate_pb2.Subject(name='Chinese')
    question_types = stub.GetSubjectQuestionTypes(subject)
    for question_type in question_types:
        print(question_type.name)


def invoke_accumulate(stub):
    """
    Client Steaming RPC 客户端流式RPC
    客户端向服务器发送请求流而不是单个请求,服务器发送回单个响应
    客户端发送多个数字，服务器累加后返回
    :param stub:
    :return:
    """

    def generate_delta():
        """
        服务端是遍历迭代器 则客户端是个生成器
        :return:
        """
        for _ in range(10):
            num = random.randint(1, 100)
            print(num)
            yield calculate_pb2.Delta(val=num)

    delta_iterator = generate_delta()
    sum = stub.Accumulate(delta_iterator)
    print('sum={}'.format(sum.val))


def invoke_guess_number(stub):
    """
    双向流式RPC 客户端和服务器可以按任何顺序独立的读写数据流
    服务器可以在收到所有的请求信息后再返回响应信息，
    或者收到一个请求信息返回一个响应信息，
    或者收到一些请求信息再返回一些请求信息
    猜数字 猜对才返回结果
    :param stub:
    :return:
    """

    def generate_num():
        for _ in range(500):
            import time
            time.sleep(0.2)
            num = random.randint(1, 20)
            print(num)
            yield calculate_pb2.Number(val=num)

    number_iterator = generate_num()
    answers = stub.GuessNumber(number_iterator)
    for answer in answers:
        print('{}: {}'.format(answer.desc, answer.val))


class DistributedChannel(object):
    def __init__(self):
        self._zk = KazooClient(hosts='{host}:{port}'.format(
            host=settings_info["zookeeper"]["host"],
            port=settings_info["zookeeper"]["port"])
        )
        self._zk.start()
        self._get_servers()

    def _get_servers(self, event=None):
        """
        从zookeeper获取服务器地址信息列表
        """
        servers = self._zk.get_children(
            '/rpc_calc', watch=self._get_servers
        )
        print(servers)
        self._servers = []
        for server in servers:
            data = self._zk.get('/rpc_calc/' + server)[0]
            if data:
                addr = json.loads(data.decode())
                self._servers.append(addr)

    def get_server(self):
        """
        随机选出一个可用的服务器
        """
        return random.choice(self._servers)


def run():
    channel = DistributedChannel()
    server = channel.get_server()
    with grpc.insecure_channel("{}:{}".format(
            server.get("host"),
            server.get("port")
    )
    ) as channel:
        # 创建辅助客户端调用的stub对象
        stub = calculate_grpc.SimpleRpcServerStub(channel)
        invoke_calculate(stub)
        invoke_get_subject_question_types(stub)
        invoke_accumulate(stub)
        invoke_guess_number(stub)


if __name__ == '__main__':
    run()
