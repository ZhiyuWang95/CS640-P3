#Programming assignment 3 for CS640
#Aditya Chechani & Zhiyu Wang
#!/usr/bin/python
import sys
import re
import pprint

#default value setting.
inf = float("inf")#represents the positive infinity
negInf = float("-inf")#represents the negtive infinity
look_ahead_Depth = 5#looking-ahead-depth, you can modify that to 3,4,5,6,7, don't overpass 8, which will be very slow.

#Read the sys-input.
#This part achieves the format-changing.
inp = sys.argv[1].replace("[", "").split("]")#remove all the [ and split by ] to get the values from the board.
lastPlay = inp.pop(len(inp)-1).replace("LastPlay:(", "").replace(")", "")

size = len(inp) - 2# size is the variable which indicate the size of the board.
remove = re.compile('(LastPlay:|\(|\))')#define the format which is not interested in the string.
lastPlay = remove.sub("", lastPlay).split(",")# get the lastplay in a list.

if lastPlay[0] == "null":
	None
else:
	for ind, num in enumerate(lastPlay):
		lastPlay[ind] = int(num)
board = []
for row in reversed(inp):
	thisRow = []
	for num in list(row):
		thisRow.append(int(num))
	board.append(thisRow)

#find Neighbors function returns list of neighboring spots
def findNeighbors(board, lastPlay, available):  
	topPositive = lastPlay[1]
	rightPositive = lastPlay[2]
	neighbors = []
	if topPositive > 1:
		neighbors = [(topPositive+1, rightPositive-1), 
					 (topPositive+1, rightPositive), 
					 (topPositive, rightPositive+1), 
					 (topPositive-1, rightPositive+1), 
					 (topPositive-1, rightPositive), 
					 (topPositive, rightPositive-1)]
	else:
		neighbors = [(topPositive+1, rightPositive-1), 
					 (topPositive+1, rightPositive), 
					 (topPositive, rightPositive+1), 
					 (topPositive-1, rightPositive), 
					 (topPositive-1, rightPositive-1), 
					 (topPositive, rightPositive-1)]

	if available=="all":
		return neighbors  #returns all neighbors
	else:
		availableA = []
		unavailableA = []
		for (up, right) in neighbors:
			if board[up][right] == 0:
				availableA.append((up, right))  #spot is available
			else:
				unavailableA.append((up, right))
		if available:
			return availableA  #return available neighbors
		else:
			return unavailableA  #return unavailable neighbors

#find available spots
def findAvailable(board):  
	availableA = []
	for idx, r in enumerate(board):
		for idxx, s in enumerate(r):
			if s == 0:
				availableA.append((idx, idxx))
	return availableA

def findAvailable2(board, spot, seen):  #find the available spots within boarder of already colored spots
	availableA = findNeighbors(board, spot, True)
	unseen = set(availableA) - seen
	kitten = set([(spot[1], spot[2])])
	kittens = seen | unseen | kitten  
	for (up, right) in unseen:
		newKittens = findAvailable2(board, [0, up, right, size+2-up-right], kittens)
		kittens = kittens | newKittens
	return kittens

def Loserfunction(board, move):  #figures out if the move will cause a loss
	if move[0] == "null":
		return False
	color = move[0]
	neighbors = findNeighbors(board, move, "all")
	for ind, (up, right) in enumerate(neighbors): 
		colors = []
		colors.append(color) 
		if board[up][right] != 0:
			colors.append(board[up][right])
		(up2, right2) = neighbors[(ind+1)%len(neighbors)]
		if board[up2][right2] != 0:
			colors.append(board[up2][right2])
		if len(set(colors)) == 3:
			return True  #if all three colors return True
	return False



