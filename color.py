# \033[1;32m

regular = "\033[0m"

def threat(text):
    return "\033[1;31m" + text + regular

def loot(text):
    return "\033[1;93m" + text + regular

def criticalHealth(text):
    return "\033[1;31m" + text + regular

def lowHealth(text):
    return "\033[1;93m" + text + regular

def fullHealth(text):
    return "\033[1;92m" + text + regular