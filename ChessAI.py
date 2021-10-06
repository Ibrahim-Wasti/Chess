import random
from typing import Counter

piece_scores = {'K':2000, 'Q': 900, 'R': 500, 'B': 330, 'N': 320, 'p': 100}

checkmate = 100000
stalemate = -1000
DEPTH = 3

wp_score = [
    [50, 50, 50, 50, 50, 50, 50, 50], 
    [40, 40, 40, 40, 40, 40, 40, 40],
    [10,10, 20,  30,  30, 20, 10,10],
    [5,  5, 10,  25,  25, 10,  5, 5],
    [0,  0,  0,  20,  20,  0,  0, 0],
    [5, -5,-10,   0,   0,-10, -5,10],
    [5, 10, 10, -20, -20, 15, 15,10],
    [0,  0,  0,   0,   0,  0,  0, 0]
]

bp_score = [
    [0,  0,  0,   0,   0,  0,  0, 0], 
    [5, 10, 10, -20, -20, 15, 15,10],
    [5, -5,-10,   0,   0,-10, -5,10],
    [0,  0,  0,  20,  20,  0,  0, 0],
    [5,  5, 10,  25,  25, 10,  5, 5],
    [10,10, 20,  30,  30, 20, 10,10],
    [40, 40, 40, 40, 40, 40, 40, 40],
    [50, 50, 50, 50, 50, 50, 50, 50]
]

wN_score = [
                [-50, -40, -30, -30, -30, -30, -40, -50],
                [-40, -20,   0,   0,   0,   0, -20, -40],
                [-30,   0,  10,  15,  15,  10,   0, -30],
                [-30,   5,  15,  20,  20,  15,   5, -30],
                [-30,   0,  15,  20,  20,  15,   0, -30],
                [-30,   5,  10,  15,  15,  10,   5, -30],
                [-40, -20,   0,   5,   5,   0, -20, -40],
                [-50, -40, -30, -30, -30, -30, -40, -50]
]

bN_score = [
                [-50, -40, -30, -30, -30, -30, -40, -50],
                [-40, -20,   0,   5,   5,   0, -20, -40],
                [-30,   5,  10,  15,  15,  10,   5, -30],
                [-30,   0,  15,  20,  20,  15,   0, -30],
                [-30,   5,  15,  20,  20,  15,   5, -30],
                [-30,   0,  10,  15,  15,  10,   0, -30],
                [-40, -20,   0,   0,   0,   0, -20, -40],
                [-50, -40, -30, -30, -30, -30, -40, -50]
]

wB_score = [
                [-20, -10, -10, -10, -10, -10, -10, -20], 
                [-10,   0,   0,   0,   0,   0,   0, -10],
                [-10,   0,   5,  10,  10,   5,   0, -10],
                [-10,   5,   5,  10,  10,   5,   5, -10],
                [-10,   0,  10,  10,  10,  10,   0, -10],
                [-10,  10,  10,  10,  10,  10,  10, -10],
                [-10,   5,   0,   0,   0,   0,   5, -10],
                [-20, -10, -10, -10, -10, -10, -10, -20]
]

bB_score = [
                [-20, -10, -10, -10, -10, -10, -10, -20], 
                [-10,   5,   0,   0,   0,   0,   5, -10],
                [-10,  10,  10,  10,  10,  10,  10, -10],
                [-10,   0,  10,  10,  10,  10,   0, -10],
                [-10,   5,   5,  10,  10,   5,   5, -10],
                [-10,   0,   5,  10,  10,   5,   0, -10],
                [-10,   0,   0,   0,   0,   0,   0, -10],
                [-20, -10, -10, -10, -10, -10, -10, -20]
]

