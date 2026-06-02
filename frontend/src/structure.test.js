import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

describe('Frontend Structure Health Test', () => {
  const requiredDirs = [
    'features/dashboard',
    'features/agents',
    'features/ops-monitor',
    'features/crypto',
    'features/memory',
    'features/settings',
    'shared/components',
    'shared/hooks',
    'shared/lib',
    'shared/layouts',
  ];

  it('should have all required domain directories', () => {
    requiredDirs.forEach((dir) => {
      const fullPath = path.resolve(__dirname, dir);
      expect(fs.existsSync(fullPath)).toBe(true);
      expect(fs.lstatSync(fullPath).isDirectory()).toBe(true);
    });
  });

  it('should have .gitkeep files in all new directories', () => {
    requiredDirs.forEach((dir) => {
      const gitkeepPath = path.resolve(__dirname, dir, '.gitkeep');
      expect(fs.existsSync(gitkeepPath)).toBe(true);
    });
  });
});
