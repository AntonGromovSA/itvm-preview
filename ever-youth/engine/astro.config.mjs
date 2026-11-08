import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://itvm.ru',
  base: '/ever-youth',
  output: 'static',
  publicDir: './public',
  build: { format: 'file', inlineStylesheets: 'never' },
  trailingSlash: 'never',
  compressHTML: true,
  integrations: [react()],
  outDir: process.env.CLINIC_COMPONENT_LAB ? './dist-lab' : './dist',
  devToolbar: { enabled: false },
});
