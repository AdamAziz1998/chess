import {inject, Injectable} from '@angular/core';
import {HistoricalData} from '../common/types';
import {Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../environments/environent';

@Injectable({providedIn: 'root'})
export class HistoricalMove {
  private http: HttpClient = inject(HttpClient);
  private readonly baseUrl = environment.historicalUrl;

  getHistoricalMovesFromFen(fen: string): Observable<HistoricalData> {
    const encodedFen = encodeURIComponent(fen);
    return this.http.get<HistoricalData>(`${this.baseUrl}/${encodedFen}`);
  }
}
