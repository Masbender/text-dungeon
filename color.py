# \033[1;32m

regular = "\033[0m"

warning = "\033[1;31m"
notification = "\033[1;33m"
good = "\033[1;92m"

# effect____ has effect as an argument because python tries to input self into them
def effectGood(effect, text):
    return good + text + regular

def effectNeutral(effect, text):
    return notification + text + regular

def effectBad(effect, text):
    return warning + text + regular

def threat(text):
    return warning + text + regular

def harm(text):
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