#!/usr/bin/env python3
###############################################################################
from datetime import timedelta
from ClientController import ClientController
###############################################################################

# hostname = socket.gethostname()
# hostip = socket.gethostbyname(hostname)
# octets = hostip.split('.')
# slash24 = "%s.%s.%s" % (octets[0],octets[1],octets[2])


# for octet in range(1, 253):
#     tested_ip = "%s.%d" % (slash24, octet)
#     print("Testing %s" % tested_ip)
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.settimeout(0.1)
#     offline = sock.connect_ex((tested_ip, 36330))
#     if(not offline):
#         print("   %s is not offline" % tested_ip)
#         try:
#             sock.close()
#         except Exception:
#             pass


client = ClientController(address='192.168.1.245', password='VMware1!')
slots = client.get_slots()
timeout = timedelta(minutes=15)
for slot in slots:
    if(slot['status'] == "READY"):
        print("Slot is READY, must need to find work to do!")
        slot_type = slot['description'].split(':')[0]
        work_units = client.get_work_by_slot_id(slot['id'])
        for wu in work_units:
            print(wu)
            if(
                wu['state'] == "DOWNLOAD"
                and wu['nextattempt'] > timeout
            ):
                print(client.remove_slot(slot['id']))
                print(client.add_slot(slot_type))
