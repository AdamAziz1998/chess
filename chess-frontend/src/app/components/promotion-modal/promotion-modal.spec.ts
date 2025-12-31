import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PromotionModal } from './promotion-modal';

describe('PromotionModal', () => {
  let component: PromotionModal;
  let fixture: ComponentFixture<PromotionModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PromotionModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PromotionModal);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
