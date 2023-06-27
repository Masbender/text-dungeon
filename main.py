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
    "Your armor class (AC) decreases the amount of damage you take.",
    "Your inventory size is influenced by your strength (STR).",
    "Your equipment will last longer if you have high intelligence (INT).",
    f"A {c.yellow('scroll of repair')} can make an item more durable than before if you have high intelligence (INT).",
    f"Reading a {c.yellow('scroll of cleansing')} will remove any curses from all items in your inventory and on the current floor."
    +"\nIf your intelligence is high enough, it might even bless a few items!",
    
    "Be on the lookout for secret rooms, most floors have one!",
    f"Just because you don't see a {c.red('!')} doesn't mean there's not an enemy there,\nsome enemies require a higher level of awareness to detect.",
    "You can only sneak past an enemy if you can also detect them.",
    f"Items with a {c.green('(+)')} are blessed and are typically stronger,\nhowever items with a {c.red('(-)')} are cursed, making them weaker.",

    "It's harder to escape from agile enemies.",
    "Your dodge chance also impacts your success chance at escaping combat.",
    "When you escape from enemies they become aware of your presence,\nmaking them harder to sneak by again.",
    f"A {c.yellow('stun bomb')} allows you to escape from any enemy unless they are a boss.",
    
    f"{c.effect(entities.Poisoned)} and {c.effect(entities.Bleeding)} each do 1 damage per turn, but {c.effect(entities.OnFire)} does 2.",
    f"Being {c.effect(entities.Poisoned)} does 1 damage per turn and lowers your strength (STR).",
    f"Being {c.effect(entities.Chilled)} drains 1 health per turn and lowers your dexterity (DEX).",
    f"Being {c.effect(entities.OnFire)} also inflicts you with {c.effect(entities.Burned)}, which lowers your armor class (AC).",
    f"{c.effect(entities.Decay)} lowers your constitution (CON), and becomes stronger over time.",
    "Select \"view stats\" to learn what your current effects do.",
    f"Having {c.effect(entities.BrokenBones)} decreases your strength (STR), constitution (CON), and dexterity (DEX),\nand it can only be cured by a {c.yellow('vial of healing')}.",
    f"Being {c.effect(entities.Dazed)} lowers both your dexterity (DEX) and your perception (PER)."
]

load = False

load_save = input("Load previous save? (y/n) : ").lower()
if load_save == 'y':
    try:
        file1 = open("./player.p", "rb")
        file2 = open("./level.p", "rb")
        file3 = open("./gear.p", "rb")

        entities.player = pickle.load(file1)
        player = entities.player
        items.player = player
        dungeon.player = player
        #dungeon.floors.extend(pickle.load(file2))
        dungeon.floors.append(dungeon.Floor([[dungeon.Collector(), dungeon.Room([items.HealingVial()], [entities.Trickster()])], [dungeon.Wall(), dungeon.Stairs()]], 0, 0))
        gear = pickle.load(file3)
        for index in gear:
            player.inventory[index].equip()
            player.inventory[index].put_on()

        file1.close()
        file2.close()
        file3.close()
    except:
        print("Error while loading save, creating new save instead.")
        load_save = 'n'
else:# load_save == 'n':
    # placeholder character 
    playerInput = gather_input("Choose a character:", ["Guard", "Assassin"], False, False)
    
    if playerInput == "Guard":
        player.inventory.extend([items.Spear(0), items.Armor(0), items.Rations()])
        player.set_stats(1, 1, 0, 2, 0)
        player.inventory[1].consume(None)
        print("You are one of the unlucky few who were in the prison when it turned.\n"
             +"While patrolling the halls you become lost, you encounter unfamiliar rooms\n"
             +"and you cannot seem to find anyone else.\n")
        pause()
    
    if playerInput == "Assassin":
        player.inventory.extend([items.Dagger(0), items.Cloak(), items.Bandage()])
        player.set_stats(0, 0, 2, 1, 1)
        player.inventory[1].consume(None)
        print("You thought that you were a legendary assassin,\n"
              +"so one day you decided to kill the monarch in order to prove your skill.\n"
              +"Needless to say, it didn't work.\n\n"
              +"For your crime, the monarch devised a new and unusual punishment.\n"
              +"You were thrown into the cursed prison, and there is no escape.\n")
        pause()
    
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
    
    dungeon.floors = []
    
    for i in range(6):
        g = dungeon.Generator()
        area = areas[i // 3]
    
        g.initialize_floor(area, i, 4 + ((i + 2) // 3))

        # adds standard encounters
        g.addRooms.append(dungeon.LockedRoom(i))
        g.addItems.extend([items.IronKey(), items.KnowledgeBook()])
    
        if i % 3 == 0:
            message = c.blue({
                "prison":"Welcome to the Dungeon. You have entered the prison, goblin scavengers and the undead roam these halls.",
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
        dungeon.floors.append(g.finalize_floor())
    
        if i == 2: # adds boss
            dungeon.floors.append(dungeon.Floor([[dungeon.Room([items.Rations()], []), dungeon.Room([items.HealingVial()], [entities.Ogre()])], [dungeon.Wall(), dungeon.Stairs()]], 0, 0))
        elif i == 5: # adds boss
            dungeon.floors.append(dungeon.Floor([[dungeon.Collector(), dungeon.Room([items.HealingVial()], [entities.Trickster()])], [dungeon.Wall(), dungeon.Stairs()]], 0, 0))
    # GENERATION END

while True:
    player.floor = None

    player.currentFloor = dungeon.floors[0]
    dungeon.floors[0].enter_floor()
    dungeon.floors.pop(0)

    if player.health <= 0:
        clear_console()
        print("you died")
        break

    elif 0 == len(dungeon.floors):
        clear_console()
        print("thanks for playing")
        break

    for item in player.inventory:
        item.recharge()

    file1 = open("./player.p", "wb")
    file2 = open("./level.p", "wb")
    file3 = open("./gear.p", "wb")

    gear = [] # unequipes gear in the save file (b/c pickles don't like gear) but saves which items were equipped
    for key in player.gear.keys():
        try:
            gear.append(player.inventory.index(player.gear[key]))
            player.gear[key].unequip()
            player.gear[key] = None
        except ValueError:
            pass

    pickle.dump(player, file1)
    pickle.dump(dungeon.floors, file2)
    pickle.dump(gear, file3)

    # re-equips gear
    for index in gear:
        player.inventory[index].equip()
        player.inventory[index].put_on()

    file1.close()
    file2.close()
    file3.close()

    clear_console()
    print(c.blue("Decending..."))
    tip = choice(tips)
    tips.remove(tip)
    slowprint("Tip: " + tip, 0.01)
    pause()