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
* search &lt;request&gt; — find VM by name or ID
* search-d &lt;request&gt; — find VM by name, ID or description (slower than search)
* start &lt;VM ID&gt; — start virtual machine
* stop &lt;VM ID&gt; — stop (force turn off) virtual machine
* shutdown &lt;VM ID&gt; — shutdown (gently turn off) virtual machine
* reset &lt;VM ID&gt; — forse reset virtual machine
* suspend &lt;VM ID&gt; — suspend virtual machine
* resume &lt;VM ID&gt; — resume virtual machine from suspend
* migrate &lt;VM ID&gt; &lt;Destination node&gt; &lt;parameters&gt; — migrate VM to another node
 *  parameters:
 * -online — online migration of running machine
* info &lt;node&gt; — Print information about node
* info &lt;VM ID&gt; — Print information about VM
* setoption &lt;VM ID&gt; &lt;option name&gt &lt;option value&gt;  — set VM configuration option
