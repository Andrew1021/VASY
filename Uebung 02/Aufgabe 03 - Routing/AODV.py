# while True
#     if sending mode:
#         if the destination node is in the route discovery table:
#             # get it from the table
#         else:
#             # Route to destination does not exist
#             # Broadcasting RREQ
#     elif receiving mode:
#         while True:
#             if packet is RREQ:
#                 if originator of RREQ is already in route discovery table or originator is receiving RREQ back to itself:
#                     # RREQ discarded
#                 else:
#                     if not in route discovery table or not originator itself:
#                         # # add reverse entry in route table
#                     elif destination exists in route discovery table:
#                         # get routing entry back
#                     else: # routing entry is to be updated
#                         if destination is reached:
#                             # send data to Next_hop that leads to destination
#                         else: # Route to destination does not exist
#                             # incrementing hop count
#                             # broadcasting RREQ to neighbours
#             elif packet is RREP:
#                 if node exists in the route table:
#                     if hop count in routing table > als hop count of packet:
#                         # remove table entry and append new entry with data form packet
#                     else:
#                         # if entry not found append new entry
#                     if RREP is reached at originator of RREQ: # means route found
#                         # send data to Next_hop that leads to destination
#                     else:
#                         # hop count incrementing
#                         # send data to Next_hop that leads to destination
#             elif packet is DATA:
#                 if data packet is received at destination:
#                     # print msg
#                     # send data to Next_hop that leads to originator of data msg
#                 else: # if data packet is received at intermediate node (not at destination)
#                     if node exists in the route table:
#                         # print that forwarding data_msg to next hop
#                         # send the same msg to next hop that leads to destination
#                     else:
#                         # Error message