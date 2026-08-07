#!/usr/bin/env node
import { Command } from 'commander';
import { runRepl } from './cli.js';
import { runDemoMode } from './utils/demoRunner.js';

const program = new Command();

program
  .name('ae-harness')
  .description('AE-01 Unified Agentic Coding Harness — Terminal CLI')
  .version('1.0.0');

program
  .command('init')
  .description('Initialize and scan target repository for agentic harness session')
  .option('-r, --repo <path>', 'Path to target repository workspace', '.')
  .option('-m, --model <provider>', 'LLM Provider / Model identity', 'gemini-3.5-flash-lite')
  .action((options) => {
    runRepl(options.repo, options.model);
  });

program
  .command('run')
  .description('Start autonomous coding run on specified issue')
  .option('-r, --repo <path>', 'Target repo', '.')
  .option('-m, --model <provider>', 'Model backend', 'gemini-3.5-flash-lite')
  .action((options) => {
    runRepl(options.repo, options.model);
  });

program
  .command('review')
  .description('Open Reviewer Summary view for completed task')
  .action(() => {
    runRepl('.', 'gemini-3.5-flash-lite');
  });

program
  .command('demo')
  .description('Run automated presentation dry run of Minimum Viable Demonstration (MVD FR37-FR42)')
  .action(() => {
    runDemoMode();
  });

program.parse(process.argv);

if (!process.argv.slice(2).length) {
  runRepl('.', 'gemini-3.5-flash-lite');
}
