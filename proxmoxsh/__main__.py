#!/usr/bin/python
# -*- coding: utf-8 -*-

from cli import CLI
import logging
logging.basicConfig(level=logging.WARNING)

def main():
    cl = CLI()

if __name__ == "__main__":
    main()

logging.shutdown()
