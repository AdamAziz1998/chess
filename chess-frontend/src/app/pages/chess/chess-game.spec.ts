import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChessGame } from './chess-game';

describe('ChessGame', () => {
  let component: ChessGame;
  let fixture: ComponentFixture<ChessGame>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChessGame]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChessGame);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render title', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const titleText = compiled.querySelector('h1')?.textContent;
    expect(titleText).toContain('Chess Practice and Explorer');
  });
});
