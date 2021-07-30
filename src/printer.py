class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def blue_print(text):
    return bcolors.OKBLUE + text + bcolors.ENDC

def green_print(text):
    return bcolors.OKGREEN + text + bcolors.ENDC

def bold_print(text):
    return bcolors.BOLD + text + bcolors.ENDC
