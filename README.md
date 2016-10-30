# Lamport Mutex #
## Scripts: ##
### main.py: ###
_Spawn new process in one of two modes: interactive or daemon_

**Arguments:**
  * id (int) - id of new process
  * port (int) - port for socket
  * list of other ids
  * list of other ports
  * path to mutex file
  * debug (boolean)
  * daemon (boolean)

**Example:** ```./main.py 0 8800 "1, 2" "8801, 8802" mutex.txt false true```

### daemons_master.py: ###
_Allow to control spawned daemons_

**Arguments:**
  * command (kill | lock | unlock)
  * pid (int or 'all')

**Example 1:** kill all daemons

```./daemons_master.py kill all```

**Example 2:** Make process with ```id = 1``` lock mutex

```./daemons_master.py lock 1```

**Example 3:** Make process with ```id = 0``` unlock mutex

```./daemons_master.py unlock 0```
