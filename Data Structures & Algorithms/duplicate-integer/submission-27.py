class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        dup = {}
        for i in nums:
            if i in dup:
                return True
            else:
                dup[i] = dup.get(i, 0) + 1
        return False
