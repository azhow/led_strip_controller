import grpc
import logging
import time

from subprocess import Popen
from concurrent import futures

import audio_capture_service_pb2
import audio_capture_service_pb2_grpc
import led_controller_service_pb2
import led_controller_service_pb2_grpc
import controller

controller = controller.MexllexLEDStripController(verbose=True)
controller.set_color([0, 0, 0, 0])

class LEDControllerServicer(led_controller_service_pb2_grpc.LEDController):
    def SetColor(self, request, context):
        print("Set color called")
        controller.set_color(request.rgba_color)
        return led_controller_service_pb2.Empty()


def captureAudio(stub):
    packets = stub.StartCapture(audio_capture_service_pb2.ProcessToCapture(pid=2712))
    for p in packets:
        print(p.num_frames)


def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    led_controller_service_pb2_grpc.add_LEDControllerServicer_to_server(LEDControllerServicer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    audioCapturerServerProcess = Popen("./../AudioCaptureService/x64/Debug/AudioCaptureService.exe")

    with grpc.insecure_channel('localhost:42069') as channel:
        stub = audio_capture_service_pb2_grpc.AudioCapturerStub(channel)
        print("-------------- CaptureAudio --------------")
        captureAudio(stub)

    logging.basicConfig()
    serve()
    audioCapturerServerProcess.kill()