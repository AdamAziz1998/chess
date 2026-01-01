import {Component, inject, input, output, signal} from '@angular/core';
import { NgOptimizedImage } from '@angular/common';
import {GameMode, PlayMode} from '../../common/types';
import {HistoricalMoveService} from '../../services/historical-move.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [NgOptimizedImage],
  templateUrl: './sidebar.html',
})
export class Sidebar {
  private historicalMoveService = inject(HistoricalMoveService);

  gameMode = input.required<GameMode>();
  playMode = input.required<PlayMode>();
  gameStatus = input.required<string>();
  historicalMoves = input.required<string[]>();
  capturedPieces = input.required<{color: string, type: string}[]>();

  fen = signal('');
  loading = signal(false);
  error = signal<string | null>(null);
  moves = signal<string[]>([]);
  hasSearched = signal(false);

  gameModeChange = output<GameMode>();
  playModeChange = output<PlayMode>();
  historicalMoveClicked = output<string>();
  flipBoardClicked = output<void>();
  resetGameClicked = output<void>();

  async findMoves() {
    this.loading.set(true);
    this.error.set(null);
    this.moves.set([]);
    this.hasSearched.set(true);
    try {
      const result = await this.historicalMoveService.getMovesFromFen(this.fen());
      this.moves.set(result);
    } catch (e: unknown) {
      this.error.set(
        e instanceof Error ? e.message : 'An unknown error occurred.'
      );
    } finally {
      this.loading.set(false);
    }
  }

  async playMove(move: string) {
    this.loading.set(true);

    console.log('Playing move:', move);
    // In a real app, this would emit an event to a parent component.
  }

  onFenInput(event: Event) {
    const input = event.target as HTMLInputElement;
    this.fen.set(input.value);
  }
}
