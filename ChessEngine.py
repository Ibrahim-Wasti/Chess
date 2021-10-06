#Resposible for storing all the info for the current state of the game object, also determining the valid moves

from os import truncate
from pygame.constants import WINDOWHITTEST, WINDOWTAKEFOCUS

class GameState():
    def __init__(self):
        #board is an 8x8 and each element is represented by a 2 char string
        #w or b stand for color, and second letter is the type of piece
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp','bp','bp','bp','bp','bp','bp','bp'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR']]
        self.move_functions = {'p': self.pawn_moves, 'R': self.rook_moves, 'N': self.knight_moves, 
                               'B': self.bishop_moves, 'Q': self.queen_moves, 'K': self.king_moves }

        self.white_to_move = True
        self.move_log = []
        self.white_king_loc = (7,4)
        self.black_king_loc = (0,4)
        self.check_mate = False
        self.stale_mate = False
        self.incheck = False
        self.pins = []
        self.checks = []
        self.enpassant_poss = ()
        self.enpassant_log = [self.enpassant_poss]
        self.white_castle_ks = True
        self.white_castle_qs = True
        self.black_castle_ks = True
        self.black_castle_qs = True
        self.castle_right_log = [Castle_Rights(self.white_castle_ks, self.black_castle_ks, self.white_castle_qs,  self.black_castle_qs)]


    def make_move(self, move): #does not work for any special moves (castling, pawn promo, etc.)
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board[move.start_row][move.start_col] = '--'
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == 'wK':#updating the kings' positions
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_loc = (move.end_row, move.end_col)
        if move.pawn_promo:#checking if the move is a pawn promo
            desired_piece = 'Q'
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + desired_piece
        #looking for possible en passant
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_poss = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.enpassant_poss = ()
        if move.en_passant:
            self.board[move.start_row][move.end_col] = '--'
        #castling
        if move.castle:
            if move.end_col - move.start_col == 2: #kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            else: #queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col -2]
                self.board[move.end_row][move.end_col - 2] = '--'
        #updating castleing rights
        self.update_castle_rights(move)
        self.castle_right_log.append(Castle_Rights(self.white_castle_ks, self.black_castle_ks, self.white_castle_qs,  self.black_castle_qs))

        self.enpassant_log.append(self.enpassant_poss)  

    def undo_move(self): #undo last move
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            if move.piece_moved == 'wK':
                self.white_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_loc = (move.start_row, move.start_col)
            #undoing an en passant
            if move.en_passant:
                self.board[move.end_row][move.end_col] = '--'#leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured
            
            self.enpassant_log.pop()     
            self.enpassant_poss = self.enpassant_log[-1]
           
            #undo castle move
            self.castle_right_log.pop()
            new_rights = self.castle_right_log[-1]
            self.white_castle_ks = new_rights.wks
            self.black_castle_ks = new_rights.bks
            self.white_castle_qs = new_rights.wqs
            self.black_castle_qs = new_rights.bqs

            if move.castle:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'
        
        self.check_mate = False
        self.stale_mate = False

    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.white_castle_ks = False
            self.white_castle_qs = False
        elif move.piece_moved == 'bK':
            self.black_castle_ks = False
            self.black_castle_qs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7: 
                if move.start_col == 0: #queen side rook for white
                    self.white_castle_qs = False
                elif move.start_col == 7: #king side rook for white
                    self.white_castle_ks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0: 
                if move.start_col == 0: #queen side rook for black
                    self.black_castle_qs = False
                elif move.start_col == 7: #king side rook for black
                    self.black_castle_ks = False

        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.white_castle_qs = False
                elif move.end_col == 7:
                    self.white_castle_ks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.black_castle_qs = False
                elif move.end_col == 7:
                    self.black_castle_ks = False
        
    def valid_moves(self):# moves allowed while in check
        moves = []
        self.incheck, self.pins, self.checks = self.checks_and_pins()
        if self.white_to_move:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]
        if self.incheck:
            if len(self.checks) == 1: #only 1 check on baord; must block, capture or move king
                moves = self.possible_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] #enemy piece that is checking
                valid_squares = [] #allowable squares to move to
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_sq = (king_row + check[2] * i, king_col + check[3] * i) #check[2] and [3] are check directions
                        valid_squares.append(valid_sq)
                        if valid_sq[0] == check_row and valid_sq[1] == check_col: #once you get to piece end checks
                            break
                for i in range(len(moves)-1, -1,- 1):
                    if moves[i].piece_moved[1] != 'K': #move does not move king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares: #move does not block or capture
                            moves.remove(moves[i])
            else: #2+ pieces checking the king. the king must move
                self.king_moves(king_row, king_col, moves)
        else:
            moves = self.possible_moves()
        if len(moves) == 0:
            if self.incheck:
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False 
        return moves
    
    def in_check(self): #determine if the current player is in check
        if self.white_to_move:
            return self.sq_attacked(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.sq_attacked(self.black_king_loc[0], self.black_king_loc[1])
    
    def sq_attacked(self,r,c, ally_color): #determine if the nemy can attack the square (r,c)
        enemy_color = 'w' if ally_color == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color:
                        break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        if (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type =='B') or \
                                (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                                return True
                        else:
                            break
                else:
                    break
        knight_moves = ((-1,-2), (-2,-1), (-2,1), (-1,2), (1,2), (2,1), (2,-1), (1,-2))
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N': #checking to see if enemy Knight
                    return True    
        return False

    def checks_and_pins(self):
        pins = [] #squares where ally pieces are protecting king from check
        checks = [] #squares that are activley checking the king
        incheck = False
        if self.white_to_move:
            enemy = 'b'
            ally = 'w'
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else:
            enemy = 'w'
            ally = 'b'
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () # reset possible pins
            for i in range(1,8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally and end_piece[1] != 'K':
                        if possible_pin == ():# 1st allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:# 2nd allied piece to be pinned, so no longer pinned and no check
                            break
                    elif end_piece[0] == enemy:
                        type = end_piece[1]
                        if (0 <= j <= 3 and type == 'R') or (4 <= j <= 7 and type =='B') or \
                                (i == 1 and type == 'p' and ((enemy == 'w' and 6 <= j <= 7) or (enemy == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == ():#no piece protecting the king, so check
                                incheck = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else: #ally piece blocking, so pinned
                                pins.append(possible_pin)
                                #print(pins)
                                break
                        else: #no check being applied
                            break
                else:
                    break #off board
        knight_moves = ((-1,-2), (-2,-1), (-2,1), (-1,2), (1,2), (2,1), (2,-1), (1,-2))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy and end_piece[1] == 'N': #checking to see if enemy Knight
                    incheck = True
                    checks.append((end_row, end_col, m[0], m[1]))
    
        return incheck, pins, checks

    def possible_moves(self):#all possible moves
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r,c,moves)
        return moves

    def pawn_moves(self, r,  c, moves): #all possible pawn moves
        piece_pinned = False
        pin_dir = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_dir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.white_to_move:
            move_amount = -1
            start_row = 6
            back_row = 0
            enemy = 'b'
            king_row, king_col = self.white_king_loc
        else:
            move_amount = 1
            start_row = 1
            back_row = 7
            enemy = 'w'
            king_row, king_col = self.black_king_loc
        pawn_promo = False

        if self.board[r+ move_amount][c] == '--':
            if not piece_pinned or pin_dir ==(move_amount,0):
                if r + move_amount == back_row:
                    pawn_promo= True
                moves.append(Move((r,c), (r + move_amount, c), self.board, pawn_promo = pawn_promo))
                if r == start_row and self.board[r + 2*move_amount][c] == '--':
                    moves.append(Move((r, c), (r + 2*move_amount, c), self.board))
        if c-1 >= 0: #pawn capture to the left
            if not piece_pinned or pin_dir ==(move_amount, -1):
                if self.board[r + move_amount][c-1][0] == enemy:
                    if r + move_amount == back_row:
                        pawn_promo = True
                    moves.append(Move((r, c), (r + move_amount, c-1), self.board, pawn_promo = pawn_promo))
                if (r + move_amount, c - 1) == self.enpassant_poss:
                    att_piece = block_piece = False
                    if king_row == r:
                        if king_col < c: #king is left of the pawn
                            inside_range = range(king_col+1, c-1) #between the pawn and the king
                            outside_range = range(c+1,8) #between the pawn and the edge
                        else: #king is right of the pawn
                            inside_range = range(king_col-1, c, -1)
                            outside_range = range(c-2, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != '--': #there is another piece in addition to the enpassant pawn which is now a blocking piece
                                block_piece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemy and (square[1] == 'R' or square[1] == 'Q'):
                                att_piece = True
                            elif square != '--':
                                block_piece = True
                    if not att_piece or block_piece:
                        moves.append(Move((r, c), (r + move_amount, c-1),self.board, en_passant = True))

        if c+1 <= 7: #pawn capture right
            if not piece_pinned or pin_dir == (move_amount, 1):
                if self.board[r + move_amount][c + 1][0] == enemy:
                    if r + move_amount == back_row:
                        pawn_promo= True
                    moves.append(Move((r, c), (r + move_amount, c+1), self.board, pawn_promo = pawn_promo))
                if (r + move_amount, c + 1) == self.enpassant_poss:
                    att_piece = block_piece = False
                    if king_row == r:
                        if king_col < c: #king is left of the pawn
                            inside_range = range(king_col+1, c) #between the pawn and the king
                            outside_range = range(c+2, 8) #between the pawn and the edge
                        else: #king is right of the pawn
                            inside_range = range(king_col-1, c+1, -1)
                            outside_range = range(c-1, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != '--': #there is another piece in addition to the enpassant pawn which is now a blocking piece
                                block_piece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemy and (square[1] == 'R' or square[1] == 'Q'):
                                att_piece = True
                            elif square != '--':
                                block_piece = True
                    if not att_piece or block_piece:
                        moves.append(Move((r, c), (r + move_amount, c+1),self.board, en_passant = True))

    def rook_moves(self, r,  c, moves):#all possible rook moves
        piece_pinned = False
        pin_dir = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_dir = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #cant remove queen from pin on rook, only on bishop
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_dir == d or pin_dir == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--': #enemy piece
                            moves.append(Move((r,c), (end_row,end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r,c), (end_row,end_col), self.board))
                            break
                        else: # same color piece
                            break
                else:#off the board
                    break

    def knight_moves(self, r,  c, moves):#all possible knight moves
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        directions = ((-1,-2), (-2,-1), (-2,1), (-1,2), (1,2), (2,1), (2,-1), (1,-2))
        ally_color = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + directions[i][0]
            end_col = c + directions[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((r,c), (end_row,end_col), self.board))

    def bishop_moves(self, r,  c, moves):#all possible bishop moves
        piece_pinned = False
        pin_dir = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_dir = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #up_left, up_right, down_left, down_right
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_dir == d or pin_dir == (-d[0],-d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--': #enemy piece
                            moves.append(Move((r,c), (end_row,end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r,c), (end_row,end_col), self.board))
                            break
                        else: # same color piece
                            break
                else:
                    break

    def queen_moves(self, r,  c, moves):#all possible queen moves
         self.rook_moves(r, c, moves)
         self.bishop_moves(r, c, moves)

    def king_moves(self, r,  c, moves):#all possible king moves
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + row_moves[i] 
            end_col = c + col_moves[i] 
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: #not an ally piece (can be empty)
                    if ally_color == 'w': #place king on end square and check for checks
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    incheck, pins, checks = self.checks_and_pins()
                    if not incheck:
                        moves.append(Move((r,c), (end_row,end_col), self.board))
                    if ally_color == 'w': #place king back on original square
                        self.white_king_loc = (r, c)
                    else:
                        self.black_king_loc = (r, c)
        self.get_castle_moves(r, c, moves, ally_color)
        
    def get_castle_moves(self, r, c, moves, ally_color):
        incheck = self.sq_attacked(r, c, ally_color)
        if incheck:
            return None
        if (self.white_to_move and self.white_castle_ks) or (not self.white_to_move and self.black_castle_ks):
            self.get_ks_castle_moves(r, c, moves, ally_color)
        if (self.white_to_move and self.white_castle_qs) or (not self.white_to_move and self.black_castle_qs):
            self.get_qs_castle_moves(r, c, moves, ally_color) 
    
    def get_ks_castle_moves(self, r, c, moves, ally_color):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--' and \
            not self.sq_attacked(r, c+1, ally_color) and not self.sq_attacked(r, c+2, ally_color):
                moves.append(Move((r, c), (r, c+2), self.board, castle = True))         

    def get_qs_castle_moves(self, r, c, moves, ally_color):
        if self.board[r][c - 1] == '--' and self.board[r][c -2] == '--' and self.board[r][c -3] == '--' and \
            not self.sq_attacked(r, c-1, ally_color) and not self.sq_attacked(r, c-2, ally_color):
                moves.append(Move((r, c), (r, c-2), self.board, castle = True))

class Castle_Rights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    #map keys to values as key : value
    rank_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in rank_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, en_passant = False, pawn_promo = False, castle = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.pawn_promo = pawn_promo
        if (self.piece_moved == 'wp' and self.end_row  == 0) or (self.piece_moved == 'bp' and self.end_row == 7):
            self.pawn_promo = True
        self.en_passant = en_passant
        self.castle = castle
        if en_passant:
            self.piece_captured = 'bp' if self.piece_moved == 'wp' else 'wp'
        self.is_capture = self.piece_captured != '--'
        self.move_id = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col
    
    # Overridung the equals method
    def __eq__(self,other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
    
    def __str__(self):
        if self.castle:
            return 'O-O' if self.end_col == 6 else 'O-O-O'
        
        end_square = self.get_rank_file(self.end_row, self.end_col)
        if self.piece_moved[1] == 'p':
            if self.is_capture:
                return self.cols_to_files[self.start_col] + 'x' + end_square
            else:
                return end_square
        turn = self.piece_moved[1]
        if self.is_capture:
            turn += 'x'
        return turn + end_square