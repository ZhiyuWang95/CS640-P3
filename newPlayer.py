#!/usr/bin/python
import sys
import re
import pprint

inf = float("inf")
negInf = float("-inf")
lookDepth = 6

#read input
inp = sys.argv[1].replace("[", "").split("]")

lastPlay = inp.pop(len(inp)-1).replace("LastPlay:(", "").replace(")", "")
# for item in inp:
# 	print(item)
size = len(inp) - 2
remove = re.compile('(LastPlay:|\(|\))')
lastPlay = remove.sub("", lastPlay).split(",")
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

def findNeighbors(board, lastPlay, available):  #returns list of neighboring spots
	topPositive = lastPlay[1]
	rightPositive = lastPlay[2]
	neighbors = []
	if topPositive > 1:
		neighbors = [(topPositive+1, rightPositive-1), (topPositive+1, rightPositive), (topPositive, rightPositive+1), (topPositive-1, rightPositive+1), (topPositive-1, rightPositive), (topPositive, rightPositive-1)]
	else:
		neighbors = [(topPositive+1, rightPositive-1), (topPositive+1, rightPositive), (topPositive, rightPositive+1), (topPositive-1, rightPositive), (topPositive-1, rightPositive-1), (topPositive, rightPositive-1)]
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

def findAvailable(board):  #find available spots
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

def isLoser(board, move):  #figures out if the move will cause a loss
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

def calcScore(board, lastPlay, maxx):  #figure out score for move
	total = 0
	if isLoser(board, lastPlay):  #if move loses return neg infin
		if not maxx:
			return (-1000, lastPlay)
		else:
			return (1000, lastPlay)
	#if move wins return inf
	trapQueen = 0
	availableA = findNeighbors(board, lastPlay, True)
	boundin = set()
	odd = 0
	even = 0
	for (up, right) in availableA:
		if (up, right) not in boundin:
			bounded = findAvailable2(board, [0,up,right,size+2-up-right], set())
			boundin = boundin | bounded
			if len(bounded) % 2 == 0:
				even += 2
			else:
				odd += 2
	trapQueen += (odd - even)
	total += trapQueen

	if maxx:
		neighbors = findNeighbors(board, lastPlay, 'all')
		
		for ind, (up, right) in enumerate(neighbors):

			# Assign high score when more uncolored neighbors
			if board[up][right] == 0:
				total += 1

			#assign low score when different colored adjacent neighbors
			# if isColored(neighbors[n]) and isColored(neighbors[n + 1]):
			up2, right2 = neighbors[(ind + 1)%len(neighbors)]	
			
			if board[up][right] != board[up2][right2]:
				total-= 0.5
			
			#Assign medium score neighbors have same color as move
			if board[up][right] == board[lastPlay[1]][lastPlay[2]]:
				total += 0.5
		
		# Assign high score when few positions left around after your move
		if len(availableA) > 0:
			total += int(3/len(availableA))

	if not maxx:
		neighbors = findNeighbors(board, lastPlay, 'all')
		for ind, (up, right) in enumerate(neighbors):

			# Assign high score when more uncolored neighbors
			if board[up][right] == 0:
				total -= 1

			#assign low score when different colored adjacent neighbors
			# if isColored(neighbors[n]) and isColored(neighbors[n + 1]):
			up2, right2 = neighbors[(ind + 1)%len(neighbors)]	
			
			if board[up][right] != board[up2][right2]:
				total+= 0.5
			
			#Assign medium score neighbors have same color as move
			# print("LastPlay: ", lastPlay)
			if board[up][right] == board[lastPlay[1]][lastPlay[2]]:
				total -= 0.5
		
		# Assign high score when few positions left around after your move
		if len(availableA) > 0:
			total -= int(3/len(availableA))
	return (total, lastPlay)

def minimaxAB(board, lastPlay, depth, maxx, alpha, beta):  #minimax & a-b pruning
	if lastPlay[0] == "null":
		return (0, [3, size, 1, 1])
	if depth == 0 or isLoser(board, lastPlay):
		return calcScore(board, lastPlay, maxx)
	else:
		gremlins = findNeighbors(board, lastPlay, True)
		# print("neighbors: ", gremlins, " ", lastPlay)
		if not gremlins:
			gremlins = findAvailable(board)
		if maxx:
			score = (negInf, [])
			for (up, right) in gremlins:
				for color in range(1, 4):						
					board[up][right] = color
					move = [color, up, right, size+2-up-right]
					childScore = minimaxAB(board, move, depth-1, False, alpha, beta)
					board[up][right] = 0
					if childScore[0] >= score[0]:
						score = (childScore[0], move)
					if score[0] > alpha:
						alpha = score[0]
					if beta <= alpha:
						break
			return score
		else:
			score = (inf, [])

			for (up, right) in gremlins:
				for color in range(1, 4):						
					board[up][right] = color
					move = [color, up, right, size+2-up-right]
					childScore = minimaxAB(board, move, depth-1, True, alpha, beta)
					board[up][right] = 0
					if childScore[0] <= score[0]:
						score = (childScore[0], move)
					if score[0] < beta:
						beta = score[0]
					if beta <= alpha:
						break
			return score
#find best move
bestMove = minimaxAB(board, lastPlay, lookDepth, True, negInf, inf)
bestMove = list(bestMove)
bestMove[1] = list(bestMove[1])
if bestMove[0] == -1000 and isLoser(board, bestMove[1]):
	for color in [1, 2, 3]:
		bestMove[1][0] = color
		if not isLoser(board, bestMove[1]):
			bestMove[1][0] = color
			break


nextMove = map(str, bestMove[1])
makeMove = ",".join(nextMove) 
#print dat shiz
sys.stdout.write("(" + makeMove + ")");


