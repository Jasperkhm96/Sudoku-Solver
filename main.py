import sys
import time
import numpy as np
from random import randint

class Board():
    def __init__(self, array):
        """
        Remember that everything will be indexed from 0 to 8!!!
        self.tiles is a 9 x 9 numpy array representing sodoku board
        """
        self.tiles = array
        
    def __str__(self):
        return str(self.tiles)
        
    def SetValue(self, value, rowNum, colNum):
        """
        To be used instead of 
        """
        if (self.tiles[rowNum, colNum] != 0):
            print("Error! Trying to edit an element that was not 0. Quitting.")
            sys.exit(4)
        elif rowNum not in range(9):
            print("Error! Trying to edit an element with rowNum not in range.")
            sys.exit(3)
        elif colNum not in range(9):
            print("Error! Trying to edit an element with colNum not in range.")
            sys.exit(3)
        else:
            self.tiles[rowNum, colNum] = value
    
    def InRow(self, value, rowNum):
        """Check if given value is in row"""
        for v in self.tiles[rowNum]:
            if (v == value):
                return True
        return False
    
    def InCol(self, value, colNum):
        """Check if given value is in column"""
        for v in self.tiles[:,colNum]:
            if (v == value):
                return True
        return False
    
    def MinBoxValues(self, rowNum, colNum):
        """
        Return the indicies of the top left corner of the given square
        Used as a helper to check if value is InBox
        """
        return ((colNum - (colNum % 3)), (rowNum - (rowNum % 3)))
        
    def InBox(self, value, rowNum, colNum):
        """Check if given value is in respective Box"""
        
        # minCol, rowNum are the minimum cells in the given locations "box"
        minCol, minRow = self.MinBoxValues(rowNum, colNum)
        
        for r in self.tiles[minRow:minRow+3,minCol:minCol+3]:
            for i in r:
                if (i == value):
                    return True
        return False
    
    def IsPossibleValue(self, value, rowNum, colNum):
        """Check all three ways, return True if value is NOT in row, column, or box"""
        return (not (self.InRow(value, rowNum) or self.InCol(value, colNum) or  self.InBox(value, rowNum, colNum)))

    def SeemsSolved(self):
        """Just a quick check to see if solved"""
        for row in self.tiles:
            if (sum(row) != 45):
                return False
        return True
    
    def VerifySolved(self):
        """Robust check for sudoku board properties. To be used if SeemsSolved passes"""
        
        # Check value appears exactly once in each row
        for row in self.tiles:
            vals = list(range(1,10))
            for i in row:
                try:
                    vals.remove(i)
                except:
                    return False
                
        # Check value appears exactly once in each column
        for col in self.tiles.T:
            vals = list(range(1,10))
            for i in col:
                try:
                    vals.remove(i)
                except:
                    return False
        
        # Check value appears exactly once in each box
        for a in range(0, 9, 3):
            for b in range(0, 9, 3):
                box = self.tiles[a:a+3,b:b+3]
                vals = list(range(1,10))
                for i in box.flatten():
                    try:
                        vals.remove(i)
                    except:
                        return False
        # If we get here, everything is okay!
        return True
    
    def Complete8Rows(self):
        """
        Complete rows of 8 with last missing number
        return True if at least 1 value added
        """
        aRowFilled = False
        rowNum = 0
        for row in self.tiles:
            if list(row).count(0) == 1:
                colNum = 0
                for i in row:
                    if i == 0:
                        self.SetValue(45 - sum(row), rowNum, colNum)
                        aRowFilled = True
                        break
                    colNum += 1
            rowNum += 1
        return aRowFilled
    
    def Complete8Cols(self):
        """
        Complete cols of 8 with last missing number
        return True if at least 1 value added
        """
        aColFilled = False
        colNum = 0
        for col in self.tiles.T:
            if list(col).count(0) == 1:
                rowNum = 0
                for i in col:
                    if i == 0:
                        self.SetValue(45 - sum(col), rowNum, colNum)
                        aColFilled = True
                        break
                    rowNum += 1
            colNum += 1
        return aColFilled
    
    def Complete8Boxes(self):
        """
        Add the final value to boxes with 8 values
        Go through boxes left to right, top to bottom
        return True if at least 1 value added
        """
        aBoxFilled = False
        
        for a in range(0, 9, 3):
            for b in range(0, 9, 3):
                box = self.tiles[a:a+3,b:b+3]
                if list(box.flatten()).count(0) == 1:
                    rowNum = a
                    for r in box:
                        colNum = b - 1 # For trick of breaking double loop
                        for i in r:
                            colNum += 1
                            if i == 0:
                                self.SetValue(45 - sum(sum(box)), rowNum, colNum)
                                aBoxFilled = True
                                break
                        # Breaking out of two loops on set
                        else:
                            rowNum += 1
                            continue
                        break
        return aBoxFilled
    
    def RowContradiction(self):
        """Check to see if a value exists in any row twice (puzzle is invalid)"""
        for row in self.tiles:
            tempList = []
            for i in row:
                if i == 0:
                    continue
                elif i in tempList:
                    return True
                else: # i not found already
                    tempList.append(i)
        return False
    
    def ColContradiction(self):
        """Check to see if a value exists in any col twice (puzzle is invalid)"""
        for col in self.tiles.T:
            tempList = []
            for i in col:
                if i == 0:
                    continue
                elif i in tempList:
                    return True
                else: # i not found already
                    tempList.append(i)
        return False
    
    def BoxContradiction(self):
        """Check to see if a value exists in any box twice (puzzle is invalid)"""
        for a in range(0, 9, 3):
            for b in range(0, 9, 3):
                box = self.tiles[a:a+3,b:b+3]
                tempList = []
                for i in box.flatten():
                    if i == 0:
                        continue
                    elif i in tempList: # Found twice in one box!
                        return True
                    else: # i not found already
                        tempList.append(i)
        return False
    
    def ContradictionExists(self):
        return (self.RowContradiction() or self.ColContradiction() or self.BoxContradiction())
        
    
