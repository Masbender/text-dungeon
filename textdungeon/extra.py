import os
from time import sleep

"""
TABLE OF CONTENTS :

messages - used to store messages that'll be printed to the screen

add_message(message) - adds a message to messages

print_messages - prints and clears messages

clearCommand - tracks what command to give the system to clear the console

clear_console() - erases all text on the screen using a system command

gather_input(prompt, options, startAtZero, returnInt) - gathers input by presenting options and requesting a number

slowprint(text, speed = .03) - prints the text one character at a time, with speed seconds in-between characters

separator() - prints a long line of '-' to separate sections of text

pause() - prompts the user to press enter to continue, erases prompt but not previous text afterwards

"""

messages = [] # this is here because it needs to be accessed by all other files

# this exists b/c things in extra are imported separately and I don't want to have a var named messages in other files (too common)
def add_message(message):
    messages.append(message)

def print_messages():
    if len(messages) > 0:
        for message in messages:
            print(message)

        messages.clear()

        print()

# if on a slow machine it doesn't slow print
doSlowPrint = True
#if input("Optimize performance? (y/n): ").lower() == 'y':
 #   doSlowPrint = False
    
# detects the os and selects the appropriate clear command
clearCommand = 'clear'
if os.name in ('nt', 'dos'):
    clearCommand = 'cls'

def clear_console():
# used to delete all text on the screen
    os.system(clearCommand)

def gather_input(prompt, options, startAtZero = False, returnInt = True):
# INPUT : prompt (string), options (list), returnInt (bool, optional)
# OUTPUT : provides the player with options and requires an INT as a response, returns index or name of response
    # prints and numbers options
    print(prompt)
    for i in range(len(options)):
        print(f"[{i + int(not startAtZero)}] {options[i]}")

  # gathers input and accounts for user error
    validResponse = False
    while not validResponse:
        playerInput = None
        try:
            playerInput = input("Enter a Number : ")
            playerInput = int(playerInput) - int(not startAtZero)
        
            if playerInput in range(len(options)):
                validResponse = True
            elif playerInput < 0:
                print(f"'{playerInput + int(not startAtZero)}' is too small")
            else:
                print(f"'{playerInput + int(not startAtZero)}' is too large")
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

def pause():
    input("- PRESS ENTER -")
    print("\033[1A\033[K", end="")

# break between output
def separator(end="\n"):
    print("----------------------------------------", end=end)