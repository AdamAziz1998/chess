import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Sidebar } from './sidebar';

describe('Sidebar', () => {
  let component: Sidebar;
  let fixture: ComponentFixture<Sidebar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Sidebar]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Sidebar);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('gameMode', 'practice');
    fixture.componentRef.setInput('playMode', 'white');
    fixture.componentRef.setInput('gameStatus', 'in-progress');
    fixture.componentRef.setInput('historicalMoves', []);
    fixture.componentRef.setInput('capturedPieces', []);
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
