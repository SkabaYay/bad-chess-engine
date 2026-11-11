from board import Board
from search import SearchEngine
from evaluation import Evaluator
from move import Move
from constants import *

def play_game():
    """Play a game against PyMinMaximus."""
    board = Board()
    evaluator = Evaluator()
    engine = SearchEngine(board, evaluator)
    
    print("Welcome to PyMinMaximus!")
    print("You are White. Enter moves in format: e2e4")
    print("Enter 'quit' to exit\n")
    
    while True:
        # Display board
        print(board)
        
        # Check game over
        legal_moves = board.generate_legal_moves()
        if len(legal_moves) == 0:
            if board.is_in_check(board.to_move):
                winner = "Black" if board.to_move == WHITE else "White"
                print(f"\nCheckmate! {winner} wins!")
            else:
                print("\nStalemate!")
            break
        
        if board.to_move == WHITE:
            # Human move
            while True:
                move_str = input("Your move: ").strip().lower()
                
                if move_str == 'quit':
                    return
                
                # Parse move
                if len(move_str) < 4:
                    print("Invalid format. Use: e2e4")
                    continue
                
                try:
                    from_col = ord(move_str[0]) - ord('a')
                    from_row = int(move_str[1]) - 1
                    to_col = ord(move_str[2]) - ord('a')
                    to_row = int(move_str[3]) - 1
                    
                    # Check for promotion
                    promotion = None
                    if len(move_str) == 5:
                        promo_map = {'q': QUEEN, 'r': ROOK, 'b': BISHOP, 'n': KNIGHT}
                        promotion = promo_map.get(move_str[4])
                    
                    # Find matching legal move
                    user_move = None
                    for move in legal_moves:
                        if (move.from_row == from_row and move.from_col == from_col and
                            move.to_row == to_row and move.to_col == to_col):
                            if promotion is None or move.promotion == promotion:
                                user_move = move
                                break
                    
                    if user_move:
                        board.make_move(user_move)
                        break
                    else:
                        print("Illegal move. Try again.")
                
                except (ValueError, IndexError):
                    print("Invalid format. Use: e2e4")
        
        else:
            # Engine move
            print("\nPyMinMaximus is thinking...")
            best_move, score = engine.iterative_deepening(5, time_limit=3.0)
            
            if best_move:
                print(f"PyMinMaximus plays: {best_move} (eval: {score:+d})")
                board.make_move(best_move)
            else:
                print("PyMinMaximus has no legal moves!")
                break

def self_play_comparison():
    # Compare material-only vs positional evaluation
    # Play the two versions against each other
    from board import Board
    from search import SearchEngine
    from evaluation import Evaluator
    
    print("Material-Only vs. Positional Evaluation")
    print("Playing 1 game at depth 5\n")
    
    board = Board()
    
    # Create two engines
    material_evaluator = Evaluator()
    # Disable all positional evaluation
    material_evaluator.pawn_table = [[0]*8 for _ in range(8)]
    material_evaluator.knight_table = [[0]*8 for _ in range(8)]
    material_evaluator.bishop_table = [[0]*8 for _ in range(8)]
    material_evaluator.rook_table = [[0]*8 for _ in range(8)]
    material_evaluator.queen_table = [[0]*8 for _ in range(8)]
    material_evaluator.king_middlegame_table = [[0]*8 for _ in range(8)]
    material_evaluator.king_endgame_table = [[0]*8 for _ in range(8)]
    
    positional_evaluator = Evaluator()  # Full evaluation
    
    engine1 = SearchEngine(board, material_evaluator)
    engine2 = SearchEngine(board, positional_evaluator)
    
    move_count = 0
    max_moves = 100
    
    while move_count < max_moves:
        legal_moves = board.generate_legal_moves()
        
        if len(legal_moves) == 0:
            if board.is_in_check(board.to_move):
                winner = "Positional" if board.to_move == WHITE else "Material"
                print(f"\nCheckmate! {winner} evaluation wins!")
            else:
                print("\nStalemate!")
            break
        
        if board.to_move == WHITE:
            # Material-only engine
            best_move, score = engine1.find_best_move_alphabeta(5)
            print(f"{move_count + 1}. Material: {best_move}")
        else:
            # Positional engine
            best_move, score = engine2.find_best_move_alphabeta(5)
            print(f"{move_count + 1}... Positional: {best_move}")
        
        if best_move:
            board.make_move(best_move)
            move_count += 1
        else:
            break
    
    if move_count >= max_moves:
        print(f"\nGame drawn by move limit ({max_moves} moves)")
                
if __name__ == "__main__":
    play_game()