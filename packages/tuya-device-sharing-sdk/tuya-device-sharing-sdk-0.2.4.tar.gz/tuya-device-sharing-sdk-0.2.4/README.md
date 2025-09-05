# Tuya Device Sharing SDK

A Python sdk for Tuya Open API, which provides basic IoT capabilities like device management capabilities, helping you create IoT solutions. 
With diversified devices and industries, Tuya IoT Development Platform opens basic IoT capabilities like device management, AI scenarios, and data analytics services, as well as industry capabilities, helping you create IoT solutions.

## Features
### APIs

- Manager
  - update_device_cache
  - refresh_mq
  - send_commands
  - get_device_stream_allocate
  - query_scenes
  - trigger_scene
  - add_device_listener
  - remove_device_listener
  - unload
- CustomerApi
	- get
	- post
	- put
	- delete
- SharingMQ
	- start
	- stop
	- add_message_listener
	- remove_message_listener
- DeviceRepository
	- query_devices_by_home
	- query_devices_by_ids
	- send_commands
- HomeRepository
	- query_homes
- SceneRepository
	- query_scenes
	- trigger_scene

## Possible scenarios

- [Smart Life Integration](https://github.com/tuya/tuya-smart-life)

## Usage

## Release Note

| version | Description                                            |
| ------- | ------------------------------------------------------ |
| 0.1.8   | fix topic error                                        |
| 0.1.9   | fix mq link id                                         |
| 0.2.0   | MQTT bulk subscription                                 |
| 0.2.1   | add updated_status_properties to SharingDeviceListener |
| 0.2.2   | add timestamp to SharingDeviceListener                 |
| 0.2.3   | fix paho-mqtt dependency                               |
| 0.2.4   | fix asbtract decorator                                 |

## Installation

`pip3 install tuya-device-sharing-sdk`

## Issue feedback

You can provide feedback on your issue via **Github Issue**.

## License

**tuya-device-sharing-sdk** is available under the MIT license. Please see the [LICENSE](./LICENSE) file for more info.
