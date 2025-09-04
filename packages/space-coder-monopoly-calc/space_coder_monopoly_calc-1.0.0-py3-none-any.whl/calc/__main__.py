print("Starting!\n\n")

import os
import time
import re
from tabulate import tabulate

''' The Castle Game's Official Calculator, keeps track of items each player currently has.'''

os_is_windows = True if os.name == 'nt' else False

if os_is_windows:
    os.system("color")

player_names = []
player_count = 0
players = {}            # Holds all the player information
enable_gems = False

colors = {
    "BLACK": '\033[30m',
    "RED": '\033[31m',
    "GREEN": '\033[32m',
    "YELLOW": '\033[33m',
    "BLUE": '\033[1;34m',
    "MAGENTA": '\033[35m',
    "CYAN": '\033[36m',
    "WHITE": '\033[37m',
    "RESET": '\033[0m',
    "HEADER": '\033[95m',
    "BOLD": '\033[1m',
    "UNDERLINE": '\033[4m'
}


def print_special(*items, color="RESET", end="\n"):
    print(colors[color], end="")

    for item in items:
        print(item, end=" ")

    print(colors["RESET"], end=end)

def print_red(*items, end="\n"):
    for item in items:
        print_special(item, color="RED", end=" ")
    
    print("", end=end)

def print_blue(*items, end="\n"):
    for item in items:
        print_special(item, color="BLUE", end=" ")
    
    print("", end=end)

def print_green(*items, end="\n"):
    for item in items:
        print_special(item, color="GREEN", end=" ")
    
    print("", end=end)

def print_underlined(*items, end="\n"):
    for item in items:
        print_special(item, color="UNDERLINE", end=" ")

    print("", end=end)


def print_bold(*items, end="\n"):
    for item in items:
        print_special(item, color="BOLD", end=" ")

    print("", end=end)


def clear(wait=0):
    time.sleep(wait)
    if os_is_windows:
        os.system("cls")
    else:
        os.system("clear")

def name_case(input_str):
    output = input_str.lower()
    output = list(output)
    output[0] = output[0].upper()
    output = "".join(output)
    return output

def confirm(item, if_true=None, if_false=None, skippable=False):
    to_be_tested = input("Confirm: ")

    if skippable and to_be_tested == "":
        return True
   
    if to_be_tested.upper() == item.upper():
        match = True
    else:
        match = False

    if match:
        if if_true != None:
            print_green(if_true)
        return True
    
    if if_false != None:
        print_red(if_false)
    return False

def get_player_count():
    try:
        player_count = int(input("Enter the number of players >>>   "))
        if player_count < 1:
            print_red("That looks wrong. Please try again...")
            clear(2)
            return get_player_count()
        print_green("ok")
        clear(0.5)
        return player_count
    
    except ValueError:
        print_red("ERROR: Must be a whole number. Please try again...")
        clear(3)
        return get_player_count()

def get_setup_info():
    global enable_gems
    try:
        player_count = get_player_count()

        for player_number in range(player_count):
            item_to_be_appended = input(f"Enter Player {player_number + 1}'s Name >>>   ")

            while not confirm(item_to_be_appended, if_false='ERROR: Please Try Again\n',skippable=True):
                time.sleep(1)
                clear()
                item_to_be_appended = input(f"Enter Player {player_number + 1}'s Name >>>   ")

            player_names.append(name_case(item_to_be_appended))
            players[name_case(item_to_be_appended)] = {"money": 0}
            clear(0.3)

        print(f"Here are the {player_count} players: ", end="")
        for player in player_names:
            print(player, end='',)
            if player != player_names[-1]:
                print(", ", end='')

        print()
        clear(1 + player_count * 0.3)

        castle_game =  input("Are you playing monopoly? (y/n) >>>   ")
        castle_game = False if castle_game == "y" else True

        if castle_game == True:
            enable_gems = True
        else:
            for player_name in player_names:
                players[player_name]["money"] = 1500

        clear(0.2)

        print_green("Setup Complete!")
        clear(1)

    except KeyboardInterrupt:
        print_red("\n\nSTOPPING")
        clear(0.2)
        exit()


def draw_money_table():
    headers = ["Player", "Money"]
    data = []
    for item in players:
        data.append([item, f"${players[item]["money"]}"])

    print_blue(tabulate(data, headers=headers, tablefmt="grid"))


def main():
    try:
        clear()
        get_setup_info()
        player_names.sort()
        player_names_str = "|".join(player_names)
        player_names_str = player_names_str.upper()
        #print(player_names_str)

        money = "MONEY|MOENY|ONEY"

        draw_money_table()

        while True:
            print_bold('\ncmd >>>', end="")
            cmd = input("  ")

            clear()

            draw_money_table()
            print_bold('\ncmd >>>', end="  ")
            print(cmd)

            cmd = cmd.upper()


            if "C:/USERS/" in cmd:
                print_red("STOPPING!")
                exit()

            active_player = re.findall(player_names_str, cmd)

            if len(active_player) != 1:
                if len(active_player) == 0:
                    active_player = None
                elif len(active_player) > 1:
                    print_red("You mentioned more than one player. Please try again...")
            else:
                active_player = name_case(active_player[0])

            if not active_player:
                if re.findall("LIST", cmd):
                    if re.findall("PLAYER", cmd):
                        input("Current Players Are: " + ", ".join(player_names) + "   (Press enter to continue)")
                        clear()
                        continue
                print_red("umm... that doesn't look right")
                continue

            if active_player == None:
                print_red("Could not find a player name in command...")
                continue
            
            #cmd = input(f"Action for {active_player} to perform >>>   ")

            numbers = re.findall("\d", cmd)

            try:
                numbers = int("".join(numbers))
            except ValueError:
                numbers = "N/A"
            
            action = ""
            cmds = re.findall("INCREASE|DECREASE|LIST|SET|WHAT|HOW MUCH|ADD|PASSED GO", cmd)

            if len(cmds) != 1:
                print_red(f"Failed... Detected {len(cmds)} commands")
                continue

            cmds = cmds[0]

            if cmds == "INCREASE" or cmds == "ADD":
                if numbers != "N/A":
                    if re.findall(money, cmd):
                        action = "increase money"
                    else:
                        print_red("Could not find what to increase")
                        continue
                else:
                    print_red(f"Could not find a number to increase {active_player}'s money by")
                    continue

            if cmds == "DECREASE":
                if numbers != "N/A":
                    if re.findall(money, cmd):
                        action = "decrease money"
                    else:
                        print_red("Could not find what to decrease")
                        continue
                else:
                    print_red(f"Could not find a number to decrease {active_player}'s money by")
                    continue


            if cmds == "LIST":
                if re.findall(money, cmd):
                    action = "list money"
                else:
                    print_red("Could not find what to list")
                    continue

            if cmds == "SET":
                if numbers != "N/A":
                    if re.findall(money, cmd):
                        action = "set money"
                    else:
                        print_red("Could not find what to set")
                        continue
                else:
                    print_red(f"Could not find a number to increase {active_player}'s money by")
                    continue

            if cmds == "WHAT":
                if re.findall(money, cmd):
                    action = "list money"
                else:
                    print_red("Could not find what to display / list")
                    continue

            if cmds == "HOW MUCH":
                if re.findall(money, cmd):
                    action = "list money"
                else:
                    print_red("Could not find what to list")
                    continue

            if cmds == "PASSED GO":
                action = 'passed go'



            if action == "increase money":
                players[active_player]["money"] += numbers
                print_green(f"Increased {active_player}'s money by ${numbers} to ${players[active_player]["money"]}")
            elif action == "decrease money":
                players[active_player]["money"] -= numbers
                print_green(f"Decreased {active_player}'s money by ${numbers} to ${players[active_player]["money"]}")
            elif action == "list money":
                print_green(f"{active_player} has ${players[active_player]["money"]}")
            elif action == "set money":
                players[active_player]["money"] = numbers
                print_green(f"Set {active_player}'s money to ${numbers}")
            elif action == 'passed go':
                players[active_player]["money"] += 200
                print_green(f'Increased {active_player}\'s money by $200 to ${players[active_player]["money"]}')
            else:
                print_red(f"No command detected for player {active_player}")
                #print(cmd, action)
    
    except KeyboardInterrupt:
        print_red("STOPPING")
        clear(0.2)


if __name__ == "__main__":
    main()