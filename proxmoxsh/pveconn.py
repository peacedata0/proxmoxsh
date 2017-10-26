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
        """Get names of all online nodes of the cluster"""
        cs = self.conn.getClusterStatus()['data']
        nodes = [ n['name'] for n in cs if n['type'] == 'node' and ((('state' in n) and n['state']) or (('online' in n) and n['online'])) ]
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
    def find_vms(self, request, search_in_desc = False):
        """Find virtual machines with stated text in ID or name. Returns dict {node:(VM_status, Description)}"""
        result = {}
        for node in self.node_names():
            vms_of_node = self.node_vms(node)
            results_of_node = []
            for vm in vms_of_node:
                desc = ""
                if search_in_desc:
                    config = self.conn.getVirtualConfig(node, vm)['data']
                    if 'description' in config:
                        desc = config['description']
                if unicode(vm).find(request) != -1 or vms_of_node[vm]['name'].find(request) != -1 or desc.find(request) != -1:
                    results_of_node.append ((vms_of_node[vm], desc))
            if results_of_node:
                result[node] = results_of_node
        return result
    @reconnect_decorator
    def find_vms_of_vlan(self, request):
        """Find virtual machines which have interfaces in stated vlan Returns dict {node:(VM_status, Description)}"""
        result = {}
        for node in self.node_names():
            vms_of_node = self.node_vms(node)
            results_of_node = []
            for vm in vms_of_node:
                config = self.conn.getVirtualConfig(node, vm)['data']
                for param in config:
                    if param.startswith(u'net'):
                        int_params = config[param].split(',')
                        for int_param in int_params:
                            if int_param.strip() == u'tag={}'.format(request):
                                results_of_node.append ((vms_of_node[vm], ""))
            if results_of_node:
                result[node] = results_of_node
        return result
    @reconnect_decorator
    def find_vms_with_mac(self, request):
        """Find virtual machines which have interfaces with stated MAC address. Returns dict {node:(VM_status, Description)}"""
        result = {}
        for node in self.node_names():
            vms_of_node = self.node_vms(node)
            results_of_node = []
            for vm in vms_of_node:
                config = self.conn.getVirtualConfig(node, vm)['data']
                for param in config:
                    if param.startswith(u'net'):
                        int_params = config[param].split(',')
                        mac = int_params[0].strip().split('=')[1]
                        if request.lower() in mac.lower():
                            results_of_node.append ((vms_of_node[vm], ""))
                            break
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
        return node, status, config
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
    @reconnect_decorator
    def cluster_tasks(self):
        """Get cluster tasks"""
        return self.conn.getClusterTasks()['data']




