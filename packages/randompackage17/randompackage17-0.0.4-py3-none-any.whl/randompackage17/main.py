import random
import math
# AI made the type checks cause I was lazy
def humanguess(a):
    number = random.randint(1, 1000)
    while True:
        try:
            guess = int(input("Enter a number between 1 and 1000: "))
            break
        except ValueError:
            print("Please enter an integer.")
    while guess != number:
        if guess > number:
            print("Too high")
        if guess < number:
            print("Too low")
        while True:
            try:
                guess = int(input("Enter a number between 1 and 1000: "))
                break
            except ValueError:
                print("Please enter an integer.")
    print("You guessed it!")

def pcguess():
    # Get the target number with validation
    num = int(input("Enter an integer between 1 and 1000: "))
    while True:
        try:
            break
        except ValueError:
            print("Please enter a valid integer.")
    guess = 500
    while guess != num:
        print("My guess is", guess)
        # Get valid feedback
        while True:
            feedback = input("Should I make my guess higher (H), lower (L), or is it correct (C)? ").strip()
            if feedback.lower() in ("h", "l", "c"):
                break
            print("Invalid input. Please enter H, L, or C.")
        # Process feedback
        if guess > num:
            if feedback.lower() == "l":
                guess = math.floor(guess / 2)
            else:
                print("You lied, it's lower.")
                guess = math.floor(guess / 2)
        elif guess < num:
            if feedback.lower() == "h":
                guess = guess + math.floor(guess / 4)
            else:
                print("You lied, it's higher.")
                guess = guess + math.floor(guess / 4)
        else:  # guess == num
            if feedback.lower() == "c":
                print("Yay, I guessed it!")
            else:
                print("You lied, I guessed it.")
