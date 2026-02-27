import {Component, ChangeDetectionStrategy, input, output, ElementRef, inject} from '@angular/core';
import { Project } from '../../models/project.model';

@Component({
  selector: 'app-project-modal',
  templateUrl: './project-modal.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectModalComponent {
  project = input.required<Project>();
  closeModal = output<void>();
  private elementRef = inject(ElementRef);

  onClose() {
    this.closeModal.emit();
  }

  onBackdropClick(event: MouseEvent) {
    if (event.target === this.elementRef.nativeElement.querySelector('.modal-backdrop')) {
        this.onClose();
    }
  }
}