def Solve(board):
    """
    Brute force solve by going through row by row, left to right
    After each full run through, check if board has changed. If not, break out
    Returns dictionary with number of solutions, information, and potentially a solved board
    """
    returnDict = {
            "Sols": 0,
            "Branches": 1, # All terminating "nodes" will be 1 "branch". If a fork is made, this is sum of all sub branches instead
            "Contradictions": 0,
            "Board": None
            }
    boardChanged = True
    while boardChanged:
        boardChanged = False
        potentialGuesses = [9, {}]
        
        # Cherry-pick the gimmes
        # No paticular reason for this order
        if (board.Complete8Rows() or board.Complete8Cols() or board.Complete8Boxes()):
            boardChanged = True
            
        if board.ContradictionExists():
            returnDict["Contradictions"] = 1
            return returnDict
        
        if board.SeemsSolved():
            if board.VerifySolved():
                returnDict["Sols"] = 1
                returnDict["Board"] = board
                return returnDict

        rowNum = 0
        for row in board.tiles:
            colNum = 0
            for value in row:
                if value == 0:
                    # Bruteforce try each one
                    possibleValues = []
                    for val in range(1,10):
                        if board.IsPossibleValue(val, rowNum, colNum):
                            possibleValues.append(val)
                    if (len(possibleValues) == 1):
                        # A single, solution has been found!
                        board.SetValue(possibleValues[0], rowNum, colNum)
                        boardChanged = True
                    elif (len(possibleValues) == 0):
                        # No solutions possible for this box. Erroneous board!
                        returnDict["Contradictions"] = 1
                        return returnDict
                    else: #len(possibleValues) > 1
                        # To be used for making guess. Compile list of possible values of shortest length
                        if len(possibleValues) == potentialGuesses[0]:
                            potentialGuesses[1][(rowNum, colNum)] = possibleValues
                        elif len(possibleValues) < potentialGuesses[0]:
                            potentialGuesses[0] = len(possibleValues)
                            potentialGuesses[1] = {}
                            potentialGuesses[1][(rowNum, colNum)] = possibleValues
                colNum += 1
            rowNum += 1
        
        # Cherry-pick the gimmes
        # No paticular reason for this order
        if (board.Complete8Rows() or board.Complete8Cols() or board.Complete8Boxes()):
            boardChanged = True
        
        if board.ContradictionExists():
            returnDict["Contradictions"] = 1
            return returnDict
            
        if board.SeemsSolved():
            if board.VerifySolved():
                returnDict["Sols"] = 1
                returnDict["Board"] = board
                return returnDict
    
    # After brute forcing each value, if board hasn't changed, branch and recurse
    # FIXME - Optimize this (len potential guesses, closest to center/furthest from center of other points)
    guessIndex = list(potentialGuesses[1].keys())[randint(0, len(potentialGuesses[1]) - 1)]
    returnDict["Branches"] = 0 # Since this is a node where terminating nodes feed up to
    for p in potentialGuesses[1][guessIndex]:
        
        # Recurse
        sb = Board(board.tiles.copy())
        sb.SetValue(p, guessIndex[0], guessIndex[1])
        branchResults = Solve(sb)
        
        returnDict["Branches"] += branchResults["Branches"]
        returnDict["Sols"] += branchResults["Sols"]
        returnDict["Contradictions"] += branchResults["Contradictions"]
        if returnDict["Board"] == None:
            # Set to "top" board
            returnDict["Board"] = branchResults["Board"]
    return returnDict

