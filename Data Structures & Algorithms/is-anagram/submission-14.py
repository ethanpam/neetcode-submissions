class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # return sorted(s) == sorted(t);
        if len(s) != len(t):
            return False

        s_set, t_set = {}, {}

        for i in range(len(s)):
            s_set[s[i]] = 1 + s_set.get(s[i], 0)
            t_set[t[i]] = 1 + t_set.get(t[i], 0)
        
        return s_set == t_set