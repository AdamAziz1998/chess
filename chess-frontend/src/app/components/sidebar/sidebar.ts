import { Component, input, output } from '@angular/core';
import { NgOptimizedImage } from '@angular/common';
import {GameMode, PlayMode} from '../../common/types';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [NgOptimizedImage],
  templateUrl: './sidebar.html',
})
export class Sidebar {
  gameMode = input.required<GameMode>();
  playMode = input.required<PlayMode>();
  gameStatus = input.required<string>();
  historicalMoves = input.required<string[]>();
  capturedPieces = input.required<{color: string, type: string}[]>();

  gameModeChange = output<GameMode>();
  playModeChange = output<PlayMode>();
  historicalMoveClicked = output<string>();
  flipBoardClicked = output<void>();
  resetGameClicked = output<void>();
}
