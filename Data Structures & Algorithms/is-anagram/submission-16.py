class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        sset, tset = {}, {}

        for i in range(len(s)):
            sset[s[i]] = 1 + sset.get(s[i], 0)
            tset[t[i]] = 1 + tset.get(t[i], 0)
        
        return sset == tset