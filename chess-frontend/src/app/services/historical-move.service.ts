import { Injectable } from '@angular/core';

@Injectable({providedIn: 'root'})
export class HistoricalMoveService {

  async getMovesFromFen(fen: string): Promise<string[]> {
    try {
      return ['a1', 'a2', 'a3', 'a4'];
    } catch (error) {
      console.error('Error fetching moves:', error);
      throw new Error('Could not fetch moves. Please check the FEN string and your API key.');
    }
  }
}
