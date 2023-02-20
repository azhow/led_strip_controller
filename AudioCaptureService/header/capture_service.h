#pragma once

#pragma warning(disable: 4251)
#include "audio_capture_service.grpc.pb.h"

#include <memory>

#include "process_audio_capturer.h"

namespace AudioCaptureService
{
    class CaptureService final : public AudioService::AudioCapturer::Service
    {
    public:
        CaptureService();

        grpc::Status StartCapture(grpc::ServerContext* context,
            const AudioService::ProcessToCapture* request,
            grpc::ServerWriter<AudioService::AudioPacket>* writer) override;

        grpc::Status StopCapture(grpc::ServerContext* context,
            const AudioService::Empty* request,
            AudioService::Empty* response) override;

        grpc::Status Status(grpc::ServerContext* context,
            const AudioService::Empty* request,
            AudioService::Availability* response) override;

        grpc::Status Shutdown(grpc::ServerContext* context,
            const AudioService::Empty* request,
            AudioService::Empty* response) override;
    private:
        std::unique_ptr<ProcessAudioCapturer> _capturer;

        AudioService::AudioPacket convertAudioPacket(
            ProcessAudioCapturer::AudioPacket src) const;

        void captureAction(grpc::ServerWriter<AudioService::AudioPacket>* writer,
            ProcessAudioCapturer::AudioPacket packet);
    };
}
