import os
from time import sleep

"""
TABLE OF CONTENTS :

clearCommand - tracks what command to give the system to clear the console

clear_console() - erases all text on the screen using a system command

gather_input(prompt, ) - gathers input by presenting options and requesting a number

"""

# if on a slow machine it doesn't slow print
doSlowPrint = True
if input("Optimize performance? (y/n): ").lower() == 'y':
    doSlowPrint = False
    
# detects the os and selects the appropriate clear command
clearCommand = 'clear'
if os.name in ('nt', 'dos'):
    clearCommand = 'cls'

def clear_console():
# used to delete all text on the screen
    os.system(clearCommand)

def gather_input(prompt, options, returnInt = True):
# INPUT : prompt (string), options (list), returnInt (bool, optional)
# OUTPUT : provides the player with options and requires an INT as a response, returns index or name of response
    # prints and numbers options
    slowprint(prompt, .004)
    for i in range(len(options)):
        slowprint(f"[{i + 1}] {options[i]}", .004)

  # gathers input and accounts for user error
    validResponse = False
    while not validResponse:
        playerInput = None
        try:
            playerInput = input("Enter a Number : ")
            playerInput = int(playerInput) - 1
        
            if playerInput in range(len(options)):
                validResponse = True
            elif playerInput < 0:
                print(f"'{playerInput}' is too small")
            else:
                print(f"'{playerInput}' is too large")
        except ValueError:
            print(f"'{playerInput}' is not a number")

    clear_console()

    if returnInt:
        return playerInput
    else:
        return options[playerInput]

# prints text slower
def slowprint(text, speed=.03):
    if doSlowPrint:
        for letter in text:
            print(letter, end="", flush=True)
            sleep(speed)
        print()
    else:
        print(text)

# break between output
def separator(end="\n"):
    print("----------------------------------------", end=end)