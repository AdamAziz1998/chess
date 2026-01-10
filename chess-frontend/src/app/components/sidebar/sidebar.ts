import {Component, inject, input, output, signal} from '@angular/core';
import {NgClass, NgOptimizedImage} from '@angular/common';
import {ChessMove, GameMode, PlayMode} from '../../common/types';
import {HistoricalMove} from '../../services/historical-move';
import { validateFen } from 'chess.js';
import { Subject, EMPTY } from 'rxjs';
import { switchMap, catchError, tap } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [NgOptimizedImage, NgClass],
  templateUrl: './sidebar.html',
})
export class Sidebar {
  private historicalMoveService = inject(HistoricalMove);

  // Inputs
  gameMode = input.required<GameMode>();
  playMode = input.required<PlayMode>();
  gameStatus = input.required<string>();
  historicalMoves = input.required<ChessMove[]>();
  capturedPieces = input.required<{color: string, type: string}[]>();

  // Signals
  showAll = signal(false);
  fen = signal('');
  loading = signal(false);
  error = signal<string | null>(null);
  moves = signal<ChessMove[]>([]);
  hasSearched = signal(false);

  // Outputs
  gameModeChange = output<GameMode>();
  playModeChange = output<PlayMode>();
  historicalMoveClicked = output<string>();
  flipBoardClicked = output<void>();
  resetGameClicked = output<void>();
  fenPositionEntered = output<string>();

  // RxJS Trigger
  private searchSubject$ = new Subject<string>();

  constructor() {
    this.searchSubject$.pipe(
      takeUntilDestroyed(),
      tap(() => {
        this.loading.set(true);
        this.error.set(null);
        this.moves.set([]);
        this.hasSearched.set(true);
      }),

      switchMap((fen) => {

        return this.historicalMoveService.getHistoricalMovesFromFen(fen).pipe(
          catchError((err) => {
            this.error.set(err instanceof Error ? err.message : 'An unknown error occurred.');
            this.loading.set(false);
            return EMPTY;
          })
        );
      })
    ).subscribe((result) => {
      const processedMoves = result.map(move => {
        const total = move.total || 1;
        return {
          ...move,
          whitePct: Math.round((move.white / total) * 100),
          drawPct: Math.round((move.draw / total) * 100),
          blackPct: Math.round((move.black / total) * 100)
        } as ChessMove;
      });

      this.moves.set(processedMoves);
      this.loading.set(false);
    });
  }

  findMoves() {
    const currentFen = this.fen().trim();
    const validation = validateFen(currentFen);

    if (!validation.ok) {
      this.error.set(`Invalid position: ${validation.error}`);
      return;
    }

    this.fenPositionEntered.emit(currentFen);
    this.searchSubject$.next(currentFen);
  }

  onFenInput(event: Event) {
    const input = event.target as HTMLInputElement;
    this.fen.set(input.value);

    if (this.error()) {
      this.error.set(null);
    }
  }

  toggleShowAll() {
    this.showAll.update(v => !v);
  }

  closeError() {
    this.error.set(null);
  }
}