wR_score = [
    [0,  0,  0,  0,  0,  0,  0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [0,  0,  0,  5,  5,  0,  0, 0]
]

bR_score = [
    [0,  0,  0,  5,  5,  0,  0, 0],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [-5, 0,  0,  0,  0,  0,  0,-5],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [0,  0,  0,  0,  0,  0,  0, 0]
]

wQ_score = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10,  0,    0,  0,  0,   0,   0, -10],
    [-10,  0,    5,  5,  5,   5,   0, -10],
    [ -5,  0,    5,  5,  5,   5,   0,  -5],
    [  0,  0,    5,  5,  5,   5,   0,  -5],
    [-10,  5,    5,  5,  5,   5,   0, -10],
    [-10,  0,    5,  0,  0,   0,   0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

bQ_score = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10,  0,    5,  0,  0,   0,   0, -10],
    [-10,  5,    5,  5,  5,   5,   0, -10],
    [ 0,   0,    5,  5,  5,   5,   0,  -5],
    [-5,   0,    5,  5,  5,   5,   0,  -5],
    [-10,  0,    5,  5,  5,   5,   0, -10],
    [-10,  0,    0,  0,  0,   0,   0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

piece_pos_scores = {'wp': wp_score, 'bp': bp_score, 'wN': wN_score, 'bN': bN_score, 'wB': wB_score, 'bB': bB_score, 'wR': wR_score, 'bR': bR_score,
                    'wQ': wQ_score, 'bQ':bQ_score}

def random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]

def meh(gs, valid_moves): #finding the best based on material only 
    turn_multiplier = 1 if gs.white_to_move else -1
    opp_minmax_score = checkmate
    good_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opp_moves = gs.valid_moves()
        if gs.stale_mate:
            opp_max_score = stalemate
        elif gs.check_mate:
            opp_max_score = checkmate
        else:
            opp_max_score = -checkmate
            for move in opp_moves:
                gs.make_move(move)
                gs.valid_moves()
                if gs.check_mate:
                    score = checkmate
                elif gs.stale_mate:
                    score = stalemate
                else:
                    score = -turn_multiplier * material_score(gs.board)
                if score > opp_max_score:
                    opp_max_score = score
                gs.undo_move()
        if  opp_max_score < opp_minmax_score:
            opp_minmax_score = opp_max_score
            good_move = player_move
        gs.undo_move()
    return good_move

def find_best_move(gs, valid_moves):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)
    counter = 0
    alpha_beta_negamax(gs, valid_moves, DEPTH, -checkmate, checkmate, 1 if gs.white_to_move else -1)
    #print(counter)
    return next_move

def minmax(gs, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:
        return material_score(gs.board)
    random.shuffle(valid_moves)
    if white_to_move:
        max_score = -checkmate
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.valid_moves()
            score = minmax(gs, next_moves, depth-1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = checkmate
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.valid_moves()
            score = minmax(gs, next_moves, depth -1 , True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score

def nega_max(gs, valid_moves, depth, multiplier):
    global next_move
    if depth == 0:
        return multiplier * board_score(gs)
    
    max_score = -checkmate
    for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.valid_moves()
            score = -nega_max(gs, next_moves, depth-1, -multiplier)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
    return max_score

def alpha_beta_negamax(gs, valid_moves, depth, alpha, beta, multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return multiplier * board_score(gs)
    

    max_score = -checkmate
    for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.valid_moves()
            score = -alpha_beta_negamax(gs, next_moves, depth-1, -beta, -alpha, -multiplier)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
                    print(move, score)
            gs.undo_move()
            if max_score > alpha: #pruning trees
                alpha = max_score
            if alpha >= beta:
                break
    return max_score

"""
Positive score means white is winning, negative means black is winning
"""
def board_score(gs):
    if gs.check_mate:
        if gs.white_to_move:
            return -checkmate
        else:
            return checkmate
    elif gs.stale_mate:
        return stalemate

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            sq = gs.board[row][col]
            if sq != '--':
                piece_pos_score = 0
                if sq[1] != 'K':
                        piece_pos_score = piece_pos_scores[sq][row][col]

                if sq[0] == 'w':
                    score += piece_scores[sq[1]] + piece_pos_score 
                elif sq[0] == 'b':
                    score -= piece_scores[sq[1]] + piece_pos_score 
    return score

def material_score(board):
    score = 0
    for row in board:
        for s in row:
            if s[0] == 'w':
                score += piece_scores[s[1]]
            elif s[0] == 'b':
                score -= piece_scores[s[1]]
    return score