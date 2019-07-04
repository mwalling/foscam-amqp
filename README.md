# foscam-amqp
Listen on AMQP for commands to send to Foscam

My use case is for Home Assistant. At my house, I'm using this to fire scene movements from automations - when we are home, the camera spins around and points to the wall. But when we're not home, it turns out and looks into the room. I also added support for up/down/left/right so that the camera can be moved from the Home Assistant UI.

## Configuration

```ini
[default]
broker_address = 192.168.1.48

[camera1]
ip = 192.168.1.58
port = 443
username = admin
password = admin
```
