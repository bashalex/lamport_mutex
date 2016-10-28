
__OK = '\033[92mok:'
__WARNING = '\033[93mwarning:'
__ERROR = '\033[91merror:'
__END = '\033[0m'


def error(message: str):
    print(__ERROR, message, __END)
    

def ok(message: str):
    print(__OK, message, __END)
    
    
def warning(message: str):
    print(__WARNING, message, __END)
    

def log(message: str):
    print(message)
