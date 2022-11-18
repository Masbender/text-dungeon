# \033[1;32m

regular = "\033[0m"

warning = "\033[1;31m"
notification = "\033[1;93m"
good = "\033[1;92m"

def threat(text):
    return warning + text + regular

def loot(text):
    return notification + text + regular

def criticalHealth(text):
    return warning + text + regular

def lowHealth(text):
    return notification + text + regular

def fullHealth(text):
    return good + text + regular

def player(text):
    return good + text + regular

def special(text):
    return notification + text + regular

def blessed(text):
    return good + text + regular

def cursed(text):
    return warning + text + regular