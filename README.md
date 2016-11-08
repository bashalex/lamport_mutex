# Lamport Mutex #

### settings.py ###
_Contains paths to the directories.
These directories must exist!_

**Default:** ```./pids``` for daemons pids and ```./logs``` for logs
## Scripts: ##
### main.py: ###
_Spawns new process in one of two modes: interactive or daemon_

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
_Allows to control spawned daemons_

**Arguments:**
  * command (kill | lock | unlock)
  * pid (int or 'all')

**Example 1:** kill all daemons

```./daemons_master.py kill all```

**Example 2:** Make process with ```id = 1``` lock mutex

```./daemons_master.py lock 1```

**Example 3:** Make process with ```id = 0``` unlock mutex

```./daemons_master.py unlock 0```

### stress_test.py: ###
_Runs stress test with ```n``` processes for ```s``` seconds_

_A lot of logger errors in the beginning of the test it's ok._
_They happens while not all of processes are spawned_

**Arguments:**
  * n (int) - number of processes
  * s (int) - time of execution

**Example:** ```./stress_test.py 10 15```


### log_checker.py: ###

_Run without arguments.
Checks correctness of logs_

## Tests ##
**run unit tests:** ```python3 -W ignore -m unittest tests/test_API.py tests/test_mutex.py```
