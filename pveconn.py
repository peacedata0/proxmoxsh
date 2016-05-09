#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pyproxmox
import logging

class Pveconn(object):
    """Class for interaction with connection to the Proxmox cluster"""
    def __init__(self, url, username, password):
        self.url, self.username, self.password = url, username, password
        self.login()
    def login(self):
        """Connect to the proxmox cluster"""
        prox_auth = pyproxmox.prox_auth(self.url, self.username, self.password)
        pve_conn = pyproxmox.pyproxmox(prox_auth)
        self.conn = pve_conn
    def reconnect_decorator(function):
        """Reconnect and retry if exception raised"""
        def reconnect(self, *args, **kwargs):
            try:
                return function(self, *args, **kwargs)
            except:
                logging.info("Trying to reconnect")
                self.login()
                return function(self, *args, **kwargs)
        return reconnect
    @reconnect_decorator
    def node_names(self):
        """Get names of all nodes of the cluster"""
        cs = self.conn.getClusterStatus()['data']
        nodes = [ n['name'] for n in cs if n['type'] == 'node' ]
        return nodes
    @reconnect_decorator
    def node_vms(self, node):
        """Get a list of qemu VMs of the present node. Format is [{<vmid>:{name:<name>,...}}]"""
        vms_list = self.conn.getNodeVirtualIndex(node)['data']
        vms_dict = {}
        for vm in vms_list:
            vms_dict[vm['vmid']] = vm
        return vms_dict
    @reconnect_decorator
    def find_vms(self, request):
        """Find virtual machines with stated text in ID or name"""
        result = {}
        for node in self.node_names():
            vms_of_node = self.node_vms(node)
            results_of_node = [ vms_of_node[vm] for vm in vms_of_node if unicode(vm).find(request) != -1 or vms_of_node[vm]['name'].find(request) != -1 ]
            if results_of_node:
                result[node] = results_of_node
        return result
    @reconnect_decorator
    def get_node_of_vm(self, vmid):
        """Find node where VM is running"""
        for node in self.node_names():
            vms_of_node = self.node_vms(node)
            if vmid in vms_of_node:
                return node
    @reconnect_decorator
    def vm_command(self, command, vmid):
        """Execute simple command for stated VM"""
        return getattr(self.conn, "{}VirtualMachine".format(command))(self.get_node_of_vm(vmid), vmid)
    @reconnect_decorator
    def migrate(self, vmid, new_node, online=False):
        """Migrate VM to another node"""
        return self.conn.migrateVirtualMachine(self.get_node_of_vm(vmid), vmid, new_node, online=True)
    @reconnect_decorator
    def get_node_status(self, node):
        """Get node status"""
        return self.conn.getNodeStatus(node)['data']
    @reconnect_decorator
    def get_vm_info(self, vmid):
        """Get VM status"""
        node = self.get_node_of_vm(vmid)
        status = self.conn.getVirtualStatus(node, vmid)['data']
        config = self.conn.getVirtualConfig(node, vmid)['data']
        return status, config
    def get_desc(self, vmid):
        """Get description of VM"""
        return self.get_config(vmid)['description']
    @reconnect_decorator
    def get_config(self, vmid):
        """Get config of VM"""
        return self.conn.getVirtualConfig(self.get_node_of_vm(vmid), vmid)['data']
    @reconnect_decorator
    def set_option(self, vmid, option, value):
        """Set VM option"""
        return self.conn.setVirtualMachineOptions(self.get_node_of_vm(vmid), vmid, {option: value})