#score each move and return the score and move in the format:(score, [move]).
def evaluator(board, lastPlay, maxnode):
	scores = 0# initialize the scores as 0.
	if Loserfunction(board, lastPlay): #if the move will cause a lose, return infinity directly.
		if not maxnode:
			return (-1000, lastPlay)
		else:
			return (1000, lastPlay)
	#if the move will not cause a lose move, do the following.
	trapQueen = 0#initialize one subscore trapQueen as 0.
	availableA = findNeighbors(board, lastPlay, True)
	# find all the available node around lastplay in the board, and store in availableA.
	boundin = set()#initialize a empty list boundin.
	odd = 0#initialize a value odd to record the nodes on the path.
	even = 0#initialize another value even to record the nodes on the path.
	for (up, right) in availableA:#for the nodes in the availableA.
		if (up, right) not in boundin:
			bounded = findAvailable2(board, [0,up,right,size+2-up-right], set())
			#find all the nodes one the path to boundary and store into bounded list.
			boundin = boundin | bounded#add items in bounded into the boundin.
			if len(bounded) % 2 == 0:
				even += 2
				#if there are even nodes in the bounded, even will add 2.
			else:
				odd += 2
				#if there are odd nodes in the bounded, even will add 2.
	trapQueen += (odd - even)
	#trap could only happen in the step when we make move, so only even path could cause trap.
	#use odd to minus even, find out which condition in safe or possible trap is more.
	scores += trapQueen
	#add the sub-score trapQueen into the scores.

	if maxnode:
		neighbors = findNeighbors(board, lastPlay, 'all')
		
		for ind, (up, right) in enumerate(neighbors):

			# Assign high score when more uncolored neighbors
			if board[up][right] == 0:
				scores += 1

			#assign low score when different colored adjacent neighbors
			# if isColored(neighbors[n]) and isColored(neighbors[n + 1]):
			up2, right2 = neighbors[(ind + 1)%len(neighbors)]	
			
			if board[up][right] != board[up2][right2]:
				scores-= 0.5
			
			#Assign medium score neighbors have same color as move
			if board[up][right] == board[lastPlay[1]][lastPlay[2]]:
				scores += 0.5
		
		# Assign high score when few positions left around after your move
		if len(availableA) > 0:
			scores += int(3/len(availableA))

	if not maxnode:
		neighbors = findNeighbors(board, lastPlay, 'all')
		for ind, (up, right) in enumerate(neighbors):

			# Assign high score when more uncolored neighbors
			if board[up][right] == 0:
				scores -= 1

			#assign low score when different colored adjacent neighbors
			# if isColored(neighbors[n]) and isColored(neighbors[n + 1]):
			up2, right2 = neighbors[(ind + 1)%len(neighbors)]	
			
			if board[up][right] != board[up2][right2]:
				scores+= 0.5
			
			#Assign medium score neighbors have same color as move
			# print("LastPlay: ", lastPlay)
			if board[up][right] == board[lastPlay[1]][lastPlay[2]]:
				scores -= 0.5
		
		# Assign high score when few positions left around after your move
		if len(availableA) > 0:
			scores -= int(3/len(availableA))
	return (scores, lastPlay)

def minimaxpruning(board, lastPlay, depth, maxnode, alpha, beta):  #minimax & a-b pruning
	if lastPlay[0] == "null":
		return (0, [3, size, 1, 1])
	if depth == 0 or Loserfunction(board, lastPlay):#if the depth == 0, means the prediction ends or the move cause a lose.
		return evaluator(board, lastPlay, maxnode)#call the evaluator function to get the score for the move.
	else:
		workingneighbors = findNeighbors(board, lastPlay, True)
		#find all the workingneighbors around the last move.
		if not workingneighbors:
			workingneighbors = findAvailable(board)
			#if there is no working neighbors, go to find the empth nodes.
		if maxnode:#if this node is a max node
			score = (negInf, [])#initialize the core as negative infinity and no move.
			for (up, right) in workingneighbors:
				for color in range(1, 4):						
					board[up][right] = color
					move = [color, up, right, size+2-up-right]
					#generate all the possible moves.
					childScore = minimaxpruning(board, move, depth-1, False, alpha, beta)
					#run the minimaxpruning recursively.
					board[up][right] = 0
					if childScore[0] >= score[0]:
						score = (childScore[0], move)
					if score[0] > alpha:
						alpha = score[0]
					if beta <= alpha:
						break
					#update the beta and alpha according to the rules in max node
			return score
		else:#if this node is a min node.
			score = (inf, [])
			for (up, right) in workingneighbors:
				for color in range(1, 4):						
					board[up][right] = color
					move = [color, up, right, size+2-up-right]
					childScore = minimaxpruning(board, move, depth-1, True, alpha, beta)
					board[up][right] = 0
					if childScore[0] <= score[0]:
						score = (childScore[0], move)
					if score[0] < beta:
						beta = score[0]
					if beta <= alpha:
						break
			return score

#find best move
bestMove = minimaxpruning(board, lastPlay, look_ahead_Depth, True, negInf, inf)
bestMove = list(bestMove)
bestMove[1] = list(bestMove[1])

#this part is designed to deal with the corner evaluation and boundary evaluation rules.
if bestMove[0] == -1000 and Loserfunction(board, bestMove[1]):
#if the move will cause a lose or score is really low.
	for color in [1, 2, 3]: #here will represent the color at the place,to find out which one will not cause lose.
		bestMove[1][0] = color
		if not Loserfunction(board, bestMove[1]):
			bestMove[1][0] = color
			break


nextMove = map(str, bestMove[1])
makeMove = ",".join(nextMove) 
#print dat shiz
sys.stdout.write("(" + makeMove + ")");


