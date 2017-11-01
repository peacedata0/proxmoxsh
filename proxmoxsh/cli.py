#!/usr/bin/python
# -*- coding: utf-8 -*-
from pveconn import Pveconn
import sys, readline, os
from getpass import getpass
reload(sys)
sys.setdefaultencoding(sys.stdout.encoding)

class CLI(object):
    commands = ["search", "search-d", "search-vlan", "search-mac", "start", "stop", "shutdown", "reset", "suspend", "resume", "migrate", "info", "nodes", "setoption", "tasks"]
    vm_commands = ["start", "stop", "shutdown", "reset", "suspend", "resume"]
    config = {}
    def __init__(self):
        try:
            self.read_config()
        except:
            c = {}
            c['url'] = raw_input(u"Enter server hostname or IP address: ")
            c['username'] = raw_input(u"Enter user name: ")
            c['password'] = getpass(u"Enter password: ")
            self.config['credentials'] = c
        self.pve = Pveconn(**self.config['credentials'])
        if '-c' in sys.argv:
            command = sys.argv[sys.argv.index('-c')+1:]
            self.parse_command(command)
        else:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.complete)
            self.wait()
    def read_config(self):
        """Read config file. Exception is raised if error"""
        with open(os.path.expanduser('~/.config/proxmoxsh/proxmoxsh.conf')) as config:
            self.config = eval(config.read())
        for i in ('url', 'username', 'password'):
            if i not in self.config['credentials']:
                raise Exception(u"Config doesn't contain {}".format(i))
    def wait(self):
        """Wait for enter a command"""
        try:
            while 1:
                command = raw_input(u"> ").strip().decode()
                if command:
                    self.parse_command(command.split())
        except (KeyboardInterrupt, EOFError):
            exit(0)
    def parse_command(self, command):
        """Parse entered command"""
        if command[0] == u'search':
            if len(command) > 1:
                self.search(command[1])
        elif command[0] == u'search-d':
            if len(command) > 1:
                self.search(command[1], search_in_desc=True)
        elif command[0] == u'search-vlan':
            if len(command) > 1:
                self.search(command[1], search_vlan=True)
        elif command[0] == u'search-mac':
            if len(command) > 1:
                self.search(command[1], search_mac=True)
        elif command[0] == u'nodes':
            self.nodes()
        elif command[0] == u"migrate":
            if len(command) >= 3:
                try:
                    print self.migrate(int(command[1]), command[2], command[3:])
                except ValueError:
                    print u"Invalid VM ID"
            else:
                print u"Invalid arguments"
        elif command[0] in self.vm_commands:
            if len (command) == 2:
                try:
                    print self.pve.vm_command(command[0], int(command[1]))
                except ValueError:
                    print u"Invalid VM ID"
            else:
                print u"Invalid arguments"
        elif command[0] == u"info":
            if len(command) > 1:
                if command[1].isdigit():
                    self.vminfo(int(command[1]))
                else:
                    self.nodeinfo(command[1])
            else:
                print u"Invalid arguments"
        elif command[0] == u"setoption":
            if len(command) > 3:
                self.set_option(*command[1:4])
        elif command[0] == u"tasks":
            self.tasks()
        else:
            print u"Invalid command"
    def nodes(self):
        """Print list of nodes"""
        for n in sorted(self.pve.node_names()):
            ns = self.pve.get_node_status(n)
            print u"{}:\tfree {}G of {}G RAM".format(n, ns['memory']['free'] / (1024.0*1024*1024), ns['memory']['total'] / (1024.0*1024*1024))
    def search(self, request, search_in_desc=False, search_vlan=False, search_mac=False):
        """Find virtual machines in cluster"""
        if search_vlan:
            result_dict = self.pve.find_vms_of_vlan(request)
        elif search_mac:
            result_dict = self.pve.find_vms_with_mac(request)
        else:
            result_dict = self.pve.find_vms(request, search_in_desc)
        for srv in sorted(result_dict.keys()):
            print srv, ":"
            for vm, desc in sorted(result_dict[srv], key=lambda vm:vm[0]['vmid']): #order by ID
                if search_mac:
                    print "\t{}\t{}\t{}".format(vm['vmid'], vm['name'], vm['status'])
                    for interface in desc:
                        print "\t\t{}:\t{}".format(interface, desc[interface])
                else:
                    print "\t{}\t{}\t{}\t{}".format(vm['vmid'], vm['name'], vm['status'], desc.strip())
    def migrate(self, vmid, new_node, params):
        parameters = {}
        if u"-online" in params:
            parameters[u'online'] = True
        self.pve.migrate(vmid, new_node, **parameters)
    def nodeinfo(self, node):
        """Get information abount node"""
        print self.pve.get_node_status(node)
    def vminfo(self, vmid):
        """Get information about VM"""
        node, status, options = self.pve.get_vm_info(vmid)
	print "Node:", node
        for r in status:
            print "{}\t\t{}".format(r, status[r])
        print u"\nConfiguration:"
        for r in options:
            print "{}\t\t{}".format(r, options[r])
#        print "Description:"
#        print self.pve.get_desc(vmid)
    def set_option(self, vmid, option, value):
        """Set VM option"""
        print self.pve.set_option(int(vmid), option, value)
    def tasks(self):
        """Print recent tasks"""
        tasks_list = self.pve.cluster_tasks()
        headers = ['starttime', 'endtime', 'node', 'status', 'type', 'upid']
        print '\t'.join(headers)
        for task in tasks_list:
            task_out = [unicode(task[header]) for header in headers]
            print '\t'.join(task_out)
    def complete(self, text, state):
        """Complete current command"""
        if len(readline.get_line_buffer().strip()) == 0 or (len(readline.get_line_buffer().split()) <= 1 and readline.get_line_buffer()[-1] != " "):
            results = [command + " " for command in self.commands if command.startswith(text) ] + [None]
        return results[state]
