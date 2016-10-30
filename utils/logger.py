
class Logger:

    __DEBUG = '\033[92mdebug:'
    __WARNING = '\033[93mwarning:'
    __OK = '\033[96mOK:'
    __ERROR = '\033[91merror:'
    __LOG = '\033[94mlog:'
    __END = '\033[0m'

    def __init__(self, out=None, debug=False, off=False):
        self.out = out
        self.off = off
        if out is not None:
            try:
                with open(out, 'w') as f:
                    f.write('id, logic_time, real_time: event\n')
            except PermissionError:
                self.error('can\'t open file {}'.format(out))
                self.out = None
        self.debug_mode = debug
        if self.debug_mode:
            self.warn('debug mode enabled')

    def error(self, message: str):
        if self.off:
            return
        if self.out is None or self.debug_mode:
            print(self.__ERROR, message, self.__END)
        if self.out is not None:
            with open(self.out, "a") as f:
                f.write("error: " + message + "\n")

    def debug(self, message: str):
        if self.off:
            return
        if self.debug_mode:
            print(self.__DEBUG, message, self.__END)

    def warn(self, message: str):
        if self.off:
            return
        if self.out is None or self.debug_mode:
            print(self.__WARNING, message, self.__END)
        if self.out is not None:
            with open(self.out, "a") as f:
                f.write("warning: " + message + "\n")

    def log(self, message: str, logic_time: int, real_time: int, pid: int):
        if self.off:
            return
        l = "{}, {}, {}: {}".format(pid, logic_time, real_time, message)
        if self.out is None:
            print(self.__LOG, l, self.__END)
            return
        with open(self.out, "a") as f:
            f.write(l + "\n")

    def ok(self, message: str):
        if self.off:
            return
        if self.out is None:
            print(self.__OK, message, self.__END)
            return
        with open(self.out, "a") as f:
            f.write(message + "\n")
