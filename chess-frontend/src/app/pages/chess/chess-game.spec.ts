import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChessGame } from './chess-game';

describe('Chess', () => {
  let component: ChessGame;
  let fixture: ComponentFixture<ChessGame>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChessGame]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChessGame);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
