import grpc
import logging
import concurrent.futures

from subprocess import Popen
from concurrent import futures

import audio_capture_service_pb2
import audio_capture_service_pb2_grpc
import led_controller_service_pb2
import led_controller_service_pb2_grpc
import controller as led_ctrl
import interactive_audio


controller = led_ctrl.MexllexLEDStripController(verbose=False)
controller.set_color([0, 0, 0, 0])

class LEDControllerServicer(led_controller_service_pb2_grpc.LEDController):
    def SetColor(self, request, context):
        print("Set color called")
        controller.set_color(request.rgba_color)
        return led_controller_service_pb2.Empty()


def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    led_controller_service_pb2_grpc.add_LEDControllerServicer_to_server(LEDControllerServicer(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


def runAudioClientVisualizer():
    #audioCapturerServerProcess = Popen("./../AudioCaptureService/x64/Debug/AudioCaptureService.exe")
    audioCapturerServerProcess = Popen("./led_strip_controller/AudioCaptureService/x64/Debug/AudioCaptureService.exe")

    visualizer = interactive_audio.AudioVisualizer()
    with grpc.insecure_channel('localhost:42069') as channel:
        stub = audio_capture_service_pb2_grpc.AudioCapturerStub(channel)
        print("-------------- CaptureAudio --------------")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            executor.submit(visualizer.captureAudio, stub)
            visualizer.frequency_visualization()
            #interactive_audio.write_file()

    audioCapturerServerProcess.kill()


def runAudioClient():
    #audioCapturerServerProcess = Popen("./../AudioCaptureService/x64/Debug/AudioCaptureService.exe")
    audioCapturerServerProcess = Popen("./led_strip_controller/AudioCaptureService/x64/Debug/AudioCaptureService.exe")

    dancer = interactive_audio.LEDDancer()
    with grpc.insecure_channel('localhost:42069') as channel:
        stub = audio_capture_service_pb2_grpc.AudioCapturerStub(channel)
        print("-------------- CaptureAudio --------------")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            executor.submit(dancer.captureAudio, stub, controller)

    audioCapturerServerProcess.kill()


if __name__ == '__main__':
    runAudioClient()
    logging.basicConfig()
    serve()