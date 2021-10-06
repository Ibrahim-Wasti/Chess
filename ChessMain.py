"""
Resposible for handling user input and displaying th evurrent Gamestate object.
"""
import pygame as p
import numpy as np
import ChessEngine, ChessAI

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 275
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT//DIMENSION
IMAGES = {}

def load_images():
    pieces = ['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bK','bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'),(SQ_SIZE,SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH,BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    move_log_font = p.font.SysFont('Arial', 14, False, False)
    gs = ChessEngine.GameState()
    valid_moves = gs.valid_moves()
    move_made = False # flag var for when move is made
    animate = False
    load_images()
    running = True
    sq_selected = () # will keep track of the last click as a tuple(row,col)
    player_clicks = [] # will keep track of player clicks and will have 2 tuples (row,col)
    game_over = False
    player_one = False #if person is playing white this will be true, if AI is white then False
    player_two = False #True if person is playing black, False if AI is playing black
    
    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two) #checks to see if it is a person's turn not AI
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handling
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos() # (x,y) coords
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row,col) or col >= 8: # the user wants to undo or user clicked the move log
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row,col)
                        player_clicks.append(sq_selected)
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0],player_clicks[1],gs.board)
                        #print(move.get_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = () #resetting user click
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            #key handling
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:# z will be the undo button
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                if e.key == p.K_r: #board resetting using the r key
                    gs = ChessEngine.GameState()
                    valid_moves = gs.valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
        
        if not game_over and not human_turn: #AI move
            ai_move = ChessAI.find_best_move(gs, valid_moves)
            if ai_move is None:
                ai_move = ChessAI.random_move(valid_moves)
            gs.make_move(ai_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animnating(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.valid_moves()
            move_made = False
            animate = False

        draw_gamestate(screen,gs,valid_moves, sq_selected, move_log_font)

        if gs.check_mate or gs.stale_mate:
            game_over = True
            text = 'Stalemate' if gs.stale_mate else 'Black wins by Checkmate' if gs.white_to_move else 'White wins by Checkmate'
            draw_endgame_text(screen, text)


        clock.tick(60)
        p.display.flip()

def draw_gamestate(screen, gs, valid_moves, sq_selected, move_log_font):
    draw_board(screen)
    highlght(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)
    draw_movelog(screen, gs, move_log_font)

def draw_board(screen): # drawing the board 
    global colors
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
            # piece = board[r][c]
            # if piece != '--': # not an empty square
            #     screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def highlght(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): #square selected is a piece that can be moved
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #transparency value -- 0 = transparent and 255 = opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('green'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (SQ_SIZE*move.end_col, SQ_SIZE*move.end_row))

def draw_pieces(screen,board): # drawing the pieces on top of the board, can be used for syntax highlighting if necessary
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--': # not an empty square
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def draw_movelog(screen, gs, font):    
    movelog_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), movelog_rect)
    move_log = gs.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        turn = str(i//2 + 1) + '. ' + str(move_log[i]) + ' '
        if i + 1 < len(move_log):
            turn += str(move_log[i+ 1]) + ' '
        move_texts.append(turn)
    
    moves_per_row = 3
    padding = 5
    y = padding
    linespacing = 2
    for i in range(0, len(move_texts), moves_per_row):
        text = ''
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j] + '  '
        text_obj = font.render(text, True, p.Color('white'))
        text_loc = movelog_rect.move(padding, y)
        screen.blit(text_obj,text_loc)
        y += text_obj.get_height() + linespacing

def animnating(move, screen, board, clock):
    global colors
    delta_r = move.end_row - move.start_row
    delta_c = move.end_col - move.start_col
    frames_per_sq = 10
    frame_count = abs(delta_c) + abs(delta_r) + frames_per_sq
    for frame in range(frame_count + 1):
        r, c = (move.start_row + delta_r * frame/frame_count, move.start_col + delta_c * frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen,color, end_square)
        if move.piece_captured != '--':
            if move.en_passant:
                ep_row = (move.end_row + 1) if move.piece_captured[0] == 'b' else (move.end_row - 1)
                end_square = p.Rect(move.end_col*SQ_SIZE, ep_row*SQ_SIZE, SQ_SIZE, SQ_SIZE) 
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_endgame_text(screen, text):
    font = p.font.SysFont('Helvetica', 32, True, False)
    text_obj = font.render(text, 0, p.Color('Gray'))
    text_loc = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - text_obj.get_width()/2, BOARD_HEIGHT/2 - text_obj.get_height()/2)
    screen.blit(text_obj,text_loc)
    text_obj = font.render(text, 0, p.Color('Black'))
    screen.blit(text_obj, text_loc.move(2, 2))

if __name__ == '__main__':
    main()
