import {AfterViewInit, Component, computed, Inject, PLATFORM_ID, signal} from '@angular/core';
import {isPlatformBrowser} from '@angular/common';
import {Chess} from 'chess.js';

declare var Chessboard: any;

type GameMode = 'explore' | 'play';
type PlayMode = 'pvp' | 'ai-white' | 'ai-black';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements AfterViewInit{
  gameMode = signal<GameMode>('play');
  playMode = signal<PlayMode>('pvp');
  gameStatus = signal<string>('White to move.');
  historicalMoves = signal<string[]>([]);

  private board: any;
  private game: any;

  currentOrientation = signal<'white' | 'black'>('white');

  flipBoard(): void {
    // 1. Update the state signal
    const newOrientation = this.currentOrientation() === 'white' ? 'black' : 'white';
    this.currentOrientation.set(newOrientation);

    // 2. Update the physical board if it exists
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
    try {
      const move = this.game.move({
        from: source,
        to: target,
        promotion: 'q'
      });

      if (move === null) {
        return 'snapback';
      }

      this.updateStatus();

      if(this.gameMode() === 'explore') {
        this.fetchHistoricalMoves(this.game.fen());
      } else {
        if (!this.game.isGameOver() && this.isAiTurn()) {
          setTimeout(() => this.makeAiMove(), 250);
        }
      }
    } catch (e) {
      console.error("Error on drop:", e);
      return 'snapback';
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
    this.game.move(randomMove);
    this.board.position(this.game.fen());
    this.updateStatus();
  }

  private updateStatus(): void {
    let status = '';
    const moveColor = this.game.turn() === 'b' ? 'Black' : 'White';

    if (this.game.isCheckmate()) {
      const winColor = moveColor.includes('Black') ? 'White' : 'Black';
      status = `Game over, ${winColor} wins`;
    } else if (this.game.isDraw()) {
      status = 'Game over, stalemate';
    } else {
      status = `${moveColor}'s Turn`;
      if (this.game.inCheck()) {
        status += ` ${moveColor} is in check`;
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

  resetGame(): void {
    if (this.board) {
      this.board.destroy();
    }
    this.initializeGame();
  }

  private fetchHistoricalMoves(fen: string): void {
    console.log("Fetching historical moves for FEN:", fen);
    // This is a mock implementation as requested.
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
}
