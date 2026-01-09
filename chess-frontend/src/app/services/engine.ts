import {inject, Injectable} from '@angular/core';
import {ChessMove} from '../common/types';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import { environment } from '../../environements/environent';

@Injectable({providedIn: 'root'})
export class HistoricalMove {
  private http: HttpClient = inject(HttpClient);
  private readonly baseUrl = environment.historicalUrl;

  getBestMoveFromFen(fen: string): Observable<ChessMove> {
    return this.http.get<ChessMove>(`${this.baseUrl}/${fen}`);
  }
}
