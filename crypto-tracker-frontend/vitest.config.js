/**
 * VITEST CONFIGURATION
 * Configures the Vitest testing framework for React components.
 * Sets up test environment, mocks, and coverage reporting.
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    // TEST ENVIRONMENT
    environment: 'jsdom', // Simulates browser environment for React components
    
    // SETUP FILES
    setupFiles: ['./src/test-setup.js'], // Runs before each test file
    
    // GLOBALS
    globals: true, // Allows using describe, it, expect without importing
    
    // COVERAGE CONFIGURATION
    coverage: {
      provider: 'v8', // Fast coverage provider
      reporter: ['text', 'json', 'html'], // Multiple report formats
      exclude: [
        'node_modules/',
        'src/test-setup.js',
        '**/*.config.js',
        '**/*.config.ts',
        'dist/',
        'build/'
      ],
      threshold: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        }
      }
    },
    
    // MOCK CONFIGURATION
    deps: {
      inline: ['@testing-library/jest-dom'] // Handle ESM modules
    },
    
    // TEST PATTERNS
    include: [
      'src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'
    ],
    exclude: [
      'node_modules',
      'dist',
      '.idea',
      '.git',
      '.cache'
    ],
    
    // TIMEOUTS
    testTimeout: 10000, // 10 seconds for slow async tests
    hookTimeout: 10000,
    
    // REPORTING
    reporter: ['verbose', 'junit', 'json'],
    outputFile: {
      junit: './test-results/junit.xml',
      json: './test-results/results.json'
    }
  },
  
  // BUILD CONFIGURATION FOR TESTS
  define: {
    'import.meta.vitest': false
  },
  
  // RESOLVE CONFIGURATION
  resolve: {
    alias: {
      '@': './src'
    }
  }
})