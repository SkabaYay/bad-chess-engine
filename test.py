import unittest
from board import Board
from evaluation import Evaluator
from move import Move
from constants import *

class TestEvaluation(unittest.TestCase):
    def test_evaluation(self):
        """Test evaluation on various positions."""
        
        evaluator = Evaluator()
        
        positions = [
            {
                'name': 'Starting Position',
                'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'expected': 'About equal (0)'
            },
            {
                'name': 'White Up a Queen',
                'fen': 'rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'expected': 'White winning (+900)'
            },
            {
                'name': 'Knight on Rim vs Center',
                'fen': '8/8/8/4N3/8/8/n7/8 w - - 0 1',
                'expected': 'White better (knight in center better than rim)'
            },
            {
                'name': 'Passed Pawn',
                'fen': '8/8/8/8/8/3P4/8/8 w - - 0 1',
                'expected': 'Passed pawn bonus'
            },
            {
                'name': 'Doubled Pawns',
                'fen': '8/8/8/8/3P4/3P4/8/8 w - - 0 1',
                'expected': 'Doubled pawns penalty'
            },
            {
                'name': 'Castled vs Uncastled King',
                'fen': 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1',
                'expected': 'Equal material, but evaluation considers king safety'
            }
        ]
        
        for pos in positions:
            print(f"\n{'='*60}")
            print(f"Position: {pos['name']}")
            print(f"Expected: {pos['expected']}")
            print('='*60)
            
            board = Board()
            board.from_fen(pos['fen'])
            
            score = evaluator.evaluate(board)
            print(f"Evaluation: {score:+d} centipawns ({score/100:+.2f} pawns)")
            
            # Show breakdown
            print("\nBreakdown:")
            
            # Material only
            material_eval = Evaluator()
            material_eval.piece_values = evaluator.piece_values
            material_score = 0
            for row in range(8):
                for col in range(8):
                    piece = board.board[row][col]
                    if piece != EMPTY:
                        piece_type = piece & 7
                        color = piece & 24
                        value = material_eval.piece_values[piece_type]
                        if color == WHITE:
                            material_score += value
                        else:
                            material_score -= value
            
            print(f"  Material: {material_score:+d}")
            print(f"  Positional: {score - material_score:+d}")


    def test_positions(self):
        """Compare how evaluation changes after moves."""
        
        print("\n" + "="*60)
        print("Comparing Evaluation Before and After Moves")
        print("="*60)
        
        board = Board()
        evaluator = Evaluator()
        
        # Test opening principles
        print("\n1. Center Control: e4 vs. h4")
        
        board1 = Board()
        score_start = evaluator.evaluate(board1)
        
        # e4 - good center move
        board1.make_move(Move(1, 4, 3, 4))
        score_e4 = evaluator.evaluate(board1)
        
        board2 = Board()
        # h4 - poor edge move
        board2.make_move(Move(1, 7, 3, 7))
        score_h4 = evaluator.evaluate(board2)
        
        print(f"Starting position: {score_start:+d}")
        print(f"After 1.e4: {score_e4:+d} (improvement: {score_e4 - score_start:+d})")
        print(f"After 1.h4: {score_h4:+d} (improvement: {score_h4 - score_start:+d})")
        print(f"e4 is better by: {score_e4 - score_h4:+d} centipawns")
        
        # Test knight development
        print("\n2. Knight Development: Nf3 vs. Na3")
        
        board3 = Board()
        board3.make_move(Move(1, 4, 3, 4))  # e4
        score_before = evaluator.evaluate(board3)
        
        # Nf3 - good square
        board3_nf3 = Board()
        board3_nf3.from_fen(board3.to_fen())
        board3_nf3.make_move(Move(0, 6, 2, 5))  # Nf3
        score_nf3 = evaluator.evaluate(board3_nf3)
        
        # Na3 - rim square
        board3_na3 = Board()
        board3_na3.from_fen(board3.to_fen())
        board3_na3.make_move(Move(0, 1, 2, 0))  # Na3
        score_na3 = evaluator.evaluate(board3_na3)
        
        print(f"After 1.e4 (White to move): {score_before:+d}")
        print(f"After 1.e4 Nf3: {score_nf3:+d}")
        print(f"After 1.e4 Na3: {score_na3:+d}")
        print(f"Nf3 is better by: {score_nf3 - score_na3:+d} centipawns")


if __name__ == "__main__":
    unittest.main()