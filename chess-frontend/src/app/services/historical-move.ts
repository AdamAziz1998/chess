import {inject, Injectable} from '@angular/core';
import {ChessMove} from '../common/types';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../environments/environent';

@Injectable({providedIn: 'root'})
export class HistoricalMove {
  private http: HttpClient = inject(HttpClient);
  private readonly baseUrl = environment.historicalUrl;

  getHistoricalMovesFromFen(fen: string): Observable<ChessMove[]> {
    const encodedFen = encodeURIComponent(fen);
    return this.http.get<ChessMove[]>(`${this.baseUrl}/${encodedFen}`);
  }
}
