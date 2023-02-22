#include <functional>
#include <windows.h>

#include <stdint.h>
#include <stdbool.h>
#include <inttypes.h>
#include <vector>
#include <stdexcept>

#include <wil/result.h>
#include <wil/result_macros.h>

#include "process_audio_capturer.h"

using namespace AudioCaptureService;

AUDIOCLIENT_ACTIVATION_PARAMS ProcessAudioCapturer::getParams() const
{
	return {
		.ActivationType = AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK,
		.ProcessLoopbackParams =
			{
				.TargetProcessId = _pid,
				.ProcessLoopbackMode =
					PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE,
			},
	};
}

PROPVARIANT
ProcessAudioCapturer::getPropvariant(AUDIOCLIENT_ACTIVATION_PARAMS *params) const
{
	return PROPVARIANT{
		.vt = VT_BLOB,
		.blob =
			{
				.cbSize = sizeof(*params),
				.pBlobData = (BYTE *)params,
			},
	};
}

void ProcessAudioCapturer::initClient()
{
	auto params{ getParams() };
	auto propvariant{ getPropvariant(&params) };

	wil::com_ptr<IActivateAudioInterfaceAsyncOperation> asyncOp;
	CompletionHandler completionHandler;

	THROW_IF_FAILED(ActivateAudioInterfaceAsync(
		VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK, __uuidof(IAudioClient),
		&propvariant, &completionHandler, &asyncOp));

	completionHandler.event_finished.wait();
	THROW_IF_FAILED(completionHandler.activate_hr);

	_client = completionHandler.client;

	THROW_IF_FAILED(_client->Initialize(AUDCLNT_SHAREMODE_SHARED,
		AUDCLNT_STREAMFLAGS_LOOPBACK | AUDCLNT_STREAMFLAGS_EVENTCALLBACK,
		5 * 10000000, 0, &_format, NULL));

	THROW_IF_FAILED(_client->SetEventHandle(
		_events[HelperEvents::PacketReady].get()));

	THROW_IF_FAILED(_client->GetService(__uuidof(IAudioCaptureClient),
		_captureClient.put_void()));
}

void ProcessAudioCapturer::forwardPacket()
{
	AudioPacket packet{};
	THROW_IF_FAILED(_captureClient->GetNextPacketSize(&packet.nFrames));

	while (packet.nFrames > 0) {
		THROW_IF_FAILED(_captureClient->GetBuffer(&packet.data, &packet.nFrames,
			(DWORD*)&packet.flags, NULL, &packet.timestamp));

		// Send forward data to processing
		if (!(packet.flags & AUDCLNT_BUFFERFLAGS_SILENT))
		{
			packet.size = packet.nFrames * static_cast<std::size_t>(
				_format.nBlockAlign);
			_captureAction(packet);
		}

		/*if (flags & AUDCLNT_BUFFERFLAGS_DATA_DISCONTINUITY)
			warn("data discontinuity flag set");

		if (flags & AUDCLNT_BUFFERFLAGS_TIMESTAMP_ERROR)
			warn("timestamp error flag set");*/

		THROW_IF_FAILED(_captureClient->ReleaseBuffer(packet.nFrames));
		THROW_IF_FAILED(_captureClient->GetNextPacketSize(&packet.nFrames));
	}
}

void ProcessAudioCapturer::capture()
{
	initClient();
	THROW_IF_FAILED(_client->Start());

	bool shutdown{ false };
	while (!shutdown) {
		auto event_id{ WaitForMultipleObjects(_events.size(),
			_events[0].addressof(), FALSE, INFINITE) };

		switch (event_id) {
		case HelperEvents::PacketReady:
			forwardPacket();
			break;

		case HelperEvents::Shutdown:
			shutdown = true;
			break;

		default:
			//error("wait failed with result: %d", event_id);
			shutdown = true;
			break;
		}
	}

	THROW_IF_FAILED(_client->Stop());
}

void ProcessAudioCapturer::captureSafe()
{
	try {
		capture();
	} catch (wil::ResultException e) {
		//error("%s", e.what());
	}
}

ProcessAudioCapturer::ProcessAudioCapturer() :
	_format{ initializeFormat() }
{
	for (auto &event : _events)
		event.create();
}

ProcessAudioCapturer::~ProcessAudioCapturer()
{
	stopCapture();
}

WAVEFORMATEX ProcessAudioCapturer::initializeFormat() const
{
    // get the device enumerator
    IMMDeviceEnumerator* pEnumerator = nullptr;
    THROW_IF_FAILED( CoCreateInstance(__uuidof(MMDeviceEnumerator),
		NULL, CLSCTX_ALL, __uuidof(IMMDeviceEnumerator), (LPVOID*)&pEnumerator));

    // get default audio endpoint
    IMMDevice* pDevice = nullptr;
    THROW_IF_FAILED(pEnumerator->GetDefaultAudioEndpoint(eRender, eMultimedia,
		&pDevice));
    IPropertyStore* store = nullptr;
    THROW_IF_FAILED(pDevice->OpenPropertyStore(STGM_READ, &store));
    PROPVARIANT prop;
    THROW_IF_FAILED(store->GetValue(PKEY_AudioEngine_DeviceFormat, &prop));

	PWAVEFORMATEX deviceFormatProperties{ (PWAVEFORMATEX)prop.blob.pBlobData };

	WAVEFORMATEX format{};
    format.wFormatTag = WAVE_FORMAT_IEEE_FLOAT;
    format.nChannels = deviceFormatProperties->nChannels;
    format.nSamplesPerSec = 192000;

    format.nBlockAlign = format.nChannels * sizeof(float);
    format.nAvgBytesPerSec = format.nSamplesPerSec * format.nBlockAlign;
    format.wBitsPerSample = CHAR_BIT * sizeof(float);
    format.cbSize = 0;

	return format;
}

void ProcessAudioCapturer::startCapture(std::uint32_t pid,
	std::function<void(AudioPacket)> action)
{
	_pid = pid;
	_captureAction = action;
	_captureThread = std::thread(&ProcessAudioCapturer::captureSafe, this);

	_captureThread.join();
}

void ProcessAudioCapturer::stopCapture()
{
	_events[HelperEvents::Shutdown].SetEvent();
	if (_captureThread.joinable())
	{
        _captureThread.join();
	}
}
