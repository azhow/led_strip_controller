import matplotlib.pyplot as plt
import matplotlib.animation as animation
import audio_capture_service_pb2
import numpy as np
import scipy.fft

class AudioVisualizer():
    def __init__(self):
        self.curr_packet = np.array([])

    def captureAudio(self, stub):
        print("Received data")
        packets = stub.StartCapture(audio_capture_service_pb2.ProcessToCapture(pid=19032))
        for p in packets:
            buffer = np.frombuffer(p.captured_audio, dtype=np.float32)
            self.curr_packet = np.average(buffer.reshape(-1, 2), axis=1)
            #self.curr_packet = np.array([self.generate_sine_wave(20000, 441), self.generate_sine_wave(20000, 441)], dtype=np.float32).T

    def frequency_visualization(self):
        # Create figure for plotting
        fig, ax = plt.subplots()
        ys = [0] * 1920
        ys2 = [0] * 1920
        fig.suptitle("Audio Data Frequencies")

        # This function is called periodically from FuncAnimation
        def animate(i, ys, ys2):
            if len(self.curr_packet) == 0:
                return

            num_frames = self.curr_packet.shape[0]

            # Add x and y to lists
            ys += self.curr_packet.tolist()

            # Limit x and y lists the last items
            del ys[:num_frames]

            yf = scipy.fft.rfft(ys) / num_frames
            xf = scipy.fft.rfftfreq(num_frames, d=1./192000)

            ax.clear()
            ax.plot(xf, np.abs(yf))

            ax.set_ylabel("Magnitude")
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylim(0, 1)
            ax.set_xlim(0, 22050)
            fig.tight_layout()

        # Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(fig, animate, fargs=(ys, ys2), interval=10)
        plt.show()

    def amplitude_visualization(self):
        # Create figure for plotting
        fig, axs = plt.subplots()
        ys = [0] * 1920 * 4
        ys2 = [0] * 1920
        fig.suptitle("Audio Data")

        # This function is called periodically from FuncAnimation
        def animate(i, ys, ys2):
            if len(self.curr_packet) == 0:
                return

            num_frames = self.curr_packet.shape[0]

            # Add x and y to lists
            ys += self.curr_packet.tolist()

            # Limit x and y lists the last items
            del ys[:num_frames]

            # Draw x and y lists
            axs.clear()
            axs.plot(ys)

            axs.set_ylabel("Amplitude")
            axs.set_ylim(-1, 1)
            fig.tight_layout()

        # Set up plot to call animate() function periodically
        ani = animation.FuncAnimation(fig, animate, fargs=(ys, ys2), interval=1)
        plt.show()

    def generate_sine_wave(self, freq, n_frames):
        x = np.linspace(0, 1, 192000, endpoint=False)
        frequencies = x * freq
        # 2pi because np.sin takes radians
        y = np.sin((2 * np.pi) * frequencies)
        return y