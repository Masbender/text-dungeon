# \033[1;32m

regular = "\033[0m"
"""
red = "\033[1;31m" # danger, enemies, bad, damage
yellow = "\033[1;33m" # loot, gold
green = "\033[1;92m" # good, healing
blue = "\033[1;36m" # descriptive, player
purple = "\033[1;35m" # story
"""

# used for enemies, to highlight damage, and for negative events, things, and effects
def red(text):
    return "\033[1;31m" + str(text) + regular

# used to highlight loot, loot providing encounters, or as a transition from green to red
def yellow(text):
    return "\033[1;33m" + str(text) + regular

# used for beneficial effects and to highlight healing or other positive things
def green(text):
    return "\033[1;92m" + str(text) + regular

# used to highlight speech, descriptive text, or mysterious encounters
def blue(text):
    return "\033[1;36m" + str(text) + regular

# used for gods and powerful effects
def purple(text):
    return "\033[1;35m" + str(text) + regular

# these functions are give to Effect classes and are called whenever they need to display their name
# effect colors has effect as an argument because python tries to input self into them
def effect_good(effect, text):
    return green(text)

def effect_neutral(effect, text):
    return yellow(text)

def effect_bad(effect, text):
    return red(text)

def effect_great(effect, text):
    return purple(text)

# compare is primarily used for displaying stats, the color determines if they're being modified or not
def compare(actual, base):
    if actual < base:
        return red(actual)
    elif actual > base:
        return green(actual)
    else:
        return str(actual)

# requires a subclass of Effect, displays the effect with it's appropriate color
def effect(eff):
    return eff.color(eff, eff.name.upper())


# used in health_status, determines the color assigned to each status of health
def critical_health(text):
    return red(text)

def low_health(text):
    return yellow(text)

def full_health(text):
    return green(text)

# displays the message of health/maxHealth with appropriate color
def health_status(health, maxHealth):
    text = f"{health}/{maxHealth}"
    if health / maxHealth < 0.40:
        return critical_health(text)
    elif health / maxHealth < 0.75:
        return low_health(text)
    else:
        return full_health(text)