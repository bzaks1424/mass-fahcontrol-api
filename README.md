# mass-fahcontrol-api
Pretty simple really.

Create a client :
```
client = ClientController(
  address='192.168.1.241',
  port=36330,
  password='VMware1!')
```

Then run commands:
```
nup = client.get_options('next-unit-percentage')
if(int(nup) > 90):
    print("NUP is currently %s Setting NUP to 90" % nup)
    client.set_option('next-unit-percentage', '90')
else:
    print("NUP is already at %s" % nup)
```

Every output is either a string or a dict.

The details for how this works are detailed here: https://github.com/FoldingAtHome/fah-control/wiki/3rd-party-FAHClient-API
