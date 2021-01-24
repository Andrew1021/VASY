from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress


coordinator = XBeeDevice("/dev/ttyUSB2", 9600)
remote_coordinator = RemoteXBeeDevice(coordinator, XBee64BitAddress.from_hex_string("0000"))

end_device_2 = XBeeDevice("/dev/ttyUSB1", 9600)
end_device_2.open()

while True:
    msg = end_device_2.read_data()

    if msg and msg.data.decode() == 'ping':
        db = int.from_bytes(end_device_2.get_parameter('DB'), 'big')
        end_device_2.send_data(remote_coordinator, "-" + str(db))
