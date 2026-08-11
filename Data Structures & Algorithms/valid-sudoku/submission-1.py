class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        rows = collections.defaultdict(set)
        cols = collections.defaultdict(set)
        squares = collections.defaultdict(set)
        for i in range(9):
            for j in range(9):
                cell = board[i][j]
                if cell == ".":
                    continue
                
                #determines which box the cell belongs in 
                boxRow = i // 3
                bowCol = j // 3

                boxKey = (boxRow, bowCol)

                if cell in rows[i] or cell in cols[j] or cell in squares[boxKey]:
                    return False
                else:
                    rows[i].add(cell)
                    cols[j].add(cell)
                    squares[boxKey].add(cell)
        return True
