# Group Anagrams - Medium

My thought process was to `return [strs]` if lens of the list was 1 and it worked

But to organized the anagrams into seperate list was hard, I couldnt find a way. The closet thing was sorting the list based on `sorted()` but how would you get the orginal string into the organized list? Now i'm watching the video to find out

 I also still dont understand how complexity works like O(27) O(n) and etc.

# Video Notes

Take each string and sort them (what I was trying to do) - O(m * nlogn)
(n is average lengh of input string and m is length of list)

Optimal Solution - Hashmap

everything is a-z(26 unique characters)
count[a-z] = eat has 1e, 1a, 1t same for ate

Hashmap:
key: [eat, ate, tea] based on count[a-z]

Time complexity - O(m * n * 26) or O(m * n)
