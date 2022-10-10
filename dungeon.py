from extra import clear_console, gather_input
import entities

player = entities.player

def update_effects(creature):
# iterates through every effect
    for i in range(len(creature.effects)):
        creature.effects[i].update()
        creature.effectDurations[i] -= 1

    # deletes expired effects
    while 0 in creature.effectDurations:
        effectIndex = creature.effectDurations.index(0)
        creature.effects[effectIndex].reverse()
        
        creature.effectDurations.pop(0)

class Battle:
    def __init__(self, enemies):
        self.battleOver = False
        self.enemies = enemies

    def start_battle(self):
        clear_console()
        while not self.battleOver:
            self.print_battle()
            self.player_turn()
            clear_console()

            updatedEnemies = []
            for enemy in self.enemies:
                if enemy.health > 0:
                    self.enemy_turn(enemy)
                    updatedEnemies.append(enemy)
            self.enemies = updatedEnemies

    def print_battle(self):
        creatures = self.enemies + [player]

        for creature in creatures:
            print(f"{creature.name.upper()} : {creature.health}/{creature.maxHealth} HP")
            
            effects = []
            for i in range(len(creature.effects)):
                effects.append(f"{creature.effects[i].name} - {creature.effectTimers[i]} turns")

            if len(effects) > 0:
                print(f"[{' | '.join(effects)}]")

            print()
    
    def enemy_turn(self, enemy):
        enemy.do_turn(self.enemies)
        update_effects(enemy)

    def player_turn(self):
        options = []
        for item in player.inventory:
            options.append(item.name)
        
        turnOver = False
        while not turnOver:
            itemUsed = gather_input("What do you use?", options)

            turnOver = player.inventory[itemUsed].attack(self.enemies)

        update_effects(player)
