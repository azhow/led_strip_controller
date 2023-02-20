#pragma once

#include <array>
#include <functional>
#include <thread>
#include <set>
#include <cstdint>

#include <windows.h>

#include <audiopolicy.h>
#include <audioclient.h>
#include <audioclientactivationparams.h>
#include <initguid.h>
#include <mmdeviceapi.h>
#include <wrl/implements.h>
#include <wil/com.h>

namespace AudioCaptureService 
{
    class ProcessAudioCapturer
    {
    public:
        struct AudioPacket
        {
            std::uint8_t* data{ nullptr };
            std::uint32_t flags{ 0 };
            std::uint64_t timestamp{ 0 };
            std::uint32_t nFrames{ 0 };
            std::size_t   size{ 0 };
        };

        ProcessAudioCapturer();
        ~ProcessAudioCapturer();

        void startCapture(std::uint32_t pid,
            std::function<void(AudioPacket)> action);
        void stopCapture();

    private:
        struct CompletionHandler : public Microsoft::WRL::RuntimeClass<
            Microsoft::WRL::RuntimeClassFlags<Microsoft::WRL::ClassicCom>, 
            Microsoft::WRL::FtmBase, IActivateAudioInterfaceCompletionHandler>
        {
            wil::com_ptr<IAudioClient> client;

            HRESULT activate_hr = E_FAIL;
            wil::unique_event event_finished;

            CompletionHandler() { event_finished.create(); }

            STDMETHOD(ActivateCompleted)
            (IActivateAudioInterfaceAsyncOperation *operation)
            {
                auto set_finished = event_finished.SetEvent_scope_exit();

                RETURN_IF_FAILED(operation->GetActivateResult(&activate_hr, 
                    client.put_unknown()));

                //if (FAILED(activate_hr))
                    //error("activate failed (0x%lx)", activate_hr);

                return S_OK;
            }
        };

        enum HelperEvents
        {
            PacketReady,
            Shutdown,
            Count,
        };

        wil::unique_couninitialize_call _couninit{ wil::CoInitializeEx() };

        wil::com_ptr<IAudioClient> _client;
        wil::com_ptr<IAudioCaptureClient> _captureClient;
        std::array<wil::unique_event, HelperEvents::Count> _events;
        WAVEFORMATEX _format;
        
        std::uint32_t _pid;
        std::function<void(AudioPacket)> _captureAction;
        std::thread _captureThread;

        AUDIOCLIENT_ACTIVATION_PARAMS getParams() const;
        PROPVARIANT getPropvariant(AUDIOCLIENT_ACTIVATION_PARAMS *params) const;
        void initClient();
        void forwardPacket();
        void capture();
        void captureSafe();
        WAVEFORMATEX initializeFormat() const;
    };
}
