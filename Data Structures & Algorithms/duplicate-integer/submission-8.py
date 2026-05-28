class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        for i in range(len(nums)):
            for j in range(1,len(nums)):
                if nums[i] in nums[i+1:len(nums)]:
                    return True
                else:
                    continue
        return False
                
