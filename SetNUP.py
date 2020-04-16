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
nup = client.get_options('next-unit-percentage')
if(int(nup) > 90):
    print("NUP is currently %s Setting NUP to 90" % nup)
    client.set_option('next-unit-percentage', '90')
else:
    print("NUP is already at %s" % nup)
