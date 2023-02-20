import matplotlib.pyplot as plt
import matplotlib.animation as animation
import audio_capture_service_pb2
import numpy as np

curr_packet = np.array([])

def captureAudio(stub):
    global curr_packet
    print("Received data")
    packets = stub.StartCapture(audio_capture_service_pb2.ProcessToCapture(pid=19172))
    for p in packets:
        buffer = np.frombuffer(p.captured_audio, dtype=np.float32)
        curr_packet = np.array(buffer).reshape((2, p.num_frames))

def setupPlot():
    # Create figure for plotting
    fig, axs = plt.subplots(2)
    xs = []
    ys1 = []
    ys2 = []
    fig.suptitle("Audio Data per Channel")

    # This function is called periodically from FuncAnimation
    def animate(i, xs, ys1, ys2):
        if len(curr_packet) == 0:
            return

        num_frames = curr_packet.shape[1]
        # Add x and y to lists
        xs.append([(num_frames * i) + j for j in range(num_frames)])
        ys1.append(curr_packet[0,])
        ys2.append(curr_packet[1,])

        # Limit x and y lists to 20 items
        xs = xs[-1764:]
        ys1 = ys1[-1764:]
        ys2 = ys2[-1764:]

        # Draw x and y lists
        axs[0].clear()
        axs[0].plot(xs, ys1)
        axs[1].clear()
        axs[1].plot(xs, ys2)

        axs[0].set_title("Channel 0")
        axs[1].set_title("Channel 1")
        fig.tight_layout()

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys1, ys2), interval=1000)
    plt.show()