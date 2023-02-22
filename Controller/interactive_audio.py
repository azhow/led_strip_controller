import matplotlib.pyplot as plt
import matplotlib.animation as animation
import audio_capture_service_pb2
import numpy as np
import scipy.fft
import pandas as pd

class LEDDancer():
    def __init__(self):
        self.colors = [[148, 0, 211, 0], [75, 0, 130, 0], [0, 0, 255, 0], [0, 255, 0, 0], [255, 255, 0, 0], [255, 127, 0, 0], [255, 0, 0, 0]]
        self.frequencies = [60, 250, 500, 2000, 4000, 6000, 20000]
        self.window = np.zeros((500))
        print(self.window.shape)
        self.curr_packet = np.array([])

    def captureAudio(self, stub, controller):
        print("Received data")
        packets = stub.StartCapture(audio_capture_service_pb2.ProcessToCapture(pid=12988))
        for p in packets:
            buffer = np.frombuffer(p.captured_audio, dtype=np.float32)
            self.curr_packet = np.average(buffer.reshape(-1, 2), axis=1)
            yf = scipy.fft.rfft(self.curr_packet) / p.num_frames
            xf = scipy.fft.rfftfreq(p.num_frames, d=1./192000)
            strongest_freq = xf[np.argmax(yf)]
            self.window = np.append(self.window[1:], strongest_freq)
            moving_avg = self.numpy_ewma_vectorized_v2(self.window, 80)
            smoothed_freq = moving_avg[-20:].mean()
            new_color = [np.interp(smoothed_freq, self.frequencies, np.take(self.colors, i, axis=1)) for i in range(4)]
            #self.window = np.append(new_color, self.window[1:], axis=0)
            #self.curr_color = np.mean(self.window, axis=0)
            #self.window = np.vstack([self.numpy_ewma_vectorized_v2(np.take(self.window, i, axis=1), 50) for i in range(4)]).T
            controller.set_color(new_color)

    def numpy_ewma_vectorized_v2(self, data, window):
        alpha = 2 /(window + 1.0)
        alpha_rev = 1-(alpha)
        n = data.shape[0]

        pows = alpha_rev**(np.arange(n+1))

        scale_arr = 1/pows[:-1]
        offset = data[0]*pows[1:]
        pw0 = alpha*alpha_rev**(n-1)

        mult = data*pw0*scale_arr
        cumsums = mult.cumsum()
        out = offset + cumsums*scale_arr[::-1]
        return out


class AudioVisualizer():
    def __init__(self):
        self.curr_packet = np.array([])

    def captureAudio(self, stub):
        print("Received data")
        packets = stub.StartCapture(audio_capture_service_pb2.ProcessToCapture(pid=19032))
        for p in packets:
            buffer = np.frombuffer(p.captured_audio, dtype=np.float32)
            self.curr_packet = np.average(buffer.reshape(-1, 2), axis=1)

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