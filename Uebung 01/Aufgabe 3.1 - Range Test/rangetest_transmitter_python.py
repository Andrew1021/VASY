from digi.xbee.devices import XBeeDevice
from digi.xbee.exception import TimeoutException

NO_OF_ROUNDS = 10
NO_OF_DEVICES = 2
TIMEOUT = 5

coordinator = XBeeDevice("/dev/ttyUSB2", 9600)
coordinator.open()

print("Running", NO_OF_ROUNDS, "rounds")

rssi_stats = {}

for node_id in range(1, NO_OF_DEVICES+1):
    stats = {
        'all': [],
    }
    rssi_stats[node_id] = stats


for round_number in range(NO_OF_ROUNDS):
    if round_number % 10 == 0:
        print("Round number:", round_number)

    coordinator.send_data_broadcast('ping')

    responses = {}

    while len(responses) < NO_OF_DEVICES:
        try:
            response = coordinator.read_data(TIMEOUT)
            sender_id = int.from_bytes(response.remote_device.get_16bit_addr().address, "big")

            if sender_id not in responses.keys():
                responses[sender_id] = response.data.decode()

        except TimeoutException:
            print("Timeout!")
            break

    for node_id in rssi_stats.keys():
        if node_id in responses.keys():
            rssi_stats[node_id]['all'].append(int(responses[node_id]))

coordinator.close()

print()
print("----------------------------------------------------------------------------")

for node_id, stats in rssi_stats.items():
    stats['min'] = min(stats['all'])
    stats['max'] = max(stats['all'])
    stats['mean'] = sum(stats['all']) / len(stats['all'])

    print("Node no.", node_id)
    print("min: {} dBm | max: {} dBm | mean: {} dBm | {}/{} received packages".format(
        stats['min'], stats['max'], stats['mean'], len(stats['all']), NO_OF_ROUNDS)
    )
    print("----------------------------------------------------------------------------")
