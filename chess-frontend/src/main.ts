import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import * as Sentry from "@sentry/angular";

import { environment } from './environments/environment';

Sentry.init({
  dsn: environment.sentryDsn,
  
  // Quota Management
  tracesSampleRate: 0.05, 
  replaysSessionSampleRate: 0.0,
  replaysOnErrorSampleRate: 0.1,
  
  // Distributed Tracing
  tracePropagationTargets: ["localhost", /^https:\/\/api\.azizoneill\.com/],

  sendDefaultPii: true,
});

bootstrapApplication(App, appConfig)
  .catch((err) => console.error(err));
