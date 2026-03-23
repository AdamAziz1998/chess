import { Injectable, signal } from '@angular/core';
import { Project, Skill } from '../models/project.model';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  projects = signal<Project[]>([
    {
      id: 'hsbc-fd',
      title: 'HSBC and FD Project',
      tagline: 'Home insurance platform for HSBC & First Direct',
      status: 'Live',
      summary:
        'Shared backend & frontend for HSBC and First Direct home insurance flows with dynamic styling per brand.',
      features: [
        'Get quotes, buy policies, renew, cancel',
        'Customer journeys with dynamic per-brand styling',
        'Secure quote engine & payment integration',
        'Analytics hooks for user behavior tracking',
      ],
      tech: ['Angular', 'Spring Boot', 'Docker', 'Postgres', 'MongoDB', 'Kafka', 'Keycloak'],
      liveUrl: 'https://homequote.insurance.hsbc.co.uk/HSBC/Home',
      liveUrlTitle: 'HSBC Site',
      liveUrl2: 'https://homequote.insurance.firstdirect.com/FD/Home',
      liveUrl2Title: 'FD Site',
      caseStudy: {
        problem: "HSBC & First Direct needed a unified, modern, and dynamically-branded home insurance platform to replace their legacy systems, improving user experience and internal efficiency.",
        role: [
          "User authentication",
          "Constructed the admin pages, both frontend and backend related task",
          "Built the dynamic multi-page form to generate a quote, including any endpoints required to get a quote.",
          "Maintained the project after deployment"
        ],
      },
    },
    {
      id: 'aviva',
      title: 'Aviva Project',
      tagline: 'Aviva business insurance web app',
      status: 'Live',
      summary:
        'Aviva Legal Indemnities Online (L.I.ON), is a secure B2B platform enabling solicitors and conveyancers to instantly quote and issue legal indemnity insurance for property and estate administration risks.',
      features: [
        'Multi-product quoting engine for various business insurance types',
        'Complex business logic rules engine for underwriting',
        'Admin tools for underwriting and policy management',
        'Comprehensive reporting and analytics dashboard',
      ],
      tech: ['Angular', 'Spring Boot', 'Docker', 'Postgres', 'MongoDB'],
      liveUrl: 'https://businessdirect.aviva.co.uk/LIon/site/home',
      caseStudy: {
        problem: "Aviva's existing B2B insurance portal was outdated, slow, and unable to handle complex multi-product quotes efficiently. They required a complete overhaul to streamline the process for brokers and underwriters.",
        role: [
          "Full-Stack Developer",
          "Developed key features for the quoting engine",
          "Built RESTful APIs",
          "Contributed to admin pages"
        ],
      },
    },
    {
      id: 'gym-app',
      title: 'Gym Training App',
      tagline: 'Gym Training Planner (mobile)',
      status: 'Ongoing',
      summary:
        'Developing an offline-first Android workout planner featuring SQLite data synchronization, admin user management, and push notifications. Currently managing the active codebase on GitHub in preparation for a full Google Play Store launch.',
      features: [
        'Create and customize workout plans',
        'Track progress and log sets/reps/weight',
        'Offline-first with local SQLite database',
        'Remote sync with a central server',
        'Push notifications for workout reminders',
      ],
      tech: ['React Native (Expo)', 'SQLite', 'Expo Router', 'Spring Boot', 'TypeScript'],
      repoUrl: 'https://github.com/AdamAziz1998/WorkoutApp',
      caseStudy: {
        problem: "Existing gym apps are often bloated, subscription-heavy, or lack robust offline capabilities. This project aims to build a lightweight, fast, and offline-first workout planner for serious trainees.",
        role: ["Solo Developer", "Mobile App Development (React Native)", "Backend API Design (Spring Boot)", "Database schema and synchronization logic"],
      },
    },
    {
      id: 'chess-engine',
      title: 'Chess engine & database',
      tagline: 'Chess engine + 1M game database',
      status: 'Live',
      summary:
        'A hybrid chess engine that consults three sub-engines — minimax, historical database, and a neural network — plus a searchable database of ~4 million GM games.',
      features: [
        'Playable engine (play as white or black)',
        'Move generated from three sub-engines',
        'Database queries by position, and moves played',
        'API endpoints for engine and database interaction',
      ],
      tech: ['FastAPI', 'Angular', 'PostgreSQL', 'PyTorch', 'Python', 'Tailwind CSS'],
      repoUrl: 'https://github.com/AdamAziz1998/chess',
      liveUrl: 'http://localhost:4200/chess',
      caseStudy: {
        problem: "Modern chess engines are dominated by expensive neural networks. This project explores a hybrid approach combining a traditional alpha-beta engine, a game database, and a lightweight neural network for consumer-hardware moves.",
        role: ["Solo Developer", "Engine development (Python/PyTorch)", "Database design and querying (PostgreSQL)", "API development (FastAPI)", "Frontend playable interface (Angular)"],
      },
    },
    {
      id: 'cruiz',
      title: 'Cruiz.sa',
      tagline: 'Landing & policy pages for startup',
      status: 'Freelance',
      summary:
        'Freelance landing page, policy & FAQ pages for cruise startup — design + implementation.',
      features: [
        'SEO-optimized landing page for high conversion',
        'Static pages for Privacy Policy, ToS, etc.',
        'Integration with a headless CMS for policy edits',
        'Fully responsive design',
      ],
      tech: ['Angular', 'Google Cloud Platform', 'Typescript'],
      liveUrl: 'https://www.cruiz.sa',
      repoUrl: 'https://github.com/AdamAziz1998/cruiz-sa',
      caseStudy: {
        problem: "The startup Cruiz.sa needed a professional, fast, and SEO-friendly web presence to attract initial customers and establish credibility. The content for legal pages needed to be easily updatable by non-technical staff.",
        role: ["Freelance Web Developer", "Design and implementation of all pages", "CMS integration", "Deployment and hosting setup on Vercel"],
      },
    }
  ]);

  skills = signal<Skill[]>([
    // Frontend
    { name: 'Angular', category: 'Frontend', logoPath: '/assets/img/portfolio/angular.svg'},
    { name: 'TypeScript', category: 'Frontend', logoPath: '/assets/img/portfolio/typescript.svg' },
    { name: 'React', category: 'Frontend', logoPath: '/assets/img/portfolio/react.svg' },
    { name: 'RxJS', category: 'Frontend', logoPath: '/assets/img/portfolio/rxjs.svg' },
    { name: 'Tailwind CSS', category: 'Frontend', logoPath: '/assets/img/portfolio/tailwindcss.svg' },

    // Backend
    { name: 'Spring Boot', category: 'Backend', logoPath: '/assets/img/portfolio/spring.svg' },
    { name: 'Node.js', category: 'Backend', logoPath: '/assets/img/portfolio/nodejs.svg' },
    { name: 'PostgreSQL', category: 'Backend', logoPath: '/assets/img/portfolio/postgresql.svg' },
    { name: 'Python', category: 'Backend', logoPath: '/assets/img/portfolio/python.svg' },
    { name: 'MongoDB', category: 'Backend', logoPath: '/assets/img/portfolio/mongodb.svg' },
    { name: 'FastAPI', category: 'Backend', logoPath: '/assets/img/portfolio/fastapi.svg' },
    { name: 'Java', category: 'Backend', logoPath: '/assets/img/portfolio/java.svg' },

    // Mobile
    { name: 'React Native', category: 'Mobile', logoPath: '/assets/img/portfolio/react.svg' },
    { name: 'Expo', category: 'Mobile', logoPath: '/assets/img/portfolio/expo.svg' },
    { name: 'SQLite', category: 'Mobile', logoPath: '/assets/img/portfolio/sqlite.svg' },

    // DevOps & Tooling
    { name: 'Docker', category: 'DevOps & Tooling', logoPath: '/assets/img/portfolio/docker.svg' },
    { name: 'AWS', category: 'DevOps & Tooling', logoPath: '/assets/img/portfolio/aws.svg' },
    { name: 'Google Cloud', category: 'DevOps & Tooling', logoPath: '/assets/img/portfolio/googlecloud.svg' },
    { name: 'GitHub Actions', category: 'DevOps & Tooling', logoPath: '/assets/img/portfolio/github.svg' },

    // AI/ML
    { name: 'PyTorch', category: 'AI/ML', logoPath: '/assets/img/portfolio/pytorch.svg' },
    { name: 'TensorFlow', category: 'AI/ML', logoPath: '/assets/img/portfolio/tensorflow.svg' },
    { name: 'Pandas', category: 'AI/ML', logoPath: '/assets/img/portfolio/pandas.svg' },
    { name: 'Numpy', category: 'AI/ML', logoPath: '/assets/img/portfolio/numpy.svg' },
    { name: 'Matplotlib', category: 'AI/ML', logoPath: '/assets/img/portfolio/matplotlib.svg' },
    { name: 'Keras', category: 'AI/ML', logoPath: '/assets/img/portfolio/keras.svg' },
  ]);
}
