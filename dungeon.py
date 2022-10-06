from extra import clear_console, gather_input

def update_effects(creature):
# iterates through every effect
    for i in range(len(creature.effects)):
        creature.effects[i].update()
        creature.effectTimers[i] -= 1

    # deletes expired effects
    while 0 in creature.effectTimers:
        effectIndex = creature.effectTimers.index(0)
        creature.effects[effectIndex].reverse()
        
        creature.effectTimers.pop(0)