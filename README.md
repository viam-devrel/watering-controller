# `watering-controller` module

This [module](https://docs.viam.com/registry/modular-resources/) implements the [`rdk:service:generic` API](https://docs.viam.com/appendix/apis/services/generic/) for the automated plant watering workshop.

With this model, you can set up automated plant watering based on a moisture sensor and relay to control a water pump.

## Requirements

This module assumes you have a Viam machine configured with a board component that is connected to a soil moisture sensor and relay.

## Model: devrel:watering-controller:plant-watering

With this model, you can set up plant watering based on a moisture sensor and relay to control a water pump.

Navigate to the [**CONFIGURE** tab](https://docs.viam.com/configure/) of your [machine](https://docs.viam.com/fleet/machines/) in the [Viam app](https://app.viam.com/).
[Add `devrel:watering-controller` to your machine](https://docs.viam.com/configure/#services).

### Attributes

The following attributes are available for `devrel:watering-controller:plant-watering` generic service:

| Name    | Type   | Required?    | Default | Description |
| ------- | ------ | ------------ | ------- | ----------- |
| `board_name` | string | Required | N/A | The name of the board component to use to control the GPIO for the moisture sensor and relay. |
| `sensor_pin` | string | Optional | "40" | The physical pin number for the moisture sensor module. |
| `relay_pin` | string | Optional | "8" | The physical pin number for the relay module. |
| `auto_start` | boolean | Optional | true | Setting to start this control loop when the machine starts, otherwise wait until `start` command. |

### Example configuration

```json
{
    "board_name": "board-1"
}
```

## Commands

This module implements the following commands to be used by the `DoCommand` method in the Control tab of the Viam app or one of the language SDKs.

**start**

Start the control loop for reading the moisture sensor data and triggering the relay for the water pump.

```json
{
    "start": []
}
```

**stop**

Stop the control loop.

```json
{
    "stop": []
}
```
