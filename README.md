# proxmoxsh
Command line utility for managing Proxmox VE
The goal of the project is create more convinient than pvesh utility for managing Proxmox VE cluster
## Requirements
* Python 2 (tested on 2.7)
* pyproxmox (https://github.com/Daemonthread/pyproxmox)

## License
GPLv2 or later

## Howto
Currently supported commands:
* search <request> — find VM by name or ID
* start <VM ID> — start virtual machine
* stop <VM ID> — stop (force turn off) virtual machine
* shutdown <VM ID> — shutdown (gently turn off) virtual machine
* reset <VM ID> — forse reset virtual machine
* suspend <VM ID> — suspend virtual machine
* resume <VM ID> — resume virtual machine from suspend
* migrate <VM ID> <Destination node> <parameters> — migrate VM to another node
* parameters:
** -online — online migration of running machine
