export type GameMode = 'explore' | 'play';
export type PlayMode = 'pvp' | 'ai-white' | 'ai-black';

export interface ChessMove {
  move: string;
  total: number;
  white: number;
  black: number;
  draw: number;
  whitePct?: number;
  drawPct?: number;
  blackPct?: number;
}
