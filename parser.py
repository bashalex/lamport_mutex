
def parse_arguments(args, logger):
    if len(args) != 8:
        logger.error("Run with 7 arguments:")
        logger.error("\t- id (int)" +
                     "\n\t- port (int)" +
                     "\n\t- list of other ids" +
                     "\n\t- list of other ports" +
                     "\n\t- path to mutex file" +
                     "\n\t- debug (boolean)" +
                     "\n\t- daemon (boolean)")
        logger.error('for example: main.py 0 8800 "1, 2" "8801, 8802" mutex.txt false false')
        raise ValueError
    try:
        id, port = int(args[1]), int(args[2])
    except ValueError:
        logger.error("'id' and 'port' must be integers")
        raise ValueError
    try:
        ids = [int(_id) for _id in args[3].split(",")]
    except ValueError:
        logger.error("wrong 3 argument")
        logger.error("must be in format 'id_1, id_2, ... id_n' where id_i is integer")
        raise ValueError
    try:
        ports = [int(_port) for _port in args[4].split(",")]
    except ValueError:
        logger.error("wrong 4 argument")
        logger.error("must be in format 'port_1, port_2, ... port_n' where port_i is integer")
        raise ValueError
    try:
        with open(args[5], 'w') as f:
            f.write('')  # clean mutex file
            mutex_path = args[5]
    except PermissionError:
        logger.error("can't write to {}".format(args[5]))
        raise ValueError
    debug = args[6].lower()
    if debug == 'false':
        debug = False
    elif debug == 'true':
        debug = True
    else:
        logger.error("6 argument must be boolean")
        raise ValueError
    daemon = args[7].lower()
    if daemon == 'false':
        daemon = False
    elif daemon == 'true':
        daemon = True
    else:
        logger.error("7 argument must be boolean")
        raise ValueError
    return id, port, ids, ports, mutex_path, debug, daemon
