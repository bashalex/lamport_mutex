# Lamport Mutex #

### settings.py ###
Contains paths to the directories.
These directories must exist!

**Default:** ```./pids``` for daemons pids and ```./logs``` for logs
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
  * stress_mode (boolean)

**Example:** ```./main.py 0 8800 "1, 2" "8801, 8802" mutex.txt false true false```

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

### log_checker.py: ###

Run without arguments.
Check correctness of logs

## Tests ##
**run tests:** ```python3 -W ignore -m unittest tests/test_API.py tests/test_mutex.py```
