import matplotlib.pyplot as plt
import matplotlib.animation as animation
import audio_capture_service_pb2
import numpy as np

curr_packet = np.array([])

def captureAudio(stub):
    global curr_packet
    print("Received data")
    packets = stub.StartCapture(audio_capture_service_pb2.ProcessToCapture(pid=23196))
    for p in packets:
        buffer = np.frombuffer(p.captured_audio, dtype=np.float32)
        curr_packet = np.array(buffer).reshape((2, p.num_frames)).T

def setupFreqPlot():
    # Create figure for plotting
    fig, axs = plt.subplots(2)
    ys1 = [0] * 441
    ys2 = [0] * 441
    fig.suptitle("Audio Data Frequencies")
    plt.ylabel('Frequency (Hz)')

    # This function is called periodically from FuncAnimation
    def animate(i, ys1, ys2):
        if len(curr_packet) == 0:
            return

        num_frames = curr_packet.shape[0]

        # Add x and y to lists
        ys1 += curr_packet[:,0].tolist()
        ys2 += curr_packet[:,1].tolist()

        # Limit x and y lists the last items
        del ys1[:num_frames]
        del ys2[:num_frames]

        y1f = np.fft.rfft(ys1)
        y2f = np.fft.rfft(ys2)
        xf = np.fft.rfftfreq(num_frames, d=1./44100)

        axs[0].clear()
        axs[1].clear()

        axs[0].plot(xf, np.abs(y1f))
        axs[1].plot(xf, np.abs(y2f))

        axs[0].set_title("Channel 0")
        axs[1].set_title("Channel 1")
        axs[0].set_ylim(0, 100)
        axs[1].set_ylim(0, 100)
        axs[0].set_xlim(0, 22050)
        axs[1].set_xlim(0, 22050)
        fig.tight_layout()

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(ys1, ys2), interval=50)
    plt.show()

def setupTimePlot():
    # Create figure for plotting
    fig, axs = plt.subplots(2)
    ys1 = [0] * 1764
    ys2 = [0] * 1764
    fig.suptitle("Audio Data per Channel")

    # This function is called periodically from FuncAnimation
    def animate(i, ys1, ys2):
        if len(curr_packet) == 0:
            return

        num_frames = curr_packet.shape[0]

        # Add x and y to lists
        ys1 += curr_packet[:,0].tolist()
        ys2 += curr_packet[:,1].tolist()

        # Limit x and y lists the last items
        del ys1[:num_frames]
        del ys2[:num_frames]

        # Draw x and y lists
        axs[0].clear()
        axs[0].plot(ys1)
        axs[1].clear()
        axs[1].plot(ys2)

        axs[0].set_title("Channel 0")
        axs[1].set_title("Channel 1")
        axs[0].set_ylim(-1, 1)
        axs[1].set_ylim(-1, 1)

        fig.tight_layout()

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(ys1, ys2), interval=100)
    plt.show()

def generate_sine_wave(freq, sample_rate, duration):
    x = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    frequencies = x * freq
    # 2pi because np.sin takes radians
    y = np.sin((2 * np.pi) * frequencies)
    return x, y