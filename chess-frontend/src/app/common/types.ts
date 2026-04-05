export type GameMode = 'explore' | 'play';
export type PlayMode = 'pvp' | 'ai-white' | 'ai-black';

export interface Player {
  name: string;
  rating: number;
}

export interface Game {
  uci: string;
  id: string;
  winner: 'white' | 'black' | null;
  speed: string;
  mode: string;
  black: Player;
  white: Player;
  year: number;
  month: string;
}

export interface Opening {
  eco: string;
  name: string;
}

export interface HistoricalMoveData {
  uci: string;
  san: string;
  averageRating: number;
  white: number;
  draws: number;
  black: number;
  game: any | null;
  opening: Opening | null;
  total?: number;
  whitePct?: number;
  drawPct?: number;
  blackPct?: number;
}

export interface HistoricalData {
  white: number;
  draws: number;
  black: number;
  moves: HistoricalMoveData[];
  recentGames: Game[];
  topGames: Game[];
  opening: Opening | null;
  total?: number;
  whitePct?: number;
  drawPct?: number;
  blackPct?: number;
}
