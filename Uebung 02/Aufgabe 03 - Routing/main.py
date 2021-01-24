import xbee
import time
import struct

COORDINATOR_ADDR = 0
DESTINATION_ADDR = 1

RREQ_PACKET = 2
RREP_PACKET = 3
PAYLOAD_PACKET = 4


class RoutingTable:
    def __init__(self):
        self.routing_table = []

    def add_route(self, _destination, _next_hop):
        self.routing_table.append({
            "destination": _destination,
            "next_hop": _next_hop,
            "timestamp": time.ticks_ms()
        })

    def update_route_table(self, _destination, _next_hop):
        for route in self.routing_table:
            if route['destination'] == _destination:
                route['next_hop'] = _next_hop
                route['timestamp'] = time.ticks_ms()

    def clean_routes(self):
        temp_routes = []

        for route in self.routing_table:
            if time.ticks_diff(time.ticks_ms(), route['timestamp']) <= (60 * 1000):
                temp_routes.append(route)

        self.routing_table = temp_routes

    def get_route(self, _destination):
        self.clean_routes()

        for route in self.routing_table:
            if route['destination'] == _destination:
                return route

        return None


class RouteDiscoveryTable:
    def __init__(self):
        self.route_discovery_table = []

    def add_route_discovery(self, _rreq_process_id, _sender_address, _forward_cost, _residual_cost=None):
        self.route_discovery_table.append({
            "rreq_process_id": _rreq_process_id,
            "sender_address": _sender_address,
            "forward_cost": _forward_cost,
            "residual_cost": _residual_cost,
            "expiration_time": time.ticks_ms() + (60 * 1000)  # current time (ms) + 1 min
        })

    def update_route_discovery(self, _rreq_process_id, _source, _forward_cost, _residual_cost):
        for route in self.route_discovery_table:
            if route['rreq_process_id'] in self.route_discovery_table  == _rreq_process_id:
                route['sender_address'] = _source
                route['forward_cost'] = _forward_cost
                route['residual_cost'] = _residual_cost
                route['expiration_time'] = time.ticks_ms() + (60 * 1000)  # current time (ms) + 1 min

    def clean_route_discovery_table(self):
        temp_routes = []

        for route in self.route_discovery_table:
            if time.ticks_diff(time.ticks_ms(), route['expiration_time']) <= (60 * 1000):
                temp_routes.append(route)

        self.route_discovery_table = temp_routes

    def get_route_discovery_entry(self, _rreq_process_id):
        self.clean_route_discovery_table()

        for route in self.route_discovery_table:
            if route['rreq_process_id'] == _rreq_process_id:
                return route

        return None


class Packer:
    @staticmethod
    def pack_frame(type_field, source_addr, destination_addr, path_cost, _id=None, payload=""):
        if _id is None:
            _id = abs(hash(str(source_addr) + str(destination_addr))) % (10 ** 4)

        return struct.pack('bhhhh', type_field, source_addr, destination_addr, path_cost, _id) + payload.encode()

    @staticmethod
    def unpack_frame(_frame):
        type_field, source_addr, destination_addr, path_cost, _id = struct.unpack('bhhhh', _frame[:10])

        return {
            "type_field": type_field,
            "source_addr": source_addr,
            "destination_addr": destination_addr,
            "path_cost": path_cost,
            "id": _id,
            "payload": _frame[10:].decode()
        }


def rreq_process(rdt: RouteDiscoveryTable, rt: RoutingTable, rreq, recv_frame):
    unpacked_rreq = Packer.unpack_frame(rreq)
    old_rreq = rdt.get_route_discovery_entry(unpacked_rreq['id'])

    if not old_rreq:
        # create route discovery table entry
        rdt.add_route_discovery(unpacked_rreq['id'], unpacked_rreq['source_addr'], unpacked_rreq['path_cost'])
    else:
        if old_rreq['forward_cost'] > unpacked_rreq['path_cost']:
            # new RREQ has lower forward costs
            rdt.update_route_discovery(unpacked_rreq['id'], unpacked_rreq['source_addr'], unpacked_rreq['path_cost'], None)

    if xbee.atcmd("MY") == unpacked_rreq['destination_addr']:
        # this node is the destination
        rrep = Packer.pack_frame(RREP_PACKET, unpacked_rreq['source_addr'], unpacked_rreq['destination_addr'], 1)

        xbee.transmit(recv_frame['sender_nwk'], rrep)
    else:
        # this node is a neighbour
        route_to_dest = rt.get_route(unpacked_rreq['destination_addr'])

        if route_to_dest:
            # forward RREQ by unicast transmission
            xbee.transmit(route_to_dest['next_hop'], rreq)
        else:
            # broadcast unpacked_rreq
            xbee.transmit(xbee.ADDR_BROADCAST, rreq)


