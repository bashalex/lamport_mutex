#!/usr/bin/python3
from network import Connection
import sys
import log


def parse_arguments(args):
    id, port, ids, ports = None, None, None, None
    if len(args) != 5:
        log.error("Run with 4 arguments:")
        log.error("\t- id \n\t- port \n\t- list of other ids \n\t- list of other ports")
        log.error('for example: main.py 0 8800 "1, 2" "8801, 8802"')
        exit()
    try:
        id, port = int(args[1]), int(args[2])
    except ValueError:
        log.error("'id' and 'port' must be integers")
        exit()
    try:
        ids = [int(_id) for _id in args[3].split(",")]
    except ValueError:
        log.error("wrong 3 argument")
        log.error("must be in format 'id_1, id_2, ... id_n' where id_i is integer")
        exit()
    try:
        ports = [int(_port) for _port in args[4].split(",")]
    except ValueError:
        log.error("wrong 4 argument")
        log.error("must be in format 'port_1, port_2, ... port_n' where port_i is integer")
        exit()
    return id, port, ids, ports


def run_command(command):
    args = command.split()
    if args[0] == 'send':
        if len(args) != 3:
            log.error("wrong command")
            return
        try:
            recipient_id = int(args[1])
            connection.send(recipient_id, args[2])
        except ValueError:
            log.error("wrong recipientId. Must be integer")
    elif args[0] == 'broadcast':
        if len(args) != 2:
            log.error("wrong command")
        connection.broadcast(args[1])
    elif args[0] == 'exit':
        connection.kill()
        exit(0)
    else:
        log.error("wrong command")


def on_message(message):
    log.log("message received: {}".format(message))

if __name__ == "__main__":
    id, port, ids, ports = parse_arguments(sys.argv)
    connection = Connection(id, port, ids, ports, on_message)
    log.log("You can use following commands:")
    log.log("\t- send recipient_id message")
    log.log("\t- broadcast message")
    log.log("\t- exit")
    while True:
        run_command(input())


