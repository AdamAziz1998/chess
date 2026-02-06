import { defineConfig } from 'vitest/config';
import {playwright} from '@vitest/browser-playwright';
import angular from '@analogjs/vite-plugin-angular'; // Add this import

export default defineConfig({
  plugins: [angular()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['src/test-setup.ts'],
    browser: {
      enabled: true,
      provider: playwright({
        launchOptions: {
          args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
          ],
        },
      }),
      instances: [{ browser: 'chromium' }],
      headless: true,
      },
    }
});
