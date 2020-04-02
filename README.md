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
nup = client.send('option next-unit-percentage')
if(nup != "90"):
    print("NUP is not 90, setting to 90")
    nup = client.send('option next-unit-percentage 90')
print(client.send('option next-unit-percentage'))
```

Every output is either a string or a dict. 

The details for how this works are detailed here: https://github.com/FoldingAtHome/fah-control/wiki/3rd-party-FAHClient-API
