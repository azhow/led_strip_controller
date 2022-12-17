import asyncio
from enum import Enum
from time import sleep
from bleak import BleakScanner, BleakClient


class MexllexLEDStripController:
    class Command(Enum):
        TURN_OFF       = 0
        TURN_ON        = 1
        MIN_BRIGHTNESS = 2
        MAX_BRIGHTNESS = 3
        MIN_SATURATION = 4
        MAX_SATURATION = 5
        BREATHING_MODE = 6
        COLOR          = 7
        RED            = 8
        GREEN          = 9
        BLUE           = 10
        WHITE          = 11
        UNKNOWN        = 12


    def __init__(self, verbose=False):
        self.DEVICE_NAME = "DMRRBA-001"
        self.COMMAND_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
        self.COMMANDS = {
            self.Command.TURN_OFF:        (0x5a010200, 4),
            self.Command.TURN_ON:         (0x5a010201, 4),
            self.Command.MIN_BRIGHTNESS : (0x5a03010000, 5),
            self.Command.MAX_BRIGHTNESS : (0x5a030100ff, 5),
            self.Command.MIN_SATURATION : (0x5a0703ffff, 5),
            self.Command.MAX_SATURATION : (0x5a07030000, 5),
            self.Command.BREATHING_MODE : (0x5a040492, 4),
            self.Command.COLOR :          (0x5a0701000000, 6),
            self.Command.RED :            (0x5a0701ff0000, 6),
            self.Command.GREEN :          (0x5a070100ff00, 6),
            self.Command.BLUE :           (0x5a07010000ff, 6),
            self.Command.WHITE :          (0x5a0701ffffff, 6),
            self.Command.UNKNOWN :        (0x5a0701ff00ff, 6)
        }

        self.DEVICE = asyncio.run(self.discover_device())
        self.VERBOSE = verbose

    def _serialize_command(self, command_pair):
        return command_pair[0].to_bytes(command_pair[1], 'big')

    def _compose_color(self, color):
        base_color, size = self.COMMANDS[self.Command.COLOR]

        composed_color = base_color | int(color[2])
        # Shift 1 byte
        composed_color = composed_color | (int(color[1]) << 8)
        # Shift 2 bytes
        composed_color = composed_color | (int(color[0]) << 16)

        return composed_color.to_bytes(size, 'big')

    async def discover_device(self):
        device = None

        devices = await BleakScanner.discover()
        for d in devices:
            if d.name == self.DEVICE_NAME:
                device = d

        return device            

    async def send_command(self, command):
        try:
            async with BleakClient(self.DEVICE) as client:
                paired = await client.pair()

                if (client.is_connected and paired):
                    await client.write_gatt_char(self.COMMAND_UUID, self._serialize_command(self.COMMANDS[command]))
                else:
                    raise Exception("Client not connect or not paired")

        except Exception as e:
            if self.VERBOSE:
                print("Error: {0}".format(e))

        finally:
            await client.disconnect()

    async def commands_test(self):
        try:
            async with BleakClient(self.DEVICE) as client:
                paired = await client.pair()

                if (client.is_connected and paired):
                    for comm in self.Command:
                        await client.write_gatt_char(self.COMMAND_UUID, self._serialize_command(self.COMMANDS[comm]))
                        sleep(0.2)
                else:
                    raise Exception("Client not connect or not paired")

        except Exception as e:
            if self.VERBOSE:
                print("Error: {0}".format(e))

        finally:
            await client.disconnect()

    async def set_color(self, color):
        assert len(color) == 3, "Color has number of channels different than 3 (R,G,B)"
        for c in color:
            assert 0 <= c < 256, "Channel outside of valid range [0, 255]"

        try:
            async with BleakClient(self.DEVICE) as client:
                paired = await client.pair()

                if (client.is_connected and paired):
                    command = self._compose_color(color)
                    if self.VERBOSE:
                        print("Executing command: {0}".format(hex(int.from_bytes(command, 'big'))))
                    await client.write_gatt_char(self.COMMAND_UUID, command)
                else:
                    raise Exception("Client not connect or not paired")

        except Exception as e:
            if self.VERBOSE:
                print("Error: {0}".format(e))

        finally:
            await client.disconnect()

    async def custom_breathing(self):
        try:
            async with BleakClient(self.DEVICE) as client:
                paired = await client.pair()

                if (client.is_connected and paired):
                            for r in range(0, 256 + 1, 256//8):
                                for g in range(0, 256 + 1, 256//8):
                                    for b in range(0, 256 + 1, 256//8):
                                        if r == 256: r -= 1
                                        if g == 256: g -= 1
                                        if b == 256: b -= 1

                                        command = self._compose_color([r, g, b])
                                        if self.VERBOSE:
                                            print("Executing command: {0}".format(hex(int.from_bytes(command, 'big'))))
                                        await client.write_gatt_char(self.COMMAND_UUID, command)
                                        sleep(0.1)
                else:
                    raise Exception("Client not connect or not paired")

        except Exception as e:
            if self.VERBOSE:
                print("Error: {0}".format(e))

        finally:
            await client.disconnect()

