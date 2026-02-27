import { Routes } from '@angular/router';
import {Home} from './pages/home/home';
import {ChessGame} from './pages/chess/chess-game';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'home', component: Home },
  { path: 'chess', component: ChessGame },
];
