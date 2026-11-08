import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://itvm.ru',
  base: '/ever-youth',
  output: 'static',
  build: { format: 'file' },
  trailingSlash: 'never',
  compressHTML: false,
  integrations: [react()],
  outDir: process.env.CLINIC_COMPONENT_LAB ? './dist-lab' : './dist',
  devToolbar: { enabled: false },
});
