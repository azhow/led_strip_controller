#include "capture_service.h"

#include "process_audio_capturer.h"

using namespace AudioCaptureService;

CaptureService::CaptureService(DWORD pid) :
    _capturer{ std::make_unique<ProcessAudioCapturer>() }
{
}

grpc::Status CaptureService::StartCapture(grpc::ServerContext* context,
    const ProcessToCapture* request, grpc::ServerWriter<AudioPacket>* writer)
{
    _capturer->startCapture(request->pid(), 
        [writer, this](auto packet) { this->captureAction(writer, packet); });

    return grpc::Status::OK;
}

grpc::Status CaptureService::StopCapture(grpc::ServerContext* context, 
    const Empty* request, Empty* response)
{
    _capturer->stopCapture();

    return grpc::Status::OK;
}

grpc::Status CaptureService::Status(grpc::ServerContext* context, 
    const Empty* request, Availability* response)
{
    return grpc::Status::OK;
}

grpc::Status CaptureService::Shutdown(grpc::ServerContext* context,
    const Empty* request, Empty* response)
{
    return grpc::Status::OK;
}

AudioPacket CaptureService::convertAudioPacket(
    ProcessAudioCapturer::AudioPacket src) const
{
    AudioPacket out;

    out.set_timestamp(src.timestamp);
    out.set_num_frames(src.nFrames);
    out.set_captured_audio(std::string(src.data, src.data + src.size));

    return out;
}

void CaptureService::captureAction(grpc::ServerWriter<AudioPacket>* writer,
    ProcessAudioCapturer::AudioPacket packet)
{
    writer->Write(convertAudioPacket(packet));
}
