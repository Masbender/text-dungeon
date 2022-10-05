import os

"""
TABLE OF CONTENTS :

clearCommand - tracks what command to give the system to clear the console

clear_console() - erases all text on the screen using a system command

gather_input(prompt, ) - gathers input by presenting options and requesting a number

"""

# detects the os and selects the appropriate clear command
clearCommand = 'clear'
if os.name in ('nt', 'dos'):
    clearCommand = 'cls'

# used to delete all text on the screen
def clear_console():
  os.system(clearCommand)

# INPUT : prompt (string), options (list), returnInt (bool, optional)
# OUTPUT : provides the player with options and requires an INT as a response, returns index or name of response
def gather_input(prompt, options, returnInt = True):
  # prints and numbers options
  print(prompt)
  for i in range(len(options)):
    print(f"{i}) {options[i]}")

  # gathers input and accounts for user error
  validResponse = False
  while not validResponse:
    playerInput = None
    try:
      playerInput = input("Enter a Number : ")
      playerInput = int(playerInput)

      if playerInput in range(len(options)):
        validResponse = True
      elif playerInput < 0:
        print(f"'{playerInput}' is too small")
      else:
        print(f"'{playerInput}' is too large")
    except ValueError:
      print(f"'{playerInput}' is not an integer")

  clear_console()

  if returnInt:
    return playerInput
  else:
    return options[playerInput]