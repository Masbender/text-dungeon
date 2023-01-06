# \033[1;32m

regular = "\033[0m"

warning = "\033[1;31m"
notification = "\033[1;33m"
good = "\033[1;92m"

# effect has effect as an argument because python tries to input self into them
def effect_good(effect, text):
    return good + text + regular

def effect_neutral(effect, text):
    return notification + text + regular

def effect_bad(effect, text):
    return warning + text + regular


def threat(text):
    return warning + text + regular

def loot(text):
    return notification + text + regular


def harm(text):
    return warning + text + regular


def critical_health(text):
    return warning + text + regular

def low_health(text):
    return notification + text + regular

def full_health(text):
    return good + text + regular

def health_status(health, maxHealth):
# returns green, yellow, or red depending on health
    text = f"{health}/{maxHealth}"
    if health / maxHealth < 0.4:
        return critical_health(text)
    elif health / maxHealth < 0.8:
        return low_health(text)
    else:
        return full_health(text)

def player(text):
    return good + text + regular

def special(text):
    return notification + text + regular


def blessed(text):
    return good + text + regular

def cursed(text):
    return warning + text + regular