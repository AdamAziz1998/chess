import {AfterViewInit, Component, inject, PLATFORM_ID, signal, ViewEncapsulation} from '@angular/core';
import {isPlatformBrowser} from '@angular/common';
import {Chess, Move, Square} from 'chess.js';
import { Subject, EMPTY } from 'rxjs';
import { switchMap, catchError } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {BoardConfig, ChessBoardInstance} from 'chessboardjs';
import {PromotionModal} from '../../components/promotion-modal/promotion-modal';
import {HistoricalMove} from '../../services/historical-move';
import {Sidebar} from '../../components/sidebar/sidebar';
import {ChessEngineService} from '../../services/engine';
import {ChessMove, GameMode, PlayMode} from '../../common/types';

declare const Chessboard: (id: string, config: BoardConfig) => ChessBoardInstance;

@Component({
  selector: 'app-chess',
  imports: [PromotionModal, Sidebar],
  templateUrl: './chess-game.html',
  styleUrl: './chess-game.css',
  encapsulation: ViewEncapsulation.None
})
export class ChessGame implements AfterViewInit {
  gameMode = signal<GameMode>('play');
  playMode = signal<PlayMode>('pvp');
  gameStatus = signal<string>('White to move');
  historicalMoves = signal<ChessMove[]>([]);
  capturedPieces = signal<{color: string, type: string}[]>([]);
  showPromotionModal = signal<boolean>(false);
  promotionPendingMove = signal<{source: string, target: string, color: string} | null>(null);

  private historicalMoveService = inject(HistoricalMove);
  private chessEngineService = inject(ChessEngineService);
  private platformId: object = inject(PLATFORM_ID)

  private boardMoveSubject$ = new Subject<string>();

  private pendingSource: string | null = null;
  private board: ChessBoardInstance | null = null;
  private game: Chess = new Chess();
  private squareHover: string | null = null;

  currentOrientation = signal<'white' | 'black'>('white');

  constructor() {
    this.boardMoveSubject$.pipe(
      takeUntilDestroyed(),
      switchMap((fen) => {
        return this.historicalMoveService.getHistoricalMovesFromFen(fen).pipe(
          catchError((err) => {
            console.error('Failed to fetch moves', err);
            return EMPTY;
          })
        );
      })
    ).subscribe((moves) => {
      const processedMoves = moves.map(move => {
        const total = move.total || 1;
        return {
          ...move,
          whitePct: Math.round((move.white / total) * 100),
          drawPct: Math.round((move.draw / total) * 100),
          blackPct: Math.round((move.black / total) * 100)
        } as ChessMove;
      });
      this.historicalMoves.set(processedMoves);
    });
  }

