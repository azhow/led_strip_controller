import argparse
import asyncio
import Controller.controller as btctrl

def set_color(color):
    controller = btctrl.MexllexLEDStripController(verbose=True)
    asyncio.run(controller.set_color(color))

def play_custom_breathing():
    controller = btctrl.MexllexLEDStripController(verbose=True)
    asyncio.run(controller.custom_breathing())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Controls LED Strip Mexllex.')

    parser.add_argument('color', metavar='channel_val', choices=range(0, 256), type=int, nargs=3, help='RGB values for to set the color to')

    args = parser.parse_args()

    set_color(args.color)