export interface Project {
  id: string;
  title: string;
  tagline: string;
  status: 'Done' | 'Ongoing' | 'Freelance' | 'Live';
  summary: string;
  features: string[];
  tech: string[];
  repoUrl?: string;
  liveUrl?: string;
  liveUrlTitle?: string;
  liveUrl2?: string;
  liveUrl2Title?: string;
  caseStudy: {
    problem: string;
    role: string[];
    architecture?: string; // URL to an image
  };
}

export interface Skill {
  name: string;
  category: 'Frontend' | 'Backend' | 'Mobile' | 'DevOps & Tooling' | 'AI/ML';
  logoPath?: string;
}
