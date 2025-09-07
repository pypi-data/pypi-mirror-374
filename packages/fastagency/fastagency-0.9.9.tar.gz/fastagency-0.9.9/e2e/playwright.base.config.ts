// this file contains common playwright settings


import { devices, defineConfig as originalDefineConfig, PlaywrightTestConfig } from '@playwright/test';



/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
// import dotenv from 'dotenv';
// import path from 'path';
// dotenv.config({ path: path.resolve(__dirname, '.env') });

/**
 * See https://playwright.dev/docs/test-configuration.
 */

//const testEnv = { ...process.env, COVERAGE_PROCESS_START: 'playwright.coverage.cfg' } as { [key: string]: string }


const baseConfig: PlaywrightTestConfig = {
    testDir: './e2e',
    /* Run tests in files in parallel */
    fullyParallel: false,
    /* Fail the build on CI if you accidentally left test.only in the source code. */
    forbidOnly: !!process.env.CI,
    /* Retry on CI only */
    retries: process.env.CI ? 2 : 0,
    /* Opt out of parallel tests on CI. */
    workers: process.env.CI ? 1 : 1,
    /* Reporter to use. See https://playwright.dev/docs/test-reporters */
    reporter: 'html',
    /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
    use: {
        /* Base URL to use in actions like `await page.goto('/')`. */
        baseURL: 'http://127.0.0.1:32123',

        /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
        trace: 'on-first-retry',
    },

    /* Configure projects for major browsers */
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },

        {
            name: 'firefox',
            use: { ...devices['Desktop Firefox'] },
        },

        {
            name: 'webkit',
            use: { ...devices['Desktop Safari'] },
        },

        /* Test against mobile viewports. */
        // {
        //   name: 'Mobile Chrome',
        //   use: { ...devices['Pixel 5'] },
        // },
        // {
        //   name: 'Mobile Safari',
        //   use: { ...devices['iPhone 12'] },
        // },

        /* Test against branded browsers. */
        // {
        //   name: 'Microsoft Edge',
        //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
        // },
        // {
        //   name: 'Google Chrome',
        //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
        // },
    ],

    // /* Run your local dev server before starting the tests */
    // webServer: {
    //     command: 'fastagency run e2e/llm-sans/main.py',
    //     url: 'http://127.0.0.1:32123',
    //     //        env: testEnv,
    //     reuseExistingServer: true,
    //     //reuseExistingServer: !process.env.CI,
    //     //reuseExistingServer: false,
    // },
}

export function defineConfig(config: PlaywrightTestConfig): PlaywrightTestConfig {
    const extendedConfig = { ...baseConfig }
    for (const key in config) {
        if (config.hasOwnProperty(key)) {
            extendedConfig[key] = config[key];
        }
    }
    return originalDefineConfig(extendedConfig)
}
