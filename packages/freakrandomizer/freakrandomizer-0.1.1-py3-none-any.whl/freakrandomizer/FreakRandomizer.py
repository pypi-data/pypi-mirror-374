# FreakRandomizer v1.0 - Improved randomness without using Python's random module
#Github:
#https://github.com/Kutay1062/FreakRandomizer
#Author: Kutay
#Date: 2024-06-20
#License: MIT License
import time
import hashlib

class FreakRandomizer:
    def __init__(self):
        self.counter = 0
        self.seen = []       # Stores all generated numbers
        self.repeats = []    # Stores repeated numbers

    def FreakRandomizeİnt(self, number1, number2):
        # Use current time and a counter to generate a pseudo-random number
        seed = f"{time.time_ns()}_{self.counter}"
        hash_val = hashlib.sha256(seed.encode()).hexdigest()
        num = int(hash_val, 16)
        result = number1 + (num % (number2 - number1 + 1))
        self.seen.append(result)
        if len(self.seen) > 1 and self.seen[-1] == self.seen[-2]:
            self.repeats.append(result)
        self.counter += 1
        return result

    def get_seen(self):
        return self.seen

    def get_repeats(self):
        return self.repeats


_default_freak_randomizer = FreakRandomizer()

def FreakRandomizeİnt(number1, number2):
    return _default_freak_randomizer.FreakRandomizeİnt(number1, number2)


