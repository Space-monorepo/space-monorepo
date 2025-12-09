// jest.config.js
// eslint-disable-next-line @typescript-eslint/no-require-imports
const nextJest = require('next/jest'); // Alterado aqui: removido os parênteses ()

/** @type {import('jest').Config} */
const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
});

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    // Ajuste para garantir que caminhos mais específicos sejam resolvidos corretamente
    '^@/app/api/(.*)$': '<rootDir>/src/app/api/$1',
    '^@/app/web/(.*)$': '<rootDir>/src/app/web/$1',
    '^@/app/(.*)$': '<rootDir>/src/app/$1', 
    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/lib/(.*)$': '<rootDir>/src/lib/$1',
  },
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig);
