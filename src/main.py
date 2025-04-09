import asyncio
from threading import Event
from typing import ClassVar, Mapping, Optional, Sequence, cast

from typing_extensions import Self
from viam.components.board import Board
from viam.logging import getLogger
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.services.generic import Generic
from viam.utils import struct_to_dict, ValueTypes

LOGGER = getLogger("refill-controller")


class PlantWatering(Generic, EasyResource):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("devrel", "watering-controller"), "plant-watering"
    )

    auto_start = True
    task = None
    event = Event()

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Generic service.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        attrs = struct_to_dict(config.attributes)

        board_name = attrs.get("board_name")

        if board_name is None:
            raise Exception("Missing required board_name attribute.")

        return [str(board_name)]

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        attrs = struct_to_dict(config.attributes)
        self.auto_start = bool(attrs.get("auto_start", self.auto_start))

        board_resource = dependencies.get(
            Board.get_resource_name(str(attrs.get("board_name")))
        )
        self.board = cast(Board, board_resource)

        self.sensor_pin = str(attrs.get("sensor_pin", "40"))
        self.relay_pin = str(attrs.get("relay_pin", "8"))

        if self.auto_start:
            self.start()

    async def on_loop(self):
        sensor = await self.board.gpio_pin_by_name(self.sensor_pin)
        relay = await self.board.gpio_pin_by_name(self.relay_pin)
        LOGGER.info("Checking moisture sensor.")

        should_water = await sensor.get()
        LOGGER.info(f"Should water? {should_water}")
        await relay.set(should_water)

        await asyncio.sleep(1)
        LOGGER.info(f"Currently watering? {await relay.get()}")
        await asyncio.sleep(1)

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Mapping[str, ValueTypes]:
        result = {key: False for key in command.keys()}
        for name, _args in command.items():
            if name == "start":
                self.start()
                result[name] = True
            if name == "stop":
                self.stop()
                result[name] = True
        return result

    def start(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.control_loop())
        self.event.clear()

    def stop(self):
        self.event.set()
        if self.task is not None:
            self.task.cancel()

    async def control_loop(self):
        while not self.event.is_set():
            await self.on_loop()
            await asyncio.sleep(0)

    def __del__(self):
        self.stop()

    async def close(self):
        self.stop()


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
