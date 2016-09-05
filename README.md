# proxmoxsh
Command line utility for managing Proxmox VE
The goal of the project is create more convinient than pvesh utility for managing Proxmox VE cluster
## Requirements
* Python 2 (tested on 2.7)
* pyproxmox (https://github.com/Daemonthread/pyproxmox)

## License
GPLv2 or later

## Howto
Create config file $HOME/.config/proxmoxsh/proxmoxsh.conf containing:

{'credentials':
 {'url':'NODE_URL',
  'username':'USER@REALM',
  'password':'PASSWORD'},
}

REALM may be "pam" or "pve".

If file doesn't exist you will be asked for credentials.

Currently supported commands:
* search *request* — find VM by name or ID
* search-d *request* — find VM by name, ID or description (slower than search)
* search-vlan *vlan_tag* — find vm that has interface with entered vlan tag 
* start *VM ID* — start virtual machine
* stop *VM ID* — stop (force turn off) virtual machine
* shutdown *VM ID* — shutdown (gently turn off) virtual machine
* reset *VM ID* — forse reset virtual machine
* suspend *VM ID* — suspend virtual machine
* resume *VM ID* — resume virtual machine from suspend
* migrate *VM ID* *Destination node* *parameters* — migrate VM to another node
 *  parameters:
 * -online — online migration of running machine
* info *node* — Print information about node
* info *VM ID* — Print information about VM
* setoption *VM ID* *option name* *option value*  — set VM configuration option

You can launch proxmoxsh without arguments and enter commands interactively or launch proxmoxsh with "-c command" arguments.
