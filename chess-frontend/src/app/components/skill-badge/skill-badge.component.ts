import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import {NgOptimizedImage} from '@angular/common';
import {Skill} from '../../models/project.model';

@Component({
  selector: 'app-skill-badge',
  templateUrl: './skill-badge.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    NgOptimizedImage
  ]
})
export class SkillBadgeComponent {
  skill = input.required<Skill>();
}
