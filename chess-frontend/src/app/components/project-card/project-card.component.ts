import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import {Project} from '../../models/project.model';

@Component({
  selector: 'app-project-card',
  templateUrl: './project-card.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectCardComponent {
  project = input.required<Project>();
  viewDetails = output<Project>();

  getStatusColor(status: string): string {
    switch (status) {
      case 'Done': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'Ongoing': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'Freelance': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'Live': return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  }

  onViewDetails() {
    this.viewDetails.emit(this.project());
  }
}