  flipBoard(): void {
    const newOrientation = this.currentOrientation() === 'white' ? 'black' : 'white';
    this.currentOrientation.set(newOrientation);

    if (this.board) {
      this.board.orientation(newOrientation);
    }
  }

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      setTimeout(() => this.initializeGame(), 500);
    }
  }

  private initializeGame(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.game = new Chess();
    }

    if (this.playMode() === 'ai-black') {
      this.currentOrientation.set('black');
    } else {
      this.currentOrientation.set('white');
    }

    const config = {
      draggable: true,
      position: 'start',
      orientation: this.currentOrientation(),
      pieceTheme: '/assets/img/chess-pieces/wikipedia/{piece}.png',
      onDragStart: this.onDragStart,
      onDrop: this.onDrop,
      onMouseoverSquare: this.onMouseoverSquare,
      onSnapEnd: () => {
        if (this.showPromotionModal()) return;
        if (this.board) {
          this.board.position(this.game.fen());
        }
      }
    } as unknown as BoardConfig;

    const boardEl = document.getElementById('myBoard');
    if (boardEl) {
      this.board = Chessboard('myBoard', config);
    } else {
      console.error("Board container 'myBoard' not found.");
      return;
    }

    this.updateStatus();

    if (this.playMode() === 'ai-black' && this.game.turn() === 'w') {
      setTimeout(() => this.makeAiMove(), 500);
    }
  }

  onDragStart = (source: string, piece: string): boolean => {
    if (this.game.isGameOver()) {
      return false;
    }

    if (this.gameMode() === 'play') {
      if ((this.game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (this.game.turn() === 'b' && piece.search(/^w/) !== -1)) {
        return false;
      }
      if ((this.playMode() === 'ai-white' && this.game.turn() === 'b') ||
        (this.playMode() === 'ai-black' && this.game.turn() === 'w')) {
        return false;
      }
    }
    return true;
  };

  private isPromotion(source: string, target: string): boolean {
    const piece = this.game.get(source as Square);
    if (piece?.type !== 'p') return false;
    if (piece.color !== this.game.turn()) return false;

    const sourceRank = source[1];
    const targetRank = target[1];

    if (piece.color === 'w' && sourceRank === '7' && targetRank === '8') return true;
    return piece.color === 'b' && sourceRank === '2' && targetRank === '1';
  }

  onDrop = (source: string, target: string): string | void => {
    if (source === target) {
      this.onBoardClick();
      return;
    }

    if (this.isPromotion(source, target)) {
      const legalMove = this.game.move({ from: source, to: target, promotion: 'q' });
      if (legalMove) {
        this.game.undo();
        this.promotionPendingMove.set({ source, target, color: this.game.turn() });
        this.showPromotionModal.set(true);
        return;
      } else {
        return 'snapback';
      }
    }

    try {
      const move = this.game.move({
        from: source,
        to: target,
        promotion: 'q'
      });
      if (move === null) return 'snapback';
      this.finalizeMoveLogic(move);
    } catch {
      return 'snapback';
    }
  };

  onMouseoverSquare = (square: string) => {
    this.squareHover = square;
  };

  onBoardClick = (): void => {
    if (!this.board) return;
    if (this.game.isGameOver()) return;
    if (!this.squareHover) return;

    const square = this.squareHover;
    const piece = this.game.get(square as Square);
    const isWhiteTurn = this.game.turn() === 'w';
    const isFriendlyPiece: undefined | boolean = piece && ((isWhiteTurn && piece.color === 'w') || (!isWhiteTurn && piece.color === 'b'));

    if (isFriendlyPiece) {
      if (this.pendingSource === square) {
        this.pendingSource = null;
        this.removeHighlights();
        return;
      }

      if (this.isAiTurn()) return;

      this.removeHighlights();

      this.pendingSource = square;
      this.showLegalMoves(square);
      return;
    }

    if (this.pendingSource) {
      if (this.isPromotion(this.pendingSource, square)) {
        const legalMove = this.game.move({ from: this.pendingSource, to: square, promotion: 'q' });
        if (legalMove) {
          this.game.undo();
          this.promotionPendingMove.set({ source: this.pendingSource, target: square, color: this.game.turn() });
          this.showPromotionModal.set(true);
        } else {
          this.pendingSource = null;
          this.removeHighlights();
        }
        return;
      }

      const move = this.game.move({
        from: this.pendingSource,
        to: square,
        promotion: 'q'
      });

      if (move) {
        this.board.position(this.game.fen());
        this.finalizeMoveLogic(move);
      } else {
        this.pendingSource = null;
        this.removeHighlights();
      }
    }
  };

  promoteTo(type: string): void {
    const pending = this.promotionPendingMove();
    if (!pending) return;
    if (!this.board) return;

    const move = this.game.move({
      from: pending.source,
      to: pending.target,
      promotion: type
    });

    if (move) {
      this.board.position(this.game.fen());
      this.finalizeMoveLogic(move);
    }

    this.showPromotionModal.set(false);
    this.promotionPendingMove.set(null);
  }

  cancelPromotion(): void {
    if (!this.board) return;

    this.showPromotionModal.set(false);
    this.promotionPendingMove.set(null);
    this.board.position(this.game.fen());
    this.pendingSource = null;
    this.removeHighlights();
  }

  private finalizeMoveLogic(move: Move): void {
    if (move.captured) {
      this.addCapturedPiece(move.color === 'w' ? 'b' : 'w', move.captured);
    }

    this.updateStatus();
    this.removeHighlights();
    this.pendingSource = null;

    if(this.gameMode() === 'explore') {
      this.fetchHistoricalMoves(this.game.fen());
    } else {
      if (!this.game.isGameOver() && this.isAiTurn()) {
        setTimeout(() => this.makeAiMove(), 250);
      }
    }
  }

  private isAiTurn(): boolean {
    return (this.playMode() === 'ai-white' && this.game.turn() === 'b') ||
      (this.playMode() === 'ai-black' && this.game.turn() === 'w');
  }

  private makeAiMove(): void {
    if (this.game.isGameOver()) return;

    this.chessEngineService.getBestMoveFromFen(this.game.fen())
      .subscribe({
        next: (response: ChessMove) => {
          const bestMove = response.move;
          try {
            const moveResult = this.game.move(bestMove);

            if (moveResult && this.board) {
              this.board.position(this.game.fen());
              this.finalizeMoveLogic(moveResult);
            }
          } catch {
            console.error('Engine returned an invalid move:', bestMove);
          }
        },
        error: (err) => {
          console.error('Failed to fetch AI move from engine:', err);
        }
      });
  }

  private updateStatus(): void {
    let status: string;
    const moveColor = this.game.turn() === 'b' ? 'Black' : 'White';

    if (this.game.isCheckmate()) {
      const winColor = moveColor.includes('Black') ? 'White' : 'Black';
      status = `Checkmate, ${winColor} wins`;
    } else if (this.game.isDraw()) {
      status = 'Game over, stalemate';
    } else {
      status = `${moveColor} to move`;
      if (this.game.inCheck()) {
        status = `${moveColor} is in check`;
      }
    }
    this.gameStatus.set(status);
  }

  setGameMode(mode: GameMode): void {
    if(this.gameMode() === mode) return;
    this.gameMode.set(mode);
    this.resetGame();
    if(mode === 'explore'){
      this.fetchHistoricalMoves(this.game.fen());
    } else {
      this.historicalMoves.set([]);
    }
  }

  setPlayMode(mode: PlayMode): void {
    if(this.playMode() === mode) return;
    this.playMode.set(mode);
    this.resetGame();
  }

  private addCapturedPiece(color: string, type: string): void {
    this.capturedPieces.update(prev => [...prev, { color, type }]);
  }

  resetGame(): void {
    this.capturedPieces.set([]);
    if (this.board) {
      this.board.destroy();
    }
    this.initializeGame();
  }

  private fetchHistoricalMoves(fen: string): void {
    this.boardMoveSubject$.next(fen);
  }

  onHistoricalMoveClick(move: string): void {
    if (!this.board) return;
    if (this.gameMode() !== 'explore' || this.game.isGameOver()) return;

    const result = this.game.move(move);
    if (result) {
      this.board.position(this.game.fen());
      this.updateStatus();
      this.fetchHistoricalMoves(this.game.fen());
    }
  }

  private removeHighlights(): void {
    const boardEl = document.getElementById('myBoard');
    if (boardEl) {
      boardEl.querySelectorAll('.square-55d63').forEach(el => {
        el.classList.remove('highlight-selected', 'highlight-move', 'highlight-capture');
      });
    }
  }

  private addHighlight(square: string, type: 'selected' | 'move' | 'capture'): void {
    const squareEl = document.querySelector(`#myBoard .square-${square}`);
    if (squareEl) {
      if (type === 'selected') {
        squareEl.classList.add('highlight-selected');
      } else if (type === 'capture') {
        squareEl.classList.add('highlight-capture');
      } else {
        squareEl.classList.add('highlight-move');
      }
    }
  }

  private showLegalMoves(square: string): void {
    const moves = this.game.moves({
      square: square as Square,
      verbose: true
    });

    if (moves.length === 0) return;

    this.addHighlight(square, 'selected');

    moves.forEach((move: Move) => {
      const isCapture = move.captured !== undefined;
      this.addHighlight(move.to, isCapture ? 'capture' : 'move');
    });
  }

  updateBoardFromFen(fen: string): void {
    try {
      this.game.load(fen);

      if (this.board) {
        this.board.position(fen);
      }
      this.updateStatus();

      if (this.gameMode() === 'explore') {
        this.fetchHistoricalMoves(fen);
      }
    } catch (e) {
      console.error("Error updating board from FEN:", e);
    }
  }
}
