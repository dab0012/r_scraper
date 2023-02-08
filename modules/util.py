from colorama import Style



# Function to print colored text
def print_colored(text, color ):
    print(color, end="")
    print(text, end="")
    print(Style.RESET_ALL)