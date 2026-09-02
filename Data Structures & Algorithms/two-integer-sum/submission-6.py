class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        numDict = {}
        for num in range(len(nums)):
            difference = target - nums[num]
            if difference in numDict:
                return [numDict[difference], num]
            if nums[num] not in numDict:
                numDict[nums[num]] = num
