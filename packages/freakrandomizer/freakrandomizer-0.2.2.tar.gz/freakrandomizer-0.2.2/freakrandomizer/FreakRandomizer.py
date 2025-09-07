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
        self.seen = []
        self.repeats = []
        self.sha_algorithm = sha_algorithm.lower()
        self._hash_funcs = {alg: getattr(hashlib, alg) for alg in hashlib.algorithms_available if hasattr(hashlib, alg)}
        self._time_ns = time.time_ns  # cache for performance
        self._last_result = None  # for fast repeat check

    def FreakRandomizeİnt(self, number1, number2, SHA=None):
        sha_to_use = (SHA or self.sha_algorithm).lower()
        hash_func = self._hash_funcs.get(sha_to_use)
        if hash_func is None:
            hash_func = getattr(hashlib, sha_to_use)

        # Use only counter as seed for speed, time_ns is called once per million
        seed = f"{self.counter}"
        hash_val = hash_func(seed.encode()).digest()
        # Use only first 8 bytes for int conversion (faster)
        num = int.from_bytes(hash_val[:8], 'big', signed=False)
        range_size = number2 - number1 + 1
        result = number1 + (num % range_size)
        self.seen.append(result)
        if self._last_result == result:
            self.repeats.append(result)
        self._last_result = result
        self.counter += 1
        return result

    def get_seen(self):
        return self.seen

    def get_repeats(self):
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
