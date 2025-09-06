"""
Pegol CLI package
Made by Pegol Reda Shokry
This package prints a fun message and a heart animation when 'pegolpro' is typed.
"""

__version__ = "0.1.0"  # لازم النسخة دي موجودة

import time
import random

def main():
    print("Hello, thanks for installing pegol! It was made by Pegol Reda Shokry.")
    user_input = input('Type "pegolpro" for fun: ')
    
    if user_input.strip().lower() == "pegolpro":
        print("🎉 You typed pegolpro! Fun activated!\n")
        # الرسائل
        message = "The World's Most Powerful Congratulation!"
        sub_message = "Wish you endless joy and love ♥"
        name = "From Pegol"
        print(message)
        print(sub_message)
        print(name)
        print()
        
        # animation بسيط بالقلب
        hearts = ["♥", "♡", "♣", "♦", "♠"]
        for _ in range(20):
            print(" ".join(random.choice(hearts) for _ in range(40)))
            time.sleep(0.1)
        
        print("\nThanks for watching! ♥")
    else:
        print("You didn't type pegolpro. Try again next time!")
