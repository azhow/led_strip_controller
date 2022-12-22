import grpc
import logging

from concurrent import futures

import test_pb2
import test_pb2_grpc
import controller


controller = controller.MexllexLEDStripController(verbose=True)

class Greeter(test_pb2_grpc.GreeterServicer):

    def SetColor(self, request, context):
        controller.set_color(request.rgb_color)
        return test_pb2.HelloReply(message='Setting color: {}.'.format(request.rgb_color))

    # def SayHelloAgain(self, request, context):
    #     return Controller.test_pb2.HelloReply(message='Hello again, %s!' % request.name)


def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()