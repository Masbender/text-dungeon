# \033[1;32m

regular = "\033[0m"

red = "\033[1;31m"
yellow = "\033[1;33m"
green = "\033[1;92m"

blue = "\033[1;36m"

# these functions are give to Effect classes and are called whenever they need to display their name
# effect colors has effect as an argument because python tries to input self into them
def effect_good(effect, text):
    return green + str(text) + regular

def effect_neutral(effect, text):
    return yellow + str(text) + regular

def effect_bad(effect, text):
    return red + str(text) + regular


# compare is primarily used for displaying stats, the color determines if they're being modified or not
def compare(actual, base):
    if actual < base:
        return red + str(actual) + regular
    elif actual > base:
        return green + str(actual) + regular
    else:
        return str(actual)


# threat and loot are used for highlighting information such as items and enemies
def threat(text):
    return red + str(text) + regular

def loot(text):
    return yellow + str(text) + regular

# desc is used for description notifcations, warning is used for notifications that indicate danger
def desc(text):
    return blue + str(text) + regular

def warning(text):
    return red + str(text) + regular


# requires a subclass of Effect, displays the effect with it's appropriate color
def effect(eff):
    return eff.color(eff, eff.name.upper())
# used for attack messages to indicate damage or other negative aspects
def harm(text):
    return red + str(text) + regular

def heal(text):
    return green + str(text) + regular


# used in health_status, determines the color assigned to each status of health
def critical_health(text):
    return red + str(text) + regular

def low_health(text):
    return yellow + str(text) + regular

def full_health(text):
    return green + str(text) + regular

# displays the message of health/maxHealth with appropriate color
def health_status(health, maxHealth):
    text = f"{health}/{maxHealth}"
    if health / maxHealth < 0.40:
        return critical_health(text)
    elif health / maxHealth < 0.75:
        return low_health(text)
    else:
        return full_health(text)


# used to display the player on the map
def player(text):
    return green + str(text) + regular

# used to display unique encounters on the map
def special(text):
    return yellow + str(text) + regular

# used to make ceratin information pop out
def highlight(text):
    return yellow + str(text) + regular

# used when items are cursed or blessed
def blessed(text):
    return green + str(text) + regular

def cursed(text):
    return red + str(text) + regular


# used when shopping
def deal_good(text):
    return green + str(text) + regular

def deal_bad(text):
    return red + str(text) + regular