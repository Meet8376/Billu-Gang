#!/usr/bin/env python3

import unittest


class Solution:
    def isPowerOfThree(self, n: int) -> bool:
        if n <= 0:
            return False
        while n % 3 == 0:
            n //= 3
        return n == 1


class TestSolution(unittest.TestCase):
    def test_is_power_of_three(self):
        sol = Solution()
        self.assertTrue(sol.isPowerOfThree(1))
        self.assertTrue(sol.isPowerOfThree(3))
        self.assertTrue(sol.isPowerOfThree(9))
        self.assertTrue(sol.isPowerOfThree(27))
        self.assertFalse(sol.isPowerOfThree(0))
        self.assertFalse(sol.isPowerOfThree(-1))
        self.assertFalse(sol.isPowerOfThree(45))


if __name__ == "__main__":
    unittest.main()
