from constants import *
from move import Move

class Board:
    def __init__(self):
        # 8x8 board
        self.board = [[EMPTY for _ in range(8)] for _ in range(8)]

        # Game state
        self.to_move = WHITE
        self.castling_rights = {
            "K" : True, # White kingside
            "Q": True, # White queenside
            "k": True, # Black kingside
            "q": True # Black queenside
        }
        self.en_passant_square = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

        self.setup_initial_position()

    def setup_initial_position(self):
        # Black pieces (rank 8 and 7)
        back_rank = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        for i in range(8):
            self.board[7][i] = BLACK | back_rank[i]
            self.board[6][i] = BLACK | PAWN

        # White pieces (rank 2 and 1)
        for i in range(8):
            self.board[1][i] = WHITE | PAWN
            self.board[0][i] = WHITE | back_rank[i]

    def piece_at(self, row, col):
        # Get the piece at a given square
        return self.board[row][col]

    def is_square_attacked(self, row, col, by_colour):
        # Check if a square is attacked by a given color
        # Check for pawn attacks
        if by_colour == WHITE:
            pawn_direction = 1
        else:
            pawn_direction = -1

        for dcol in [-1, 1]:
            pawn_row = row - pawn_direction
            pawn_col = col + dcol
            if 0<= pawn_row < 8 and 0 <= pawn_col < 8:
                piece = self.board[pawn_row][pawn_col]
                if piece == (by_colour | PAWN):
                    return True

        # Check for knight attacks
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for drow, dcol in knight_offsets:
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = self.board[new_row][new_col]
                if piece == (by_colour | KNIGHT):
                    return True

        # Check for sliding piece attacks
        # Diagonal (bishop and queen)
        for drow, dcol in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            new_row, new_col = row + drow, col + dcol
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = self.board[new_row][new_col]
                if piece != EMPTY:
                    if (piece & 24) == by_colour:
                        piece_type = piece & 7
                        if piece_type in [BISHOP, QUEEN]:
                            return True
                    break
                new_row += drow
                new_col += dcol

        # Straight (rook and queen)
        for drow, dcol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + drow, col + dcol
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = self.board[new_row][new_col]
                if piece != EMPTY:
                    if (piece & 24) == by_colour:
                        piece_type = piece & 7
                        if piece_type in [ROOK, QUEEN]:
                            return True
                    break
                new_row += drow
                new_col += dcol

        # Check for king attacks
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue
                new_row, new_col = row + drow, col + dcol
                if 0 <= new_row < 8 and 0 <=new_col < 8:
                    piece = self.board[new_row][new_col]
                    if piece == (by_colour | KING):
                        return True

        return False

    def find_king(self, colour):
        # Find the king's position for a given colour
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece == (colour | KING):
                    return (row, col)
        return None
    
    def is_in_check(self, colour):
        # Check if the given colour's king is in check
        king_pos = self.find_king(colour)
        if king_pos is None:
            return False

        opponent_colour = BLACK if colour == WHITE else WHITE
        return self.is_square_attacked(king_pos[0], king_pos[1], opponent_colour)
        
    def is_legal_move(self, move):
        # Check if a move is legal (doesn't leave king in check)
        undo_info = self.make_move(move)

        # The king of the side that just moved
        moving_colour = BLACK if self.to_move == WHITE else WHITE

        # Special check for castling - squares must not be under attack
        if move.is_castling:
            king_row = move.from_row
            opponent_colour = BLACK if moving_colour == WHITE else WHITE

            # Check that king doesn't move through check
            if move.to_col == 6: # Kingside
                for col in [4, 5, 6]:
                    if self.is_square_attacked(king_row, col, opponent_colour):
                        self.unmake_move(move, undo_info)
                        return False
            else: # Queenside
                for col in [2, 3, 4]:
                    if self.is_square_attacked(king_row, col, opponent_colour):
                        self.unmake_move(move, undo_info)
                        return False

        legal = not self.is_in_check(moving_colour)
        self.unmake_move(move, undo_info)
        return legal

    def generate_legal_moves(self):
        # Generate all legal moves for the current position
        pseudo_legal = self.generate_pseudo_legal_moves()
        return [move for move in pseudo_legal if self.is_legal_move(move)]

    def generate_pawn_moves(self, row, col, moves):
        # Generate all pawn moves from a given square
        piece = self.board[row][col]
        colour = piece & 24

        if colour == WHITE:
            direction = 1
            start_row = 1
            promotion_row = 7
        else:
            direction = -1
            start_row = 6
            promotion_row = 0

        # Single push
        if self.board[row + direction][col] == EMPTY:
            if row + direction == promotion_row:
                # Promotions
                for promo_piece in [QUEEN, ROOK, BISHOP, KNIGHT]:
                    moves.append(Move(row, col, row + direction, col, promotion=promo_piece))
            else:
                moves.append(Move(row, col, row + direction, col))

            # Double push
            if row == start_row and self.board[row + 2 * direction][col] == EMPTY:
                moves.append(Move(row, col, row + 2 * direction, col))

        for dcol in [-1, 1]:
            new_col = col + dcol
            if 0 <= new_col < 8:
                new_row = row + direction
                target = self.board[new_row][new_col]

                # Regular capture
                if target != EMPTY and (target & 24) != colour:
                    if new_row == promotion_row:
                        for promo_piece in [QUEEN, ROOK, BISHOP, KNIGHT]:
                            moves.append(Move(row, col, new_row, new_col, promotion=promo_piece))
                    else:
                        moves.append(Move(row, col, new_row, new_col))

                # En passant
                if self.en_passant_square == (new_row, new_col):
                    moves.append(Move(row, col, new_row, new_col, is_en_passant=True))

    def generate_knight_moves(self, row, col, moves):
        # Generate all knight moves from a given square
        piece = self.board[row][col]
        colour = piece & 24

        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for drow, dcol in knight_offsets:
            new_row, new_col = row + drow, col + dcol

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target == EMPTY or (target & 24) != colour:
                    moves.append(Move(row, col, new_row, new_col))

    def generate_sliding_moves(self, row, col, moves, directions):
        # Generate moves for sliding pieces (bishop, rook, queen)
        piece = self.board[row][col]
        colour = piece & 24

        for drow, dcol in directions:
            new_row, new_col = row + drow, col + dcol

            while 0 <=new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]

                if target == EMPTY:
                    moves.append(Move(row, col, new_row, new_col))
                elif (target & 24) != colour:
                    moves.append(Move(row, col, new_row, new_col))
                    break # Can't move past a capture
                else:
                    break # Blocked by own piece

                new_row += drow
                new_col += dcol

    def generate_bishop_moves(self, row, col, moves):
        # Generate all bishop moves
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.generate_sliding_moves(row, col, moves, directions)

    def generate_rook_moves(self, row, col, moves):
        # Generate all rook moves
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.generate_sliding_moves(row, col, moves, directions)

    def generate_queen_moves(self, row, col, moves):
        # Generate all queen moves
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1), 
            (1, -1), (1, 0), (1, 1)
        ]
        self.generate_sliding_moves(row, col, moves, directions)

    def generate_king_moves(self, row, col, moves):
        # Generate all king moves including castling
        piece = self.board[row][col]
        colour = piece & 24

        # Regular king moves
        for drow in [-1, 0, 1]:
            for dcol in [-1, 0, 1]:
                if drow == 0 and dcol == 0:
                    continue

                new_row, new_col = row + drow, col + dcol

                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.board[new_row][new_col]
                    if target == EMPTY or (target & 24) != colour:
                        moves.append(Move(row, col, new_row, new_col))

        # Castling
        if colour == WHITE and row == 0:
            # Kingside
            if (self.castling_rights["K"] and
                self.board[0][5] == EMPTY and
                self.board[0][6] == EMPTY):
                moves.append(Move(0, 4, 0, 6, is_castling=True))

            # Queenside
            if (self.castling_rights["Q"] and
                self.board[0][1] == EMPTY and
                self.board[0][2] == EMPTY and
                self.board[0][3] == EMPTY):
                moves.append(Move(0, 4, 0, 2, is_castling=True))

        elif colour == BLACK and row == 7:
            # Kingside
            if (self.castling_rights["k"] and
                self.board[7][5] == EMPTY and
                self.board[7][6] == EMPTY):
                moves.append(Move(7, 4, 7, 6, is_castling=True))

            # Queenside
            if (self.castling_rights["q"] and
                self.board[7][1] == EMPTY and
                self.board[7][2] == EMPTY and
                self.board[7][3] == EMPTY):
                moves.append(Move(7, 4, 7, 2, is_castling=True))

    def generate_pseudo_legal_moves(self):
        # Generate all pseudo-legal moves for the current position
        moves= []

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]

                if piece == EMPTY or (piece & 24) != self.to_move:
                    continue

                piece_type = piece & 7 # Identify the piece type

                if piece_type == PAWN:
                    self.generate_pawn_moves(row, col, moves)
                elif piece_type == KNIGHT:
                    self.generate_knight_moves(row, col, moves)
                elif piece_type == BISHOP:
                    self.generate_bishop_moves(row, col, moves)
                elif piece_type == ROOK:
                    self.generate_rook_moves(row, col, moves)
                elif piece_type == QUEEN:
                    self.generate_queen_moves(row, col, moves)
                elif piece_type == KING:
                    self.generate_king_moves(row, col, moves)

        return moves

    def make_move(self, move):
        # Make a move on the board and return information needed to unmake it
        # Store state for unmaking
        undo_info = {
            "captured_piece": self.board[move.to_row][move.to_col],
            "castling_rights": self.castling_rights.copy(),
            "en_passant_square": self.en_passant_square,
            "halfmove_clock": self.halfmove_clock
        }
        piece = self.board[move.from_row][move.from_col]
        piece_type = piece & 7

        # Move the piece
        self.board[move.to_row][move.to_col] = piece
        self.board[move.from_row][move.from_col] = EMPTY

        # Handle promotion
        if move.promotion:
            self.board[move.to_row][move.to_col] = (piece & 24) | move.promotion

        # Handle en passant capture
        if move.is_en_passant:
            capture_row = move.from_row
            self.board[capture_row][move.to_col] = EMPTY

        # Handle castling
        if move.is_castling:
            # Move the rook
            if move.to_col == 6:
                self.board[move.to_row][5] = self.board[move.to_row][7]
                self.board[move.to_row][7] = EMPTY
            else: # Queenside
                self.board[move.to_row][3] = self.board[move.to_row][0]
                self.board[move.to_row][0] = EMPTY

        # Update en passant square
        self.en_passant_square = None
        if piece_type == PAWN and abs(move.to_row - move.from_row) == 2:
            self.en_passant_square = ((move.from_row + move.to_row) // 2, move.from_col)

        # Update castling rights
        if piece_type == KING:
            if self.to_move == WHITE:
                self.castling_rights["K"] = False
                self.castling_rights["Q"] = False
            else:
                self.castling_rights["k"] = False
                self.castling_rights["q"] = False

        if piece_type == ROOK:
            if self.to_move == WHITE:
                if move.from_row == 0 and move.from_col == 0:
                    self.castling_rights["Q"] = False
                elif move.from_row == 0 and move.from_col == 7:
                    self.castling_rights["K"] = False
            else:
                if move.from_row == 7 and move.from_col == 0:
                    self.castling_rights["q"] = False
                elif move.from_row == 7 and move.from_col == 7:
                    self.castling_rights["k"] = False

        # A rook captured on its home square removes that castling right
        corner_rights = {
            (0, 0): "Q", (0, 7): "K",
            (7, 0): "q", (7, 7): "k",
        }
        right = corner_rights.get((move.to_row, move.to_col))
        if right:
            self.castling_rights[right] = False

        # Update halfmove clock
        if piece_type == PAWN or undo_info["captured_piece"] != EMPTY:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Update move counters
        if self.to_move == BLACK:
            self.fullmove_number += 1

        self.to_move = BLACK if self.to_move == WHITE else WHITE

        return undo_info

    def unmake_move(self, move, undo_info):
        # Unmake a move and restore the previous position.
        # Switch back to the side that made the move
        self.to_move = BLACK if self.to_move == WHITE else WHITE

        # Restore move counters
        if self.to_move == BLACK:
            self.fullmove_number -= 1

        piece = self.board[move.to_row][move.to_col]

        # Handle promotion (restore pawn)
        if move.promotion:
            piece = (piece & 24) | PAWN

        # Move the piece back
        self.board[move.from_row][move.from_col] = piece
        self.board[move.to_row][move.to_col] = undo_info["captured_piece"]

        # Handle en passant
        if move.is_en_passant:
            capture_row = move.from_row
            opponent_colour = BLACK if self.to_move == WHITE else WHITE
            self.board[capture_row][move.to_col] = opponent_colour | PAWN

        # Handle castling
        if move.is_castling: # Kingside
            if move.to_col == 6:
                self.board[move.to_row][7] = self.board[move.to_row][5]
                self.board[move.to_row][5] = EMPTY
            else: # Queenside
                self.board[move.to_row][0] = self.board[move.to_row][3]
                self.board[move.to_row][3] = EMPTY

        # Restore game state
        self.castling_rights = undo_info["castling_rights"]
        self.en_passant_square = undo_info["en_passant_square"]
        self.halfmove_clock = undo_info["halfmove_clock"]

    def from_fen(self, fen):
        # Load a position from FEN notation
        parts = fen.split()

        rows = parts[0].split("/")
        for row_idx, row in enumerate(rows):
            col_idx = 0
            for char in row:
                if char.isdigit():
                    for _ in range(int(char)):
                        self.board[7 - row_idx][col_idx] = 0
                        col_idx += 1
                else:
                    piece_map = {
                        "P" : WHITE | PAWN, "N": WHITE | KNIGHT,
                        "B": WHITE | BISHOP, "R": WHITE | ROOK,
                        "Q": WHITE | QUEEN, "K": WHITE | KING,
                        "p": BLACK | PAWN, "n": BLACK | KNIGHT,
                        "b": BLACK | BISHOP, "r": BLACK | ROOK,
                        "q": BLACK | QUEEN, "k": BLACK | KING  
                    }
                    self.board[7 - row_idx][col_idx] = piece_map[char]
                    col_idx += 1
        
        # Parse side to move
        self.to_move = WHITE if parts[1] == "w" else BLACK

        # Parse castling rights
        castling = parts[2]
        self.castling_rights = {
            "K" : "K" in castling,
            "Q" : "Q" in castling,
            "k" : "k" in castling,
            "q" : "q" in castling
        }

        # Parse en passant
        if parts[3] != "-":
            file = ord(parts[3][0]) - ord('a')
            rank = int(parts[3][1]) - 1
            self.en_passant_square = (rank, file)
        else:
            self.en_passant_square = None

        # Parse move counters
        self.halfmove_clock = int(parts[4])
        self.fullmove_number = int(parts[5])

    def to_fen(self):
        # Convert the current position to FEN notation
        fen_parts = []

        # Board position
        for row in range(7, -1, -1):
            empty_count = 0
            row_str = ""

            for col in range(8):
                piece = self.board[row][col]

                if piece == EMPTY:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0

                    piece_type = piece & 7
                    colour = piece & 24

                    piece_chars = {
                        PAWN: "p", KNIGHT: "n", BISHOP: "b",
                        ROOK: "r", QUEEN: "q", KING: "k"
                    }
                    char = piece_chars[piece_type]
                    if colour == WHITE:
                        char = char.upper()
                    row_str += char

            if empty_count > 0:
                row_str += str(empty_count)

            fen_parts.append(row_str)

        fen = "/".join(fen_parts)

        # Side to move
        fen += " w" if self.to_move == WHITE else " b"

        castling = ""
        if self.castling_rights["K"]:
            castling += "K"
        if self.castling_rights["Q"]:
            castling += "Q"
        if self.castling_rights['k']:
            castling += 'k'
        if self.castling_rights['q']:
            castling += 'q'
        fen += " " + (castling if castling else "-")

        # En passant
        if self.en_passant_square:
            files = "abcdefgh"
            fen += f" {files[self.en_passant_square[1]]}{self.en_passant_square[0] + 1}"
        else:
            fen += " -"

        # Move counters
        fen += f" {self.halfmove_clock} {self.fullmove_number}"

        return fen

    def __str__(self):
        # Display the board in a human-readable format.
        piece_symbols = {
            EMPTY: '.',
            WHITE | PAWN: 'P', WHITE | KNIGHT: 'N', WHITE | BISHOP: 'B',
            WHITE | ROOK: 'R', WHITE | QUEEN: 'Q', WHITE | KING: 'K',
            BLACK | PAWN: 'p', BLACK | KNIGHT: 'n', BLACK | BISHOP: 'b',
            BLACK | ROOK: 'r', BLACK | QUEEN: 'q', BLACK | KING: 'k'
        }

        board_string = "\n  a b c d e f g h\n"
        board_string += "  ---------------\n"
        for row in range(7, -1, -1):
            board_string += f"{row + 1}|"
            for col in range(8):
                piece = self.board[row][col]
                board_string += piece_symbols.get(piece, "?") + " "
            board_string += f"|{row + 1}\n"
        board_string += "  ---------------\n"

        return board_string