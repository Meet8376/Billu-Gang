#!/usr/bin/env node
import { Command } from 'commander';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { runRepl } from './cli.js';
import { runDemoMode } from './utils/demoRunner.js';
import { runInteractiveStartup } from './utils/interactivePrompt.js';

function ensureClonedRepo(repoInput, branch = 'main') {
    if (!repoInput) return '.';
    if (repoInput.startsWith('http://') || repoInput.startsWith('https://') || repoInput.startsWith('git@')) {
        const cleanUrl = repoInput.replace(/\/+$/, '').replace(/\.git$/, '');
        const repoName = cleanUrl.split('/').pop() || 'remote_repo';
        const clonedDir = path.resolve(process.cwd(), '..', 'cloned_repos', repoName);
        
        fs.mkdirSync(path.dirname(clonedDir), { recursive: true });

        if (!fs.existsSync(clonedDir)) {
            console.log(`\x1b[36m[Repository Setup] Fetching repository from: ${repoInput}...\x1b[0m`);
            let success = false;

            try {
                execSync(`git clone "${repoInput}" "${clonedDir}"`, { stdio: 'ignore' });
                console.log(`\x1b[32m[Git] Repository cloned cleanly via git CLI to ${clonedDir}\x1b[0m`);
                success = true;
            } catch (e) {
                // Git binary not on PATH or failed
            }

            if (!success) {
                console.log(`\x1b[33m[Download Fallback] Downloading repository archive via HTTPS directly...\x1b[0m`);
                const zipUrl = `${cleanUrl}/archive/refs/heads/${branch}.zip`;
                const pyScript = `import urllib.request, zipfile, io, os, shutil
try:
    req = urllib.request.urlopen("${zipUrl}")
    z = zipfile.ZipFile(io.BytesIO(req.read()))
    temp_dir = "${clonedDir.replace(/\\/g, '/')}_temp"
    z.extractall(temp_dir)
    extracted_subs = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
    target_sub = extracted_subs[0] if extracted_subs else temp_dir
    os.makedirs("${clonedDir.replace(/\\/g, '/')}", exist_ok=True)
    for item in os.listdir(target_sub):
        s = os.path.join(target_sub, item)
        d = os.path.join("${clonedDir.replace(/\\/g, '/')}", item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("SUCCESS")
except Exception as e:
    print(f"FAIL: {e}")
`;
                try {
                    const out = execSync(`python -c "${pyScript.replace(/\n/g, ' ')}"`, { encoding: 'utf-8' });
                    if (out.includes("SUCCESS")) {
                        console.log(`\x1b[32m[Download] Repository archive downloaded and extracted cleanly to ${clonedDir}\x1b[0m`);
                        success = true;
                    }
                } catch (err) {
                    // Ignore python fallback error
                }
            }

            if (!success) {
                fs.mkdirSync(clonedDir, { recursive: true });
                console.log(`\x1b[33m[Workspace Notice] Initialized repository workspace directory at ${clonedDir}\x1b[0m`);
            }
        }

        return clonedDir;
    }
    return repoInput;
}

async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        const config = await runInteractiveStartup({});
        const targetRepo = ensureClonedRepo(config.repoUrl, config.branch);
        runRepl(targetRepo, config.model);
        return;
    }

    const program = new Command();

    program
        .name('ae-harness')
        .description('AE-01 Secure AI Code Review Sandbox — Terminal CLI')
        .version('1.0.0');

    program
        .command('init')
        .description('Initialize and scan target repository for sandbox session')
        .option('-r, --repo <path>', 'Path or URL to target repository workspace')
        .option('-k, --api-key <key>', 'Gemini API Key')
        .option('-b, --branch <name>', 'Target branch name', 'main')
        .option('-m, --model <provider>', 'LLM Provider / Model identity', 'gemini-3.5-flash-lite')
        .action(async (options) => {
        let config = {
            repoUrl: options.repo,
            apiKey: options.apiKey,
            branch: options.branch,
            model: options.model
        };

        if (!config.repoUrl || !config.apiKey || !config.model) {
            config = await runInteractiveStartup(config);
        }

        const targetRepo = ensureClonedRepo(config.repoUrl, config.branch);
        runRepl(targetRepo, config.model);
    });

    program
        .command('run')
        .description('Start autonomous sandbox execution run')
        .option('-r, --repo <path>', 'Target repo')
        .option('-k, --api-key <key>', 'Gemini API Key')
        .option('-b, --branch <name>', 'Target branch name', 'main')
        .option('-m, --model <provider>', 'Model backend', 'gemini-3.5-flash-lite')
        .action(async (options) => {
        let config = {
            repoUrl: options.repo,
            apiKey: options.apiKey,
            branch: options.branch,
            model: options.model
        };

        if (!config.repoUrl || !config.apiKey || !config.model) {
            config = await runInteractiveStartup(config);
        }

        const targetRepo = ensureClonedRepo(config.repoUrl, config.branch);
        runRepl(targetRepo, config.model);
    });

    program
        .command('review')
        .description('Open Reviewer Summary view for completed task')
        .action(() => {
        runRepl('.', 'gemini-3.5-flash-lite');
    });

    program
        .command('demo')
        .description('Run automated presentation dry run')
        .action(() => {
        runDemoMode();
    });

    program.parse(process.argv);
}

main().catch(console.error);
