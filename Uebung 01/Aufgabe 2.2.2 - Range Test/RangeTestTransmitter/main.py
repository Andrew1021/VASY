import xbee
import time

NO_OF_ROUNDS = 5

NO_OF_DEVICES = 2
TIMEOUT = 5000


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

    xbee.transmit(xbee.ADDR_BROADCAST, 'ping')

    responses = {}
    start_time = time.ticks_ms()

    while len(responses) < NO_OF_DEVICES:
        response = xbee.receive()

        if response and response['sender_nwk'] not in responses.keys():
            responses[response['sender_nwk']] = response

            print(response)

        time_delta = time.ticks_diff(time.ticks_ms(), start_time)

        if time_delta >= TIMEOUT:
            print("Timeout!")
            break

    for node_id in rssi_stats.keys():
        if node_id in responses.keys():
            rssi_stats[node_id]['all'].append(int(responses[node_id]['payload'].decode()))

print()
print("----------------------------------------------------------------")

for node_id, stats in rssi_stats.items():
    stats['min'] = min(stats['all'])
    stats['max'] = max(stats['all'])
    stats['mean'] = sum(stats['all']) / len(stats['all'])

    print("Node no.", node_id)
    print("min: {} dB | max: {} dB | mean: {} dB | {}/{} received packages".format(
        stats['min'], stats['max'], stats['mean'], len(stats['all']), NO_OF_ROUNDS)
    )
    print("----------------------------------------------------------------")
