#pragma once

#pragma warning(disable: 4251)
#include "audio_capture_service.grpc.pb.h"

#include <memory>

#include "process_audio_capturer.h"

namespace AudioCaptureService
{
    class CaptureService final : public AudioCapture::Service
    {
    public:
        CaptureService(DWORD pid);

        grpc::Status StartCapture(grpc::ServerContext* context, 
            const ProcessToCapture* request, 
            grpc::ServerWriter<AudioPacket>* writer) override;

        grpc::Status StopCapture(grpc::ServerContext* context, 
            const Empty* request, Empty* response) override;
        
        grpc::Status Status(grpc::ServerContext* context, 
            const Empty* request, Availability* response) override;
        
        grpc::Status Shutdown(grpc::ServerContext* context,
            const Empty* request, Empty* response) override;
    private:
        std::unique_ptr<ProcessAudioCapturer> _capturer;

        AudioPacket convertAudioPacket(
            ProcessAudioCapturer::AudioPacket src) const;

        void captureAction(grpc::ServerWriter<AudioPacket>* writer, 
            ProcessAudioCapturer::AudioPacket packet);
    };
}
