import {Component, inject, input, output, signal} from '@angular/core';
import {NgClass, NgOptimizedImage} from '@angular/common';
import {GameMode, PlayMode, HistoricalData} from '../../common/types';
import {HistoricalMove} from '../../services/historical-move';
import { validateFen } from 'chess.js';
import { Subject } from 'rxjs';
import {NumberFormatPipe} from '../../pipes/number-word';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [NgOptimizedImage, NgClass, NumberFormatPipe],
  templateUrl: './sidebar.html',
})
export class Sidebar {
  private historicalMoveService = inject(HistoricalMove);

  // Inputs
  gameMode = input.required<GameMode>();
  playMode = input.required<PlayMode>();
  gameStatus = input.required<string>();
  historicalData = input.required<HistoricalData | null>();
  capturedPieces = input.required<{color: string, type: string}[]>();

  // Signals
  showAll = signal(false);
  fen = signal('');
  error = signal<string | null>(null);

  // Outputs
  gameModeChange = output<GameMode>();
  playModeChange = output<PlayMode>();
  historicalMoveClicked = output<string>();
  flipBoardClicked = output<void>();
  resetGameClicked = output<void>();
  fenPositionEntered = output<string>();

  // RxJS Trigger
  private searchSubject$ = new Subject<string>();

  findMoves() {
    const currentFen = this.fen().trim();
    const validation = validateFen(currentFen);

    if (!validation.ok) {
      this.error.set(`Invalid position: ${validation.error}`);
      return;
    }

    this.fenPositionEntered.emit(currentFen);
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
