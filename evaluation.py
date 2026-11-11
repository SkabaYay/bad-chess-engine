# evaluation.py

from constants import *

class Evaluator:
    def __init__(self):
        self.piece_values = {
            PAWN: 100,
            KNIGHT: 320,
            BISHOP: 330,
            ROOK: 500,
            QUEEN: 900,
            KING: 20000
        }

        # Piece-square tables for midgame
        self.setup_piece_square_tables()

    def setup_piece_square_tables(self):
        # Set up piece-square tables
        # Values are from White's perspective (higher = better for white)
        # Tables are stored from rank 0 = rank 1, rank 7 = rank 8

        # Pawn table - encourage center control and advancement
        self.pawn_table = [
            [  0,   0,   0,   0,   0,   0,   0,   0],  # Rank 8
            [ 50,  50,  50,  50,  50,  50,  50,  50],  # Rank 7
            [ 10,  10,  20,  30,  30,  20,  10,  10],  # Rank 6
            [  5,   5,  10,  25,  25,  10,   5,   5],  # Rank 5
            [  0,   0,   0,  20,  20,   0,   0,   0],  # Rank 4
            [  5,  -5, -10,   0,   0, -10,  -5,   5],  # Rank 3
            [  5,  10,  10, -20, -20,  10,  10,   5],  # Rank 2
            [  0,   0,   0,   0,   0,   0,   0,   0]   # Rank 1
        ]
        
        # Knight table - encourage center control
        self.knight_table = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20,   0,   0,   0,   0, -20, -40],
            [-30,   0,  10,  15,  15,  10,   0, -30],
            [-30,   5,  15,  20,  20,  15,   5, -30],
            [-30,   0,  15,  20,  20,  15,   0, -30],
            [-30,   5,  10,  15,  15,  10,   5, -30],
            [-40, -20,   0,   5,   5,   0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]
        
        # Bishop table - encourage long diagonals
        self.bishop_table = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10,   0,   0,   0,   0,   0,   0, -10],
            [-10,   0,   5,  10,  10,   5,   0, -10],
            [-10,   5,   5,  10,  10,   5,   5, -10],
            [-10,   0,  10,  10,  10,  10,   0, -10],
            [-10,  10,  10,  10,  10,  10,  10, -10],
            [-10,   5,   0,   0,   0,   0,   5, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]
        
        # Rook table - encourage open files and 7th rank
        self.rook_table = [
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [  5,  10,  10,  10,  10,  10,  10,   5],
            [ -5,   0,   0,   0,   0,   0,   0,  -5],
            [ -5,   0,   0,   0,   0,   0,   0,  -5],
            [ -5,   0,   0,   0,   0,   0,   0,  -5],
            [ -5,   0,   0,   0,   0,   0,   0,  -5],
            [ -5,   0,   0,   0,   0,   0,   0,  -5],
            [  0,   0,   0,   5,   5,   0,   0,   0]
        ]
        
        # Queen table - slight center preference, stay back early
        self.queen_table = [
            [-20, -10, -10,  -5,  -5, -10, -10, -20],
            [-10,   0,   0,   0,   0,   0,   0, -10],
            [-10,   0,   5,   5,   5,   5,   0, -10],
            [ -5,   0,   5,   5,   5,   5,   0,  -5],
            [  0,   0,   5,   5,   5,   5,   0,  -5],
            [-10,   5,   5,   5,   5,   5,   0, -10],
            [-10,   0,   5,   0,   0,   0,   0, -10],
            [-20, -10, -10,  -5,  -5, -10, -10, -20]
        ]
        
        # King middlegame table - encourage castling and safety
        self.king_middlegame_table = [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [ 20,  20,   0,   0,   0,   0,  20,  20],
            [ 20,  30,  10,   0,   0,  10,  30,  20]
        ]
        
        # King endgame table - encourage centralization
        self.king_endgame_table = [
            [-50, -40, -30, -20, -20, -30, -40, -50],
            [-30, -20, -10,   0,   0, -10, -20, -30],
            [-30, -10,  20,  30,  30,  20, -10, -30],
            [-30, -10,  30,  40,  40,  30, -10, -30],
            [-30, -10,  30,  40,  40,  30, -10, -30],
            [-30, -10,  20,  30,  30,  20, -10, -30],
            [-30, -30,   0,   0,   0,   0, -30, -30],
            [-50, -30, -30, -30, -30, -30, -30, -50]
        ]

    def get_piece_square_value(self, piece_type, row, col, is_white, is_endgame):
        # Get the piece-square table value for a piece.
        # Black's tables are flipped vertically from White's

        # Flip row for black pieces
        table_row = 7 - row if is_white else row

        if piece_type == PAWN:
            return self.pawn_table[table_row][col]
        elif piece_type == KNIGHT:
            return self.knight_table[table_row][col]
        elif piece_type == BISHOP:
            return self.bishop_table[table_row][col]
        elif piece_type == ROOK:
            return self.rook_table[table_row][col]
        elif piece_type == QUEEN:
            return self.queen_table[table_row][col]
        elif piece_type == KING:
            if is_endgame:
                return self.king_endgame_table[table_row][col]
            else:
                return self.king_middlegame_table[table_row][col]
        
        return 0

    def is_endgame(self, board):
        # Determine if we're in the endgame
        # Simple heuristic: both sides have no queens, or
        # every side which has a queen has additionally no other pieces or one minor piece maximum
        white_queens = 0
        black_queens = 0
        white_minor = 0 # knights and bishops
        black_minor = 0
        white_major = 0 # rooks
        black_major = 0

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece == EMPTY:
                    continue

                piece_type = piece & 7
                colour = piece & 24

                if piece_type == QUEEN:
                    if colour == WHITE:
                        white_queens += 1
                    else:
                        black_queens += 1
                elif piece_type in [KNIGHT, BISHOP]:
                    if colour == WHITE:
                        white_minor += 1
                    else:
                        black_minor += 1
                elif piece_type == ROOK:
                    if colour == WHITE:
                        white_major += 1
                    else:
                        black_major += 1

        # No queens = endgame
        if white_queens == 0 and black_queens == 0:
            return True

        white_limited = (white_queens == 1 and white_minor + white_major <= 1)
        black_limited = (black_queens == 1 and black_minor + black_major <= 1)

        # Queen but limited material = endgame
        if white_limited or black_limited:
            return True

        return False

    def evaluate_pawn_structure(self, board):
        # Evaluate pawn structure features.
        # Returns a score from White's perspective
        score = 0

        # Analyze each file for pawn structure
        white_pawns = [[] for _ in range(8)]  # List of rows for each file
        black_pawns = [[] for _ in range(8)]

        # Collect pawn positions
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece == (WHITE | PAWN):
                    white_pawns[col].append(row)
                elif piece == (BLACK | PAWN):
                    black_pawns[col].append(row)

        # Evaluate white pawns
        for col in range(8):
            if len(white_pawns[col]) > 1:
                # Doubled pawns penalty
                score -= 10 * (len(white_pawns[col]) - 1)

            if len(white_pawns[col]) > 0:
                # Check for isolate pawns (no friendly pawns on adjacent files)
                is_isolated = True
                if col > 0 and len(white_pawns[col - 1]) > 0:
                    is_isolated = False
                if col < 7 and len(white_pawns[col + 1]) > 0:
                    is_isolated = False

                if is_isolated:
                    score -= 15

                # Check for passed pawns (no enemy pawns ahead on same adjacent files)
                for pawn_row in white_pawns[col]:
                    is_passed = True

                    # Check same file
                    for black_row in black_pawns[col]:
                        if black_row > pawn_row:
                            is_passed = False
                            break

                    # Check adjacent files
                    if is_passed:
                        for adjacent_col in [col - 1, col + 1]:
                            if 0 <=adjacent_col < 8:
                                for black_row in black_pawns[adjacent_col]:
                                    if black_row > pawn_row:
                                        is_passed = False
                                        break

                    if is_passed:
                        # Passed pawn bonus increases with advancement
                        bonus = 10 + (pawn_row * 10)
                        score += bonus

        # Evaluate black pawns (same logic, opposite scoring)
        for col in range(8):
            if len(black_pawns[col]) > 1:
                score += 10 * (len(black_pawns[col]) - 1)
            
            if len(black_pawns[col]) > 0:
                is_isolated = True
                if col > 0 and len(black_pawns[col - 1]) > 0:
                    is_isolated = False
                if col < 7 and len(black_pawns[col + 1]) > 0:
                    is_isolated = False
                
                if is_isolated:
                    score += 15
                
                for pawn_row in black_pawns[col]:
                    is_passed = True
                    
                    for white_row in white_pawns[col]:
                        if white_row < pawn_row:
                            is_passed = False
                            break
                    
                    if is_passed:
                        for adjacent_col in [col - 1, col + 1]:
                            if 0 <= adjacent_col < 8:
                                for white_row in white_pawns[adjacent_col]:
                                    if white_row < pawn_row:
                                        is_passed = False
                                        break
                    
                    if is_passed:
                        bonus = 10 + ((7 - pawn_row) * 10)
                        score -= bonus
        
        return score

    def evaluate_king_safety(self, board, is_endgame):
        # Evalue king safety
        # Only important in middlegame

        if is_endgame:
            return 0

        score = 0

        # Find kings
        white_king_pos = None
        black_king_pos = None

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece == (WHITE | KING):
                    white_king_pos = (row, col)
                elif piece == (BLACK | KING):
                    black_king_pos = (row, col)


        if white_king_pos:
            score += self.evaluate_single_king_safety(board, white_king_pos, WHITE)

        if black_king_pos:
            score -= self.evaluate_single_king_safety(board, black_king_pos, BLACK)

        return score

    def evaluate_single_king_safety(self, board, king_pos, colour):
        # Evalue safety for a single king
        # Returns positive value for safe king
        safety = 0
        row, col = king_pos

        # Bonus for castled position
        if colour == WHITE:
            if row == 0 and (col == 6 or col == 2):
                safety += 30
        else:
            if row == 7 and (col == 6 or col == 2):
                safety += 30

        # Evaluate pawn shield
        if colour == WHITE:
            shield_row = row + 1
            if shield_row < 8:
                for dcol in [-1, 0, 1]:
                    shield_col = col + dcol
                    if 0 <=shield_col<8:
                        piece = board.board[shield_row][shield_col]
                        if piece == (WHITE | PAWN):
                            safety += 10
        else:
            shield_row = row - 1
            if shield_row >= 0:
                for dcol in [-1, 0, 1]:
                    shield_col = col + dcol
                    if 0 <= shield_col < 8:
                        piece = board.board[shield_row][shield_col]
                        if piece == (BLACK | PAWN):
                            safety += 10

        # Penalty for open files near king
        for dcol in [-1, 0, 1]:
            check_col = col + dcol
            if 0 <= check_col < 8:
                has_pawn = False
                for check_row in range(8):
                    piece = board.board[check_row][check_col]
                    if piece & 7 == PAWN:
                        has_pawn = True
                        break

                if not has_pawn:
                    safety -= 15

        return safety

    def evaluate_mobility(self, board):
        # Evaluate piece mobility
        # More legal moves = better position

        # Count legal moves for current side
        our_mobility = len(board.generate_legal_moves())

        # Switch sides and count opponent mobility
        board.to_move = BLACK if board.to_move == WHITE else WHITE
        their_mobility = len(board.generate_legal_moves())
        board.to_move = BLACK if board.to_move == WHITE else WHITE

        # Mobility difference
        mobility_score = (our_mobility - their_mobility) * 2

        # Return from White's perspective
        if board.to_move == WHITE:
            return mobility_score
        else:
            return -mobility_score

    def evaluate_bishop_pair(self, board):
        # Bonus for having the bishop pair
        white_bishops = 0
        black_bishops = 0

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece == (WHITE | BISHOP):
                    white_bishops += 1
                elif piece == (BLACK | BISHOP):
                    black_bishops += 1

        score = 0
        if white_bishops >= 2:
            score += 30
        if black_bishops >= 2:
            score -= 30

        return score

    def evaluate_old(self, board):
        # Complete position evaluation
        # Returns score from White's perspective

        # 0. Is checkmate
        moves = board.generate_legal_moves()
        if len(moves) == 0 and board.is_in_check(board.to_move):
            if board.to_move == WHITE:
                return -20000
            else:
                return 20000

        score = 0
        is_endgame = self.is_endgame(board)

        # 1. Material and piece-square tables
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]

                if piece == EMPTY:
                    continue

                piece_type = piece & 7
                colour = piece & 24
                is_white = (colour == WHITE)

                # Base material value
                value = self.piece_values[piece_type]

                # Piece-square table bonus
                pst_value = self.get_piece_square_value(
                    piece_type, row, col, is_white, is_endgame
                )

                if is_white:
                    score += value + pst_value
                else:
                    score -= value + pst_value

        # 2. Pawn structure
        score += self.evaluate_pawn_structure(board)

        # 3. King safety (middlegame only)
        score += self.evaluate_king_safety(board ,is_endgame)

        # 4. Bishop pair
        score += self.evaluate_bishop_pair(board)

        # 5. Mobility (expensive, so we scale it down)
        # Comment if too slow future me
        #score += self.evaluate_mobility(board) // 2

        return score

    def evaluate_relative(self, board):
        # Evaluate from the perspective of the side to move.
        score = self.evaluate(board)
        return score if board.to_move == WHITE else -score

    def get_game_phase(self, board):
        # Calculate game phase (0 = endgame, 24 = opening).
        # Based on material: each piece contributes to the phase
        phase = 0

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece == EMPTY:
                    continue

                piece_type = piece & 7

                if piece_type == KNIGHT or piece_type == BISHOP:
                    phase += 1
                elif piece_type == ROOK:
                    phase += 2
                elif piece_type == QUEEN:
                    phase += 4

        return min(phase, 24) # Cap at 24 (opening value)

    def evaluate(self, board):
        # Use tapered evaluation for smooth phase transitions
        phase = self.get_game_phase(board)

        # Calculate middlegame and endgame scores seperately
        mg_score = 0 # Middlegame score
        eg_score = 0 # Endgame score

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]

                if piece == EMPTY:
                    continue

                piece_type = piece & 7
                colour = piece & 24
                is_white = (colour == WHITE)

                # Material value
                value = self.piece_values[piece_type]

                # Piece-square values for both phases
                mg_pst = self.get_piece_square_value(piece_type, row, col, is_white, False)
                eg_pst = self.get_piece_square_value(piece_type, row, col, is_white, True)

                if is_white:
                    mg_score += value + mg_pst
                    eg_score += value + eg_pst
                else:
                    mg_score -= value + mg_pst
                    eg_score -= value + eg_pst

        # Add other evaluation terms
        pawn_score = self.evaluate_pawn_structure(board)
        mg_score += pawn_score
        eg_score += pawn_score

        # King safety only in middlegame
        mg_score += self.evaluate_king_safety(board, False)

        bishop_pair = self.evaluate_bishop_pair(board)
        mg_score += bishop_pair
        eg_score += bishop_pair

        # Taper between phases
        # phase 24 = pure middlegame, phase 0 = pure endgame
        score = int((mg_score * phase + eg_score * (24 - phase)) // 24)

        return score