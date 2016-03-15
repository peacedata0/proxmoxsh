#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pyproxmox

class Pveconn(object):
    """Class for interaction with connection to the Proxmox cluster"""
    def __init__(self, url, username, password):
        self.login(url, username, password)
    def login(self, url, username, password):
        """Connect to the proxmox cluster"""
        prox_auth = pyproxmox.prox_auth(url, username, password)
        pve_conn = pyproxmox.pyproxmox(prox_auth)
        self.conn = pve_conn
    def node_names(self):
        """Get names of all nodes of the cluster"""
        cs = self.conn.getClusterStatus()['data']
        nodes = [ n['name'] for n in cs if n['type'] == 'node' ]
        return nodes
    def node_vms(self, node):
        """Get a list of qemu VMs of the present node. Format is [{<vmid>:{name:<name>,...}}]"""
        vms_list = self.conn.getNodeVirtualIndex(node)['data']
        vms_dict = {}
        for vm in vms_list:
            vms_dict[vm['vmid']] = vm
        return vms_dict
    def find_vms(self, request):
        """Find virtual machines with stated text in ID or name"""
        result = {}
        for node in self.node_names():
            vms_of_node = self.node_vms(node)
            results_of_node = [ vms_of_node[vm] for vm in vms_of_node if unicode(vm).find(request) != -1 or vms_of_node[vm]['name'].find(request) != -1 ]
            if results_of_node:
                result[node] = results_of_node
        return result
    def get_node_of_vm(self, vmid):
        """Find node where VM is running"""
        for node in self.node_names():
            vms_of_node = self.node_vms(node)
            if vmid in vms_of_node:
                return node
    def vm_command(self, command, vmid):
        """Execute simple command for stated VM"""
        return getattr(self.conn, "{}VirtualMachine".format(command))(self.get_node_of_vm(vmid), vmid)
    def migrate(self, vmid, new_node, online=False):
        """Migrate VM to another node"""
        return self.conn.migrateVirtualMachine(self.get_node_of_vm(vmid), vmid, new_node, online=True)


