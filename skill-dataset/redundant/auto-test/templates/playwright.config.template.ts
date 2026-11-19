import { defineConfig, devices } from '@playwright/test';

/**
 * auto-test skill 默认 Playwright 配置模板。
 *
 * 使用方式：
 * 1. 复制本文件到项目根目录的 playwright.config.ts。
 * 2. 把下方占位字段替换为项目实际值（用 <<<>>> 标记）。
 * 3. 如项目已有 playwright.config.ts，禁止覆盖；改为人工合并。
 */
export default defineConfig({
  testDir: '.auto-test/case/specs',
  outputDir: '.auto-test/runs/last/output',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : 1,
  reporter: [
    ['list'],
    ['html', { outputFolder: '.auto-test/runs/last/html', open: 'never' }],
    ['json', { outputFile: '.auto-test/runs/last/report.json' }],
  ],
  use: {
    // <<< 替换为项目 baseUrl，与 .auto-test/config.json 的 baseUrl 保持一致 >>>
    baseURL: 'http://localhost:3000',
    storageState: '.auto-test/.auth/storageState.json',
    trace: 'on-first-retry',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 20_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
