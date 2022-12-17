import asyncio
import Controller.controller

controller = Controller.controller.MexllexLEDStripController()

asyncio.run(controller.commands_test())