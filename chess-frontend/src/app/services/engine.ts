import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ChessEngineService {
  private http: HttpClient = inject(HttpClient);
  private readonly engineUrl = environment.engineUrl;

  getBestMoveFromFen(fen: string): Observable<string> {
    const encodedFen = encodeURIComponent(fen);
    return this.http.get<string>(`${this.engineUrl}/${encodedFen}`);
  }
}
