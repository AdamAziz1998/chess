import { Component, input, output } from '@angular/core';
import { NgOptimizedImage } from '@angular/common';
@Component({
  selector: 'app-promotion-modal',
    imports: [
        NgOptimizedImage
    ],
  templateUrl: './promotion-modal.html',
})
export class PromotionModal {
  color = input.required<string>();
  onPromote = output<string>();
  onCancel = output<void>();

  select(type: string) {
    this.onPromote.emit(type);
  }
}
