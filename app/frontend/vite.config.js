import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite';


// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte(),tailwindcss()],
  server: {
    historyApiFallback: {
      rewrites: [
        { from: /.*/, to: '/index.html' }
      ]
    }
  },

  build: {
       rollupOptions: {
         onwarn: (warning, warn) => {
           // Skip certain warnings
           if (warning.code === 'UNRESOLVED_IMPORT') return;
           warn(warning);
         }
       }
     }
})
