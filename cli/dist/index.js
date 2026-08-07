#!/usr/bin/env node
import { Command } from 'commander';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { runRepl } from './cli.js';
import { runDemoMode } from './utils/demoRunner.js';
import { runInteractiveStartup } from './utils/interactivePrompt.js';
function normalizeRepoUrl(input) {
    if (!input)
        return '';
    const trimmed = input.trim();
    if (trimmed.startsWith('http://') || trimmed.startsWith('https://') || trimmed.startsWith('git@')) {
        return trimmed;
    }
    if (trimmed.includes('/') && !trimmed.includes('\\') && !fs.existsSync(trimmed)) {
        if (trimmed.startsWith('github.com/')) {
            return `https://${trimmed}.git`;
        }
        return `https://github.com/${trimmed}.git`;
    }
    return trimmed;
}
function ensureDirectoryHasFiles(dirPath) {
    const absPath = path.resolve(dirPath);
    if (!fs.existsSync(absPath)) {
        fs.mkdirSync(absPath, { recursive: true });
    }
    const files = fs.readdirSync(absPath);
    if (files.length === 0) {
        // Create base workspace files if directory is empty
        fs.writeFileSync(path.join(absPath, 'main.py'), `# AE-01 Autonomous Workspace\ndef review_target():\n    print("Reviewing workspace target")\n\nif __name__ == "__main__":\n    review_target()\n`);
        fs.writeFileSync(path.join(absPath, 'pytest.ini'), `[pytest]\ntestpaths = .\npython_files = test_*.py *_test.py\n`);
        fs.writeFileSync(path.join(absPath, 'test_sample.py'), `def test_environment():\n    assert True\n`);
        fs.writeFileSync(path.join(absPath, 'README.md'), `# Target Repository Workspace\n\nAutonomous sandbox environment for code review and verification.\n`);
    }
}
function ensureClonedRepo(repoInput, branch = 'main') {
    if (!repoInput) {
        ensureDirectoryHasFiles('.');
        return '.';
    }
    const repoUrl = normalizeRepoUrl(repoInput);
    if (repoUrl.startsWith('http://') || repoUrl.startsWith('https://') || repoUrl.startsWith('git@')) {
        const cleanUrl = repoUrl.replace(/\/+$/, '').replace(/\.git$/, '');
        const repoName = cleanUrl.split('/').pop() || 'remote_repo';
        let clonedDir = path.resolve(process.cwd(), '..', 'cloned_repos', repoName);
        // Clean up destination directory so git clone can create a fresh clone
        if (fs.existsSync(clonedDir)) {
            try {
                fs.rmSync(clonedDir, { recursive: true, force: true });
            }
            catch (e) {
                const timeTag = Date.now().toString().slice(-6);
                clonedDir = path.resolve(process.cwd(), '..', 'cloned_repos', `${repoName}_${timeTag}`);
            }
        }
        console.log(`\x1b[36m[Repository Setup] Fetching repository from: ${repoUrl}...\x1b[0m`);
        let success = false;
        // 1. Try system git command first (destination path must not exist prior to clone)
        try {
            try {
                if (branch && branch !== 'main') {
                    execSync(`git clone -b "${branch}" "${repoUrl}" "${clonedDir}"`, { stdio: 'inherit' });
                }
                else {
                    execSync(`git clone "${repoUrl}" "${clonedDir}"`, { stdio: 'inherit' });
                }
            }
            catch (bErr) {
                // Fallback to cloning default branch
                execSync(`git clone "${repoUrl}" "${clonedDir}"`, { stdio: 'inherit' });
            }
            if (fs.existsSync(clonedDir)) {
                const contents = fs.readdirSync(clonedDir);
                if (contents.length > 0) {
                    console.log(`\x1b[32m[Git] Repository cloned cleanly via git CLI to ${clonedDir} (${contents.length} top-level items)\x1b[0m`);
                    success = true;
                }
            }
        }
        catch (e) {
            console.log(`\x1b[33m[Git Notice] Git CLI clone notice, attempting direct HTTP archive extraction...\x1b[0m`);
        }
        // 2. Fallback: Download & extract GitHub zip archive via HTTPS
        if (!success) {
            console.log(`\x1b[33m[Download Fallback] Downloading repository archive via HTTPS directly...\x1b[0m`);
            const zipUrls = [
                `${cleanUrl}/archive/refs/heads/${branch}.zip`,
                `${cleanUrl}/archive/refs/heads/main.zip`,
                `${cleanUrl}/archive/refs/heads/master.zip`,
                `${cleanUrl}/zipball/HEAD`
            ];
            for (const zipUrl of zipUrls) {
                const normDir = clonedDir.replace(/\\/g, '/');
                const pyScript = `import urllib.request, zipfile, io, os, shutil
try:
    req = urllib.request.Request("${zipUrl}", headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        z = zipfile.ZipFile(io.BytesIO(resp.read()))
        temp_dir = "${normDir}_temp"
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir, ignore_errors=True)
        z.extractall(temp_dir)
        subs = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
        target_sub = subs[0] if subs else temp_dir
        if os.path.exists("${normDir}"): shutil.rmtree("${normDir}", ignore_errors=True)
        shutil.copytree(target_sub, "${normDir}", dirs_exist_ok=True)
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("SUCCESS")
except Exception as err:
    print(f"FAIL: {err}")
`;
                try {
                    const base64Py = Buffer.from(pyScript).toString('base64');
                    const out = execSync(`python -c "import base64; exec(base64.b64decode('${base64Py}').decode('utf-8'))"`, { encoding: 'utf-8' });
                    if (out.includes("SUCCESS") && fs.existsSync(clonedDir)) {
                        const contents = fs.readdirSync(clonedDir);
                        console.log(`\x1b[32m[Download] Repository archive downloaded and extracted cleanly to ${clonedDir} (${contents.length} top-level items)\x1b[0m`);
                        success = true;
                        break;
                    }
                }
                catch (err) {
                    continue;
                }
            }
        }
        if (!success) {
            ensureDirectoryHasFiles(clonedDir);
        }
        return clonedDir;
    }
    ensureDirectoryHasFiles(repoInput);
    return repoInput;
}
function startDockerContainerForWorkspace(targetWorkspace) {
    const containerName = 'ae01-sandbox-active';
    const absHostPath = path.resolve(targetWorkspace);
    ensureDirectoryHasFiles(absHostPath);
    console.log(`\x1b[36m[Docker Engine] Mounting workspace to container: ${absHostPath}...\x1b[0m`);
    // 1. Remove stale container if existing
    try {
        execSync(`docker rm -f ${containerName}`, { stdio: 'ignore' });
    }
    catch { }
    const initCmd = 'sh -c "echo ================================================== && echo AE-01 Secure Code Review Sandbox Container Active && echo Mounted Workspace Path: /workspace && echo ================================================== && tail -f /dev/null"';
    // 2. Check if ae01-sandbox:latest exists locally on Docker daemon
    let hasCustomImage = false;
    try {
        execSync(`docker image inspect ae01-sandbox:latest`, { stdio: 'ignore' });
        hasCustomImage = true;
    }
    catch { }
    const targetImage = hasCustomImage ? 'ae01-sandbox:latest' : 'python:3.11-slim';
    // 3. Run container with mounted workspace volume
    try {
        const out = execSync(`docker run -d --name ${containerName} -v "${absHostPath}:/workspace" ${targetImage} ${initCmd}`, { encoding: 'utf-8' });
        const cid = out.trim();
        if (cid) {
            console.log(`\x1b[32m[Docker Engine] Live sandbox container created and running in Docker Desktop (ID: ${cid.slice(0, 12)}, Image: ${targetImage})\x1b[0m`);
            return cid;
        }
    }
    catch (err1) {
        try {
            const out = execSync(`docker run -d --name ${containerName} python:3.11-slim ${initCmd}`, { encoding: 'utf-8' });
            const cid = out.trim();
            if (cid) {
                console.log(`\x1b[32m[Docker Engine] Live sandbox container created and running in Docker Desktop (ID: ${cid.slice(0, 12)})\x1b[0m`);
                return cid;
            }
        }
        catch (err2) {
            console.log(`\x1b[33m[Docker Engine Notice] ${err2.message || err2}\x1b[0m`);
        }
    }
    return '';
}
async function main() {
    const args = process.argv.slice(2);
    if (args.length === 0) {
        const config = await runInteractiveStartup({});
        if (config.apiKey) {
            process.env.GEMINI_API_KEY = config.apiKey;
            process.env.GOOGLE_API_KEY = config.apiKey;
        }
        const targetRepo = ensureClonedRepo(config.repoUrl, config.branch);
        startDockerContainerForWorkspace(targetRepo);
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
        .option('-m, --model <provider>', 'LLM Provider / Model identity', 'gemini-2.5-flash')
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
        startDockerContainerForWorkspace(targetRepo);
        runRepl(targetRepo, config.model);
    });
    program
        .command('run')
        .description('Start autonomous sandbox execution run')
        .option('-r, --repo <path>', 'Target repo')
        .option('-k, --api-key <key>', 'Gemini API Key')
        .option('-b, --branch <name>', 'Target branch name', 'main')
        .option('-m, --model <provider>', 'Model backend', 'gemini-2.5-flash')
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
        startDockerContainerForWorkspace(targetRepo);
        runRepl(targetRepo, config.model);
    });
    program
        .command('review')
        .description('Open CLI TUI for code review and verification')
        .action(() => {
        runRepl('.', 'gemini-2.5-flash');
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
