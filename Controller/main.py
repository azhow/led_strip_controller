import grpc
import logging

from concurrent import futures

import led_controller_service_pb2
import led_controller_service_pb2_grpc
import controller


controller = controller.MexllexLEDStripController(verbose=True)

class IllumiServicer(led_controller_service_pb2_grpc.IllumiService):

    def SetColor(self, request, context):
        controller.set_color(request.rgba_color)
        return led_controller_service_pb2.Empty()

    # def SayHelloAgain(self, request, context):
    #     return Controller.test_pb2.HelloReply(message='Hello again, %s!' % request.name)


def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    led_controller_service_pb2_grpc.add_IllumiServiceServicer_to_server(IllumiServicer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()