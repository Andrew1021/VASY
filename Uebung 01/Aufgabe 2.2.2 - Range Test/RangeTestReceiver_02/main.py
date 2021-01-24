import xbee

print("\nI am " + xbee.atcmd("NI"))

while True:
    msg = xbee.receive()

    if msg and msg['payload'].decode() == 'ping':

        for node in list(xbee.discover()):
            if node['node_id'] == 'Coordinator':
                xbee.transmit(xbee.ADDR_BROADCAST, str(node['rssi']))
