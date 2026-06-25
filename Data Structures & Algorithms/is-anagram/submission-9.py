class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        # return sorted(s) == sorted(t);
        s_set = {};
        t_set = {};

        for i in s:
            if i in s_set:
                s_set[i] += 1
            else:
                s_set[i] = 1

        for j in t:
            if j in t_set:
                t_set[j] += 1
            else:
                t_set[j] = 1
        
        if s_set == t_set:
            return True
        
        return False