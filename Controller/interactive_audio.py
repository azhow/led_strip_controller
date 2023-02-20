import queue
import sys

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import soundcard as sc

# def callback(indata, frames, time, status):
#     plt.plot(indata)
#     plt.xlabel("Sample Number")
#     plt.ylabel("Amplitude")
#     plt.show()

# with sd.InputStream(device=sd.default.device, callback=callback):
#     print('#' * 80)
#     print('press Return to quit')
#     print('#' * 80)
#     input()


# Set the virtual loopback device as the default input
sc.default_input_device = sc.default_output_device
print(sc.default_input_device)

mapping = [c - 1 for c in [1, 2]]  # Channel numbers start with 1
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    # Fancy indexing with mapping creates a (necessary!) copy:
    if np.any(indata):
        print("Dados?")
        q.put(indata[::10, mapping])


def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata
    while True:
        try:
            data = q.get_nowait()
        except queue.Empty:
            break

        shift = len(data)
        plotdata = np.roll(plotdata, -shift, axis=0)
        plotdata[-shift:, :] = data
    for column, line in enumerate(lines):
        line.set_ydata(plotdata[:, column])
    return lines

device_info = sd.query_devices(sd.default.device, 'output')
samplerate = device_info['default_samplerate']
print(device_info)

length = int(200 * samplerate / (1000 * 10))
plotdata = np.zeros((length, 2))

fig, ax = plt.subplots()
lines = ax.plot(plotdata)

ax.axis((0, len(plotdata), -1, 1))
ax.set_yticks([0])
ax.yaxis.grid(True)
ax.tick_params(bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
fig.tight_layout(pad=0)

stream = sd.InputStream(device=sc.default_input_device, channels=device_info['max_output_channels'], callback=audio_callback)

ani = FuncAnimation(fig, update_plot, interval=30, blit=True)

with stream:
    plt.show()