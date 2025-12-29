import {AfterViewInit, Component, computed, Inject, PLATFORM_ID, signal, ViewEncapsulation} from '@angular/core';
import {isPlatformBrowser, NgOptimizedImage} from '@angular/common';
import {Chess} from 'chess.js';

declare var Chessboard: any;

type GameMode = 'explore' | 'play';
type PlayMode = 'pvp' | 'ai-white' | 'ai-black';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  imports: [
    NgOptimizedImage
  ],
  styleUrl: './app.css',
  encapsulation: ViewEncapsulation.None
})
export class App implements AfterViewInit{
  gameMode = signal<GameMode>('play');
  playMode = signal<PlayMode>('pvp');
  gameStatus = signal<string>('White to move');
  historicalMoves = signal<string[]>([]);
  capturedPieces = signal<{color: string, type: string}[]>([]);
  private pendingSource: string | null = null;

  private board: any;
  private game: any;

  currentOrientation = signal<'white' | 'black'>('white');

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

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

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
      pieceTheme: '/assets/img/chesspieces/wikipedia/{piece}.png',
      onDragStart: this.onDragStart,
      onDrop: this.onDrop,
      onSquareClick: this.onSquareClick,
      onSnapEnd: () => {
        if (this.board) {
          this.board.position(this.game.fen());
        }
      }
    };

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

  onDrop = (source: string, target: string): string | void => {
    if (source === target) {
      this.onSquareClick(source);
      return;
    }
    try {
      const move = this.game.move({
        from: source,
        to: target,
        promotion: 'q'
      });
      if (move === null) return 'snapback';
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
    } catch (e) {
      return 'snapback';
    }
  };

  onSquareClick = (square: string): void => {
    if (this.game.isGameOver()) return;

    const piece = this.game.get(square);
    const isWhiteTurn = this.game.turn() === 'w';
    const isFriendlyPiece = piece && ((isWhiteTurn && piece.color === 'w') || (!isWhiteTurn && piece.color === 'b'));

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
      const move = this.game.move({
        from: this.pendingSource,
        to: square,
        promotion: 'q'
      });

      if (move) {
        this.board.position(this.game.fen());
        this.updateStatus();
        if (move.captured) {
          this.addCapturedPiece(move.color === 'w' ? 'b' : 'w', move.captured);
        }
        this.pendingSource = null;
        this.removeHighlights();

        if (!this.game.isGameOver() && this.isAiTurn()) {
          setTimeout(() => this.makeAiMove(), 250);
        }
      } else {
        this.pendingSource = null;
        this.removeHighlights();
      }
    }
  };

  private isAiTurn(): boolean {
    return (this.playMode() === 'ai-white' && this.game.turn() === 'b') ||
      (this.playMode() === 'ai-black' && this.game.turn() === 'w');
  }

  private makeAiMove(): void {
    if (this.game.isGameOver()) return;

    const moves = this.game.moves();
    const randomMove = moves[Math.floor(Math.random() * moves.length)];
    const moveResult = this.game.move(randomMove);

    if (moveResult.captured) {
      this.addCapturedPiece(moveResult.color === 'w' ? 'b' : 'w', moveResult.captured);
    }

    this.board.position(this.game.fen());
    this.updateStatus();
  }

  private updateStatus(): void {
    let status = '';
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
    console.log("Fetching historical moves for FEN:", fen);
    const dummyMoves = ['e4', 'd4', 'Nf3', 'c4', 'g3', 'f4'];
    this.historicalMoves.set(dummyMoves.filter(move => this.game.move(move, {dry_run: true})));
  }

  onHistoricalMoveClick(move: string): void {
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
        el.classList.remove('highlight-selected', 'highlight-move');
      });
    }
  }

  private addHighlight(square: string, type: 'selected' | 'move'): void {
    const squareEl = document.querySelector(`#myBoard .square-${square}`);
    if (squareEl) {
      squareEl.classList.add(type === 'selected' ? 'highlight-selected' : 'highlight-move');
    }
  }

  private showLegalMoves(square: string): void {
    const moves = this.game.moves({
      square: square,
      verbose: true
    });

    if (moves.length === 0) return;

    this.addHighlight(square, 'selected');

    moves.forEach((move: any) => {
      this.addHighlight(move.to, 'move');
    });
  }
}
