import { TestBed } from '@angular/core/testing';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient, HttpErrorResponse } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { ChessEngineService } from './engine';
import { environment } from '../../environments/environent';

describe('ChessEngineService', () => {
  let service: ChessEngineService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ChessEngineService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(ChessEngineService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // Verify no outstanding HTTP requests
    httpMock.verify();
  });

  describe('getBestMoveFromFen', () => {
    const mockMove = 'e2e4'; // Changed from object to string

    it('should be created', () => {
      expect(service).toBeTruthy();
    });

    it('should correctly encode FEN string in request URL', () => {
      const fenString = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      const encodedFen = encodeURIComponent(fenString);
      const expectedUrl = `${environment.engineUrl}/${encodedFen}`; // Changed to engineUrl

      service.getBestMoveFromFen(fenString).subscribe();

      const req = httpMock.expectOne(expectedUrl);
      expect(req.request.method).toBe('GET');
      expect(req.request.url).toContain(encodedFen);

      req.flush(mockMove);
    });

    it('should encode FEN with special characters correctly', () => {
      // FEN with en passant square and more complex state
      const fenString = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1';
      const encodedFen = encodeURIComponent(fenString);

      service.getBestMoveFromFen(fenString).subscribe();

      const req = httpMock.expectOne((request) =>
        request.url.includes(encodedFen)
      );
      expect(req.request.method).toBe('GET');

      // Verify spaces are encoded as %20
      expect(req.request.url).toContain('%20');

      req.flush(mockMove);
    });

    it('should return a string on successful response', async () => {
      const fenString = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -';

      const resultPromise = firstValueFrom(service.getBestMoveFromFen(fenString));

      const req = httpMock.expectOne((request) =>
        request.url.startsWith(environment.engineUrl) // Changed to engineUrl
      );
      req.flush(mockMove);

      const result = await resultPromise;
      // Now expecting just the string response
      expect(result).toBe(mockMove);
    });

    it('should handle 500 Internal Server Error gracefully', async () => {
      const fenString = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -';

      const resultPromise = firstValueFrom(service.getBestMoveFromFen(fenString));

      const req = httpMock.expectOne((request) =>
        request.url.startsWith(environment.engineUrl) // Changed to engineUrl
      );

      req.flush('Internal Server Error', {
        status: 500,
        statusText: 'Internal Server Error',
      });

      try {
        await resultPromise;
        expect(true).toBe(false); // Should not reach here
      } catch (error) {
        expect(error).toBeInstanceOf(HttpErrorResponse);
        expect((error as HttpErrorResponse).status).toBe(500);
        expect((error as HttpErrorResponse).statusText).toBe('Internal Server Error');
      }
    });

    it('should handle 404 Not Found error', async () => {
      const fenString = '8/8/8/8/8/8/8/8 w - -'; // Empty board - unlikely to be in DB

      const resultPromise = firstValueFrom(service.getBestMoveFromFen(fenString));

      const req = httpMock.expectOne((request) =>
        request.url.startsWith(environment.engineUrl) // Changed to engineUrl
      );

      req.flush({ detail: 'Position not found' }, {
        status: 404,
        statusText: 'Not Found',
      });

      try {
        await resultPromise;
        expect(true).toBe(false); // Should not reach here
      } catch (error) {
        expect(error).toBeInstanceOf(HttpErrorResponse);
        expect((error as HttpErrorResponse).status).toBe(404);
      }
    });

    it('should handle network error', async () => {
      const fenString = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -';

      const resultPromise = firstValueFrom(service.getBestMoveFromFen(fenString));

      const req = httpMock.expectOne((request) =>
        request.url.startsWith(environment.engineUrl) // Changed to engineUrl
      );

      req.error(new ProgressEvent('error'), {
        status: 0,
        statusText: 'Unknown Error',
      });

      try {
        await resultPromise;
        expect(true).toBe(false); // Should not reach here
      } catch (error) {
        expect(error).toBeInstanceOf(HttpErrorResponse);
        expect((error as HttpErrorResponse).status).toBe(0);
      }
    });

    it('should handle 400 Bad Request for invalid FEN', async () => {
      const invalidFen = 'not_a_valid_fen';

      const resultPromise = firstValueFrom(service.getBestMoveFromFen(invalidFen));

      const req = httpMock.expectOne((request) =>
        request.url.startsWith(environment.engineUrl) // Changed to engineUrl
      );

      req.flush({ detail: 'Invalid FEN string' }, {
        status: 400,
        statusText: 'Bad Request',
      });

      try {
        await resultPromise;
        expect(true).toBe(false); // Should not reach here
      } catch (error) {
        expect(error).toBeInstanceOf(HttpErrorResponse);
        expect((error as HttpErrorResponse).status).toBe(400);
      }
    });

    it('should handle timeout/503 Service Unavailable', async () => {
      const fenString = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -';

      const resultPromise = firstValueFrom(service.getBestMoveFromFen(fenString));

      const req = httpMock.expectOne((request) =>
        request.url.startsWith(environment.engineUrl) // Changed to engineUrl
      );

      req.flush('Service Unavailable', {
        status: 503,
        statusText: 'Service Unavailable',
      });

      try {
        await resultPromise;
        expect(true).toBe(false); // Should not reach here
      } catch (error) {
        expect(error).toBeInstanceOf(HttpErrorResponse);
        expect((error as HttpErrorResponse).status).toBe(503);
      }
    });
  });

  describe('URL construction', () => {
    it('should use correct base URL from environment', () => {
      const fenString = 'test';

      service.getBestMoveFromFen(fenString).subscribe();

      const req = httpMock.expectOne((request) =>
        request.url.startsWith(environment.engineUrl) // Changed to engineUrl
      );

      expect(req.request.url).toBe(`${environment.engineUrl}/${fenString}`); // Changed to engineUrl
      req.flush('e4');
    });

    it('should handle FEN with slashes correctly after encoding', () => {
      // FEN strings contain many forward slashes
      const fenString = 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq -';

      service.getBestMoveFromFen(fenString).subscribe();

      const req = httpMock.expectOne((request) => {
        // Verify slashes are properly encoded as %2F
        return request.url.includes('%2F');
      });

      expect(req.request.method).toBe('GET');
      req.flush('e4');
    });
  });
});
