# FreakRandomizer v1.0 - Improved randomness without using Python's random module
# Github: https://github.com/Kutay1062/FreakRandomizer
# Author: Kutay
# Date: 2024-06-20
# License: MIT License
import time
import hashlib

class FreakRandomizer:
    """
    FreakRandomizer Class

    Methods:
    
    - FreakRandomizeInt(number1, number2, SHA=None):
        Returns a random integer between number1 and number2.
        Optionally, specify the SHA algorithm to use (e.g., 'sha1', 'sha256', 'sha512').
        If SHA is None, uses the default SHA algorithm set at initialization.
        
    - get_seen():
        Returns a list of all numbers generated so far.
        
    - get_repeats():
        Returns a list of numbers that were repeated consecutively.
        
    Example usage:
        fr = FreakRandomizer()
        fr.FreakRandomizeInt(1, 100)
        fr.FreakRandomizeInt(1, 100, SHA="sha1")
    """

    def __init__(self, sha_algorithm="sha256"):
        self.counter = 0
        self.seen = []       # Stores all generated numbers
        self.repeats = []    # Stores repeated numbers
        self.sha_algorithm = sha_algorithm.lower()  # SHA seçimi

    def FreakRandomizeİnt(self, number1, number2, SHA=None):
        # SHA parametresi verilmişse override et
        if SHA:
            sha_to_use = SHA.lower()
        else:
            sha_to_use = self.sha_algorithm

        seed = f"{time.time_ns()}_{self.counter}"
        hash_func = getattr(hashlib, sha_to_use)
        hash_val = hash_func(seed.encode()).hexdigest()
        num = int(hash_val, 16)
        result = number1 + (num % (number2 - number1 + 1))
        self.seen.append(result)
        if len(self.seen) > 1 and self.seen[-1] == self.seen[-2]:
            self.repeats.append(result)
        self.counter += 1
        return result

    def get_seen(self):
        """Returns a list of all numbers generated so far."""
        return self.seen

    def get_repeats(self):
        """Returns a list of numbers that were repeated consecutively."""
        return self.repeats
    
    def help(any=None):
        help_text = """
        FreakRandomizer Class:
        - FreakRandomizeInt(number1, number2, SHA=None): Returns a random integer between number1 and number2.
          Optionally, you can specify the SHA algorithm to use (e.g., 'sha1', 'sha256', 'sha512').
          If SHA is None, uses the default SHA algorithm set at initialization.
        - get_seen(): Returns a list of all numbers generated so far.
        - get_repeats(): Returns a list of numbers that were repeated consecutively.
        """
        print(help_text)
        print(hashlib.algorithms_available)

# ---------- Default instance ----------
_default_freak_randomizer = FreakRandomizer()

def FreakRandomizeİnt(number1, number2, SHA=None):
    return _default_freak_randomizer.FreakRandomizeİnt(number1, number2, SHA=SHA)
