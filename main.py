import dungeon
import entities
from extra import clear_console, slowprint
from extra import gather_input, pause
import items
import color
from random import randint, choice
import pickle

player = entities.player
c = color

tips = [
    "Armor class (AC) decreases the amount of damage you take.",
    "Your inventory size is influenced by your strength (STR).",
    "Your equipment will last longer if you have high intelligence (INT).",
    "You can't sneak past an enemy unless you can detect them.",
    f"Be careful, if you pick up a cursed item {c.red('(-1)')}, you can't drop it.",
    f"Just because you don't see a {c.red('!')} doesn't mean there's not an enemy there,\nsome enemies require a higher level of awareness to detect.",
    f"Both {c.effect(entities.Poisoned)} and {c.effect(entities.Bleeding)} drain 1 health per turn, but {c.effect(entities.OnFire)} drains 2.",
    f"Being {c.effect(entities.Poisoned)} drains 1 health per turn and lowers your strength (STR).",
    f"Being {c.effect(entities.OnFire)} also inflicts you with {c.effect(entities.Burned)}, which lowers your armor class (AC).",
    f"{c.effect(entities.Decay)} lowers your constitution (CON), and becomes stronger over time.",
    "Select \"view stats\" to learn what your current effects do.",
    f"Having {c.effect(entities.BrokenBones)} decreases your strength (STR), constitution (CON), and dexterity (DEX),\nand it can only be cured by a {c.yellow('vial of healing')}."
]

load = False
floors = []

load_save = input("Load previous save? (y/n) : ").lower()
if load_save == 'y':
    try:
        file1 = open("player.p", "rb")
        file2 = open("level.p", "rb")
        entities.player = pickle.load(file1)
        player = entities.player
        items.player = player
        dungeon.player = player
        floors = pickle.load(file2)
        file1.close()
        file2.close()
    except:
        print("Error while loading save, creating new save instead.")
        load_save = 'n'
if load_save == 'n':
    # placeholder character 
    playerInput = gather_input("Choose a character:", ["Guard", "Thief"], False, False)
    
    introMessage = ""
    
    if playerInput == "Guard":
        player.inventory.extend([items.Spear(0), items.HeavyArmor(0), items.Rations()])
        player.set_stats(1, 1, 0, 2, 0)
        player.inventory[1].consume(None)
        introMessage = "While patrolling the halls of the Prison you become lost, the halls feel like a maze and you cannot find the way back."
    
    if playerInput == "Thief":
        player.inventory.extend([items.Dagger(0), items.Cloak(), items.Bandage()])
        player.set_stats(0, 0, 2, 1, 1)
        player.inventory[1].consume(None)
        introMessage = "You manage to escape your cell, but you soon become lost in the halls of the Prison."

    if playerInput == "Assassin":
        player.inventory.extend([items.Dagger(1), items.Cloak(), items.StunBomb()])
        player.inventory[1].consume(None)
        player.inventory[0].uses = 10
        player.set_stats(0, -1, 2, 0, 1)
        introMessage = "You have only recently been thrown into the cursed prison, yet all fresh air has already disappeared."
    
    if playerInput == "Sorcerer":
        player.inventory.extend([items.Mace(0), items.MagicRobe(), items.PoisonWand()])
        player.inventory[2].enchantment += 1
        player.set_stats(-1, 0, 1, 0, 3)
        player.inventory[1].consume(None)
    
    dungeon.sort_inventory()
    
    # GENERATION START
    goldKeyLocation = randint(0, 2)
    floodedFloor = randint(4, 5)
    
    areas = ["prison", "crossroads", "stronghold"]
    
    floors = []
    
    for i in range(6):
        g = dungeon.Generator()
        area = areas[i // 3]
    
        g.initialize_floor(area, i, 4 + ((i + 2) // 3))

        # adds standard encounters
        g.addRooms.append(dungeon.LockedRoom(i))
        g.addItems.extend([items.IronKey(), items.KnowledgeBook(), items.ScrollEnchant()])
    
        if i % 3 == 0:
            message = c.blue({
                "prison":"Welcome to the Dungeon. " + introMessage,
                "crossroads":"You have entered the Crossroads. The halls are sewer like and the sounds of rats are everywhere."
            }[area] + "\n")
            g.entryMessage = message + g.entryMessage
    
        if i == goldKeyLocation: # adds gold key
            g.addItems.append(items.GoldKey())
        
        if i % 3 == 1: # adds shops
            g.addRooms.append(dungeon.Shop(i))
    
        elif i % 3 == 2: # adds gold chest
            g.addRooms.append(dungeon.Chest(i))
            goldKeyLocation = i + randint(1, 3)

        if i == floodedFloor:
            g.modifier = "flooded"

        if i == 3:
            g.addRooms.append(dungeon.Chasm())

        g.generate_floor()
        floors.append(g.finalize_floor())
    
        if i % 3 == 2: # adds boss
            floors.append(dungeon.Floor([[dungeon.Room([items.Rations()], []), dungeon.Room([items.HealingVial()], [entities.Ogre()])], [dungeon.Wall(), dungeon.Stairs()]], 0, 0))
    # GENERATION END

while True:
    player.floor = None
    file1 = open("player.p", "wb")
    file2 = open("level.p", "wb")
    pickle.dump(player, file1)
    pickle.dump(floors, file2)
    file1.close()
    file2.close()

    player.currentFloor = floors[0]
    floors[0].enter_floor()
    floors.pop(0)

    if player.health <= 0:
        clear_console()
        print("you died")
        break

    elif 0 == len(floors):
        clear_console()
        print("thanks for playing")
        break

    for item in player.inventory:
        item.recharge()

    clear_console()
    print("Decending...")
    slowprint("Tip: " + choice(tips), 0.01)
    pause()