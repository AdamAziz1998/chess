import {AfterViewInit, Component, inject, Inject, PLATFORM_ID, signal} from '@angular/core';
import {DatePipe, isPlatformBrowser} from '@angular/common';
import {DataService} from '../../services/data.service';
import {Project, Skill} from '../../models/project.model';
import {HeaderComponent} from '../../components/header/header.component';
import {ProjectCardComponent} from '../../components/project-card/project-card.component';
import {ProjectModalComponent} from '../../components/project-modal/project-modal.component';
import {SkillBadgeComponent} from '../../components/skill-badge/skill-badge.component';

declare var particlesJS: any;

@Component({
  selector: 'app-home',
  imports: [
    DatePipe,
    HeaderComponent,
    ProjectCardComponent,
    ProjectModalComponent,
    SkillBadgeComponent
  ],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements AfterViewInit{
  constructor(@Inject(PLATFORM_ID) private platformId: Object) {}

  ngAfterViewInit(): void {
    if (isPlatformBrowser(this.platformId)) {

      setTimeout(() => {
        this.initParticles();
      }, 0);
    }
  }

  initParticles() {
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 150,
          "density": {
            "enable": true,
            "value_area": 1500
          }
        },
        "color": {
          "value": "#ffffff"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 3,
            "color": "#000000"
          },
          "polygon": {
            "nb_sides": 5
          },
          "image": {
            "src": "img/github.svg",
            "width": 100,
            "height": 100
          }
        },
        "opacity": {
          "value": 0.5,
          "random": false,
          "anim": {
            "enable": false,
            "speed": 1,
            "opacity_min": 0.1,
            "sync": false
          }
        },
        "size": {
          "value": 2,
          "random": true,
          "anim": {
            "enable": true,
            "speed": 1,
            "size_min": 1,
            "sync": false
          }
        },
        "line_linked": {
          "enable": true,
          "distance": 100,
          "color": "#ffffff",
          "opacity": 0.4,
          "width": 1
        },
        "move": {
          "enable": true,
          "speed": 0.2,
          "direction": "top",
          "random": true,
          "straight": true,
          "out_mode": "out",
          "bounce": false,
          "attract": {
            "enable": false,
            "rotateX": 1183.723797780518,
            "rotateY": 1657.213316892725
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": false,
            "mode": "grab"
          },
          "onclick": {
            "enable": true,
            "mode": "repulse"
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 85.26836695850781,
            "line_linked": {
              "opacity": 1
            }
          },
          "bubble": {
            "distance": 400,
            "size": 40,
            "duration": 2,
            "opacity": 8,
            "speed": 3
          },
          "repulse": {
            "distance": 79.92007992007991,
            "duration": 0.4
          },
          "push": {
            "particles_nb": 4
          },
          "remove": {
            "particles_nb": 2
          }
        }
      },
    });
  }

  private dataService = inject(DataService);

  projects = this.dataService.projects;
  skills = this.dataService.skills;

  frontendSkills = signal<Skill[]>(this.skills().filter(s => s.category === 'Frontend'));
  backendSkills = signal<Skill[]>(this.skills().filter(s => s.category === 'Backend'));
  mobileSkills = signal<Skill[]>(this.skills().filter(s => s.category === 'Mobile'));
  devopsSkills = signal<Skill[]>(this.skills().filter(s => s.category === 'DevOps & Tooling'));
  aiSkills = signal<Skill[]>(this.skills().filter(s => s.category === 'AI/ML'));

  selectedProject = signal<Project | null>(null);

  today = new Date();

  openProjectModal(project: Project) {
    this.selectedProject.set(project);
    document.body.style.overflow = 'hidden';
  }

  closeProjectModal() {
    this.selectedProject.set(null);
    document.body.style.overflow = 'auto';
  }
}