def rrep_process(rdt: RouteDiscoveryTable, rt: RoutingTable, rrep, recv_frame):
    unpacked_rrep = Packer.unpack_frame(rrep)
    route = rt.get_route(unpacked_rrep['destination_addr'])

    discovery_entry = rdt.get_route_discovery_entry(unpacked_rrep['id'])

    if not route:
        # first RREP in route dicovery process:
        rt.add_route(unpacked_rrep['destination_addr'], recv_frame['sender_nwk'])

        if xbee.atcmd('MY') != COORDINATOR_ADDR:
            rdt.update_route_discovery(discovery_entry['rreq_process_id'], discovery_entry['sender_address'],
                                       discovery_entry['forward_cost'], unpacked_rrep['path_cost'])
    else:
        if xbee.atcmd('MY') != COORDINATOR_ADDR:
            if unpacked_rrep['path_cost'] < discovery_entry['residual_cost']:
                rt.update_route_table(unpacked_rrep['destination_addr'], recv_frame['sender_nwk'])

                rdt.update_route_discovery(discovery_entry['rreq_process_id'], discovery_entry['sender_address'],
                                           discovery_entry['forward_cost'], unpacked_rrep['path_cost'])

    if xbee.atcmd("MY") == unpacked_rrep['source_addr']:
        # TODO: Confirm route establishment
        print("Confirm route establishment")
    else:
        # forward RREP towards source
        new_rrep = Packer.pack_frame(unpacked_rrep['type_field'], unpacked_rrep['source_addr'],
                                     unpacked_rrep['destination_addr'], unpacked_rrep['path_cost'] + 1,
                                     unpacked_rrep['id'])

        xbee.transmit(discovery_entry['sender_address'], new_rrep)


def payload_process(payload_packet):
    unpacked_payload = Packer.unpack_frame(payload_packet)

    if unpacked_payload['destination_addr'] == xbee.atcmd("MY"):
        print("Received from node", unpacked_payload['source_addr'], ":", unpacked_payload['payload'])
    else:
        next_hop_route = routing_table.get_route(DESTINATION_ADDR)
        if next_hop_route:
            xbee.transmit(next_hop_route['next_hop'], payload_packet)
        else:
            print("No route found in routing table for destination", DESTINATION_ADDR)


if __name__ == '__main__':
    routing_table = RoutingTable()
    route_discovery_table = RouteDiscoveryTable()

    print("I'm", xbee.atcmd("NI"))

    MY = xbee.atcmd("MY")
    COOLDOWN = 5000
    cooldown_timer = 0

    TABLE_PRINT_TIMER = 30000
    table_timer = time.ticks_ms()

    while True:
        if MY == COORDINATOR_ADDR:
            # SENDER NODE
            if time.ticks_diff(time.ticks_ms(), cooldown_timer) >= COOLDOWN:
                cooldown_timer = time.ticks_ms()
                _route = routing_table.get_route(DESTINATION_ADDR)

                if _route:
                    # send to next hop
                    print("Send Payload to Destination")
                    print(_route)

                    xbee.transmit(_route['next_hop'],
                                  Packer.pack_frame(PAYLOAD_PACKET, xbee.atcmd("MY"), DESTINATION_ADDR, 0,
                                                    payload="I'm looking for you."))
                else:
                    # start discovering
                    print("Start Discovery")
                    xbee.transmit(xbee.ADDR_BROADCAST, Packer.pack_frame(RREQ_PACKET, xbee.atcmd("MY"), DESTINATION_ADDR, 1))

            received_frame = xbee.receive()
            if received_frame:
                received_type_field = Packer.unpack_frame(received_frame['payload'])['type_field']
                print("Reiceved a RREP")

                print(Packer.unpack_frame(received_frame['payload']))

                if received_type_field == RREP_PACKET:
                    rrep_process(route_discovery_table, routing_table, received_frame['payload'],  received_frame)
        else:
            # NEIGHBOUR NODES
            received_frame = xbee.receive()
            if received_frame:
                received_type_field = Packer.unpack_frame(received_frame['payload'])['type_field']

                print()
                print("**************************************")
                print("sender_nwk", received_frame['sender_nwk'])
                print("----------------")
                print("unpacked frame", Packer.unpack_frame(received_frame['payload']))
                print("**************************************")
                print()

                if received_type_field == RREQ_PACKET:
                    print("Reiceved a RREQ")
                    rreq_process(route_discovery_table, routing_table, received_frame['payload'], received_frame)
                elif received_type_field == RREP_PACKET:
                    print("Reiceved a RREP")
                    rrep_process(route_discovery_table, routing_table, received_frame['payload'], received_frame)
                elif received_type_field == PAYLOAD_PACKET:
                    print("Reiceved a Payload")
                    payload_process(received_frame['payload'])
                else:
                    print(received_frame)
                    raise TypeError("Unexpected type field", received_type_field)

        if time.ticks_diff(time.ticks_ms(), table_timer) >= TABLE_PRINT_TIMER:
            table_timer = time.ticks_ms()
            print()
            print("######################################")
            print("routing_table", routing_table.routing_table)
            print("----------------")
            print("route_discovery_table", route_discovery_table.route_discovery_table)
            print("######################################")
            print()

        routing_table.clean_routes()
        route_discovery_table.clean_route_discovery_table()
