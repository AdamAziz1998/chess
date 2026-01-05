export type GameMode = 'explore' | 'play';
export type PlayMode = 'pvp' | 'ai-white' | 'ai-black';

export type ChessMove = {
  move: string;
  total: number;
  white: number;
  black: number;
  draw: number;
}
