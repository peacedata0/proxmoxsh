#!/usr/bin/python
# -*- coding: utf-8 -*-
from pveconn import Pveconn
import sys, readline, os
from getpass import getpass
reload(sys)
sys.setdefaultencoding(sys.stdout.encoding)

class CLI(object):
    commands = ["search", "start", "stop", "shutdown", "reset", "suspend", "resume", "migrate"]
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
        else:
            print u"Invalid command"
    def search(self, request):
        """Find virtual machines in cluster"""
        result_dict = self.pve.find_vms(request)
        for srv in sorted(result_dict.keys()):
            print srv, ":"
            for vm in sorted(result_dict[srv], key=lambda vm:vm['vmid']): #order by ID
                print "{}\t{}\t{}".format(vm['vmid'], vm['name'], vm['status'])
    def migrate(self, vmid, new_node, params):
        parameters = {}
        if u"-online" in params:
            parameters[u'online'] = True
        self.pve.migrate(vmid, new_node, **parameters)
    def complete(self, text, state):
        """Complete current command"""
        if len(readline.get_line_buffer().strip()) == 0 or (len(readline.get_line_buffer().split()) <= 1 and readline.get_line_buffer()[-1] != " "):
            results = [command + " " for command in self.commands if command.startswith(text) ] + [None]
#        if readline.get_line_buffer().split()[0] in ("start", "stop"):
#            results = ['test1', 'test2', None]
        return results[state]
