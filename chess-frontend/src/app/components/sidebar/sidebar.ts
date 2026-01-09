import {Component, inject, input, output, signal} from '@angular/core';
import {NgClass, NgOptimizedImage} from '@angular/common';
import {ChessMove, GameMode, PlayMode} from '../../common/types';
import {HistoricalMove} from '../../services/historical-move';
import {Chess, validateFen} from 'chess.js';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [NgOptimizedImage, NgClass],
  templateUrl: './sidebar.html',
})
export class Sidebar {
  private historicalMoveService = inject(HistoricalMove);

  gameMode = input.required<GameMode>();
  playMode = input.required<PlayMode>();
  gameStatus = input.required<string>();
  showAll = signal(false);
  historicalMoves = input.required<ChessMove[]>();
  capturedPieces = input.required<{color: string, type: string}[]>();

  fen = signal('');
  loading = signal(false);
  error = signal<string | null>(null);
  moves = signal<ChessMove[]>([]);
  hasSearched = signal(false);

  gameModeChange = output<GameMode>();
  playModeChange = output<PlayMode>();
  historicalMoveClicked = output<string>();
  flipBoardClicked = output<void>();
  resetGameClicked = output<void>();
  fenPositionEntered = output<string>();

  async findMoves() {
    const currentFen = this.fen().trim();
    const validation = validateFen(currentFen);

    if (!validation.ok) {
      this.error.set(`Invalid position: ${validation.error}`);
      return;
    }

    this.loading.set(true);
    this.error.set(null);
    this.moves.set([]);
    this.hasSearched.set(true);

    try {
      this.fenPositionEntered.emit(currentFen);

      const result = await this.historicalMoveService.getMovesFromFen(currentFen);
      this.moves.set(
        result.map(move => {
          const total = move.total || 1;
          return {
            ...move,
            whitePct: Math.round((move.white / total) * 100),
            drawPct: Math.round((move.draw / total) * 100),
            blackPct: Math.round((move.black / total) * 100)
          } as ChessMove;
        })
      );
    } catch (e: unknown) {
      this.error.set(e instanceof Error ? e.message : 'An unknown error occurred.');
    } finally {
      this.loading.set(false);
    }
  }

  onFenInput(event: Event) {
    const input = event.target as HTMLInputElement;
    this.fen.set(input.value);
  }

  toggleShowAll() {
    this.showAll.update(v => !v);
  }

  calcPct(denominator: number, numerator: number) {
    return Math.round((numerator/denominator) * 100)
  }
}