def main(args = sys.argv):
    startTime = time.time()
    if len(args) == 1:
        fileName = input("Enter the filename of the csv file containing the sodoku puzzle values: ")
    elif len(args) == 2:
        fileName = args[1]
    else:
        print("The sudoku solver will solve a sodoku board, input through a .csv file. Please enter a filename as the first and only argument.")
        return 1

    if fileName[-4:] != ".csv":
        print("You must enter a .csv file! You entered: %s" % fileName)
        return 1

    try:
        f = open(fileName, "r")
    except:
        print("Please enter a valid filename as the first argument")
        return 1

    lineNum = 1
    rows = [] # Make list of lists to create numpy array
    for l in f:
        l = l.strip().split(',')
        if len(l) != 9:
            print("Each row must contain exactly 9 entries. Row %d contained %d" % (lineNum, len(l)))
            return 2

        try:
            vals = []
            for i in l:
                if i == '':
                    vals.append(0)
                elif (int(i) < 0) or (int(i) > 9):
                    print("All elements must be an integer between 1 and 9, or a 0 or blank to represent unknown values. An error occured in row %d: %s" %  (lineNum, i))
                    return 2
                else:
                    vals.append(int(i))
        except:
            print("Each element must be an integer. Enter 0 for unfilled boxes. Error in row %d" % lineNum)
            return 2

        rows.append(vals)
        lineNum += 1

    if lineNum != 10:
        print("Your file must have exactly 9 rows. Yours had %d" % lineNum-1)
        return 2
    
    f.close()
    

    board = np.array(rows)
    boardObject = Board(board)
    solution = Solve(boardObject)
    
    print()
    if solution["Sols"] == 1:
        print("Found an exact solution:")
        print(solution["Board"])
    elif solution["Sols"] > 1:
        print("Not a well formulated problem- many solutions possible. One possible solution:")
        print(solution["Board"])
    elif solution["Sols"] == 0:
        print("No solutions possible")
    else:
        print("Something went wrong")
    
    # Some statistics
    #print("\nSolver statistics:")
    #print("Branches: %d" % solution["Branches"])
    #print("Runtime: %.02f seconds" % (time.time() - startTime))

if __name__ == "__main__":
    main(sys.argv)