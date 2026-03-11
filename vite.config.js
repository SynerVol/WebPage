import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Listen on all network interfaces
    port: 5173,      // Ensure this matches the port you're using
    strictPort: true, // If 5173 is busy, fail instead of picking a random port
    allowedHosts: ['website.drone.eratosteme.fr'], // Explicitly allow your domain
    hmr: {
      clientPort: 443, // Helps with Hot Module Replacement over HTTPS
    },
  }
})
