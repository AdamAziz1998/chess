import { Injectable } from '@angular/core';
import {dummyMoves} from '../common/constants';
import {ChessMove} from '../common/types';

@Injectable({providedIn: 'root'})
export class HistoricalMoveService {

  async getMovesFromFen(fen: string): Promise<ChessMove[]> {
    try {
      return dummyMoves;
    } catch (error) {
      console.error('Error fetching moves:', error);
      throw new Error('Could not fetch moves. Please check the FEN string and your API key.');
    }
  }
}
