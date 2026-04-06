import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Sidebar } from './sidebar';
import { HistoricalMove } from '../../services/historical-move';
import { vi } from 'vitest';

// Create a simple mock for the injected service
class MockHistoricalMoveService {}

describe('Sidebar', () => {
  let component: Sidebar;
  let fixture: ComponentFixture<Sidebar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Sidebar],
      providers: [
        { provide: HistoricalMove, useClass: MockHistoricalMoveService }
      ]
    })
      .compileComponents();

    fixture = TestBed.createComponent(Sidebar);
    component = fixture.componentInstance;

    // Set all required inputs to satisfy Angular's input.required()
    fixture.componentRef.setInput('gameMode', 'practice');
    fixture.componentRef.setInput('playMode', 'white');
    fixture.componentRef.setInput('gameStatus', 'in-progress');
    fixture.componentRef.setInput('historicalData', null);
    fixture.componentRef.setInput('capturedPieces', []);

    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('findMoves()', () => {
    it('should emit fenPositionEntered when given a valid FEN', () => {
      // Standard starting position FEN
      const validFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
      component.fen.set(validFen);

      vi.spyOn(component.fenPositionEntered, 'emit');

      component.findMoves();

      expect(component.error()).toBeNull();
      expect(component.fenPositionEntered.emit).toHaveBeenCalledWith(validFen);
    });

    it('should set an error and NOT emit when given an invalid FEN', () => {
      const invalidFen = 'this-is-not-a-valid-fen';
      component.fen.set(invalidFen);

      vi.spyOn(component.fenPositionEntered, 'emit');

      component.findMoves();

      expect(component.error()).toContain('Invalid position');
      expect(component.fenPositionEntered.emit).not.toHaveBeenCalled();
    });
  });

  describe('onFenInput()', () => {
    it('should update the fen signal and clear any existing errors', () => {
      // Setup an existing error
      component.error.set('Previous error message');

      // Mock an HTML input event
      const mockEvent = {
        target: { value: 'e2e4' }
      } as unknown as Event;

      component.onFenInput(mockEvent);

      expect(component.fen()).toBe('e2e4');
      expect(component.error()).toBeNull();
    });
  });

  describe('toggleShowAll()', () => {
    it('should toggle the showAll boolean signal', () => {
      expect(component.showAll()).toBeFalsy(); // Initial state

      component.toggleShowAll();
      expect(component.showAll()).toBeTruthy();

      component.toggleShowAll();
      expect(component.showAll()).toBeFalsy();
    });
  });

  describe('closeError()', () => {
    it('should set the error signal to null', () => {
      component.error.set('Test error');
      expect(component.error()).toBeTruthy();

      component.closeError();
      expect(component.error()).toBeNull();
    });
  });
});
