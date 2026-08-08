import readline from 'readline';
import { execSync } from 'child_process';
import http from 'http';

export interface StartupConfig {
  repoUrl: string;
  apiKey: string;
  branch: string;
  model: string;
  tier?: 'free' | 'algo';
  algoBalance?: number;
}

function promptText(query: string, defaultValue: string = '', isPassword: boolean = false): Promise<string> {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    if (isPassword && process.stdin.isTTY) {
      process.stdout.write(query);
      let password = '';
      
      const onData = (char: Buffer) => {
        const str = char.toString('utf-8');
        for (let i = 0; i < str.length; i++) {
          const c = str[i];
          if (c === '\n' || c === '\r' || c === '\u0004') {
            process.stdin.removeListener('data', onData);
            if (process.stdin.isRaw) process.stdin.setRawMode(false);
            rl.close();
            process.stdout.write('\n');
            resolve(password.trim() || defaultValue);
            return;
          } else if (c === '\u0008' || c === '\x7f') {
            if (password.length > 0) {
              password = password.slice(0, -1);
              process.stdout.write('\b \b');
            }
          } else if (c >= ' ' && c <= '~') {
            password += c;
            process.stdout.write('*');
          }
        }
      };

      if (process.stdin.isTTY) process.stdin.setRawMode(true);
      process.stdin.resume();
      process.stdin.on('data', onData);
    } else {
      const promptQuery = defaultValue ? `${query} (default: ${defaultValue}): ` : `${query}: `;
      rl.question(promptQuery, (answer) => {
        rl.close();
        resolve(answer.trim() || defaultValue);
      });
    }
  });
}

function fetchBackendPaymentStatus(): Promise<{ confirmed: boolean; status: string; algo_balance: number }> {
  return new Promise((resolve) => {
    const req = http.get('http://localhost:8000/api/v1/algorand/status', (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch {
          resolve({ confirmed: false, status: 'pending', algo_balance: 0.0 });
        }
      });
    });
    req.on('error', () => resolve({ confirmed: false, status: 'pending', algo_balance: 0.0 }));
    req.setTimeout(1500, () => {
      req.destroy();
      resolve({ confirmed: false, status: 'pending', algo_balance: 0.0 });
    });
  });
}

function resetBackendPaymentStatus(): Promise<void> {
  return new Promise((resolve) => {
    const req = http.request('http://localhost:8000/api/v1/algorand/reset', { method: 'POST' }, (res) => {
      res.on('data', () => {});
      res.on('end', () => resolve());
    });
    req.on('error', () => resolve());
    req.setTimeout(1500, () => {
      req.destroy();
      resolve();
    });
    req.end();
  });
}

export async function runInteractiveStartup(flags: Partial<StartupConfig>): Promise<StartupConfig> {
  console.log('\x1b[36m=========================================================\x1b[0m');
  console.log('\x1b[1m\x1b[34m Secure AI Code Review Sandbox — Multi-Model Session Setup\x1b[0m');
  console.log('\x1b[36m=========================================================\x1b[0m\n');

  // 1. FIRST: Access Tier Selection (Asked BEFORE Repo Link!)
  console.log('\x1b[33m? Select Access Tier:\x1b[0m');
  console.log('  1) FREE TIER — Bring Your Own API Key');
  console.log('  2) ALGORAND PAID TIER — Pay-As-You-Go via ALGO Blockchain');
  const tierChoice = await promptText('  Enter choice [1-2]', '1');
  const tier: 'free' | 'algo' = tierChoice === '2' ? 'algo' : 'free';
  let algoBalance = 0.0;

  if (tier === 'algo') {
    await resetBackendPaymentStatus();
    // Ensure status is reset before starting
    let initialCheck = await fetchBackendPaymentStatus();
    while (initialCheck.confirmed) {
      await resetBackendPaymentStatus();
      initialCheck = await fetchBackendPaymentStatus();
    }

    const payUrl = 'http://localhost:8000/api/v1/algorand/pay';
    console.log('\n\x1b[35m=========================================================\x1b[0m');
    console.log('\x1b[1m\x1b[35m ALGORAND DEVELOPER SETTLEMENT GATEWAY (Testnet v1.0)\x1b[0m');
    console.log('\x1b[35m=========================================================\x1b[0m');
    console.log(`\x1b[36m  Payment Portal URL : ${payUrl}\x1b[0m`);
    console.log('\x1b[36m  Gateway Receiver   : BILLUGANG27XALGORANDPAYMENTGATEWAYTESTNET999\x1b[0m');
    console.log('\x1b[31m  Current Balance    : 0.0 ALGO ($0.00 USD) [UNPAID]\x1b[0m\n');

    try {
      const openCmd = process.platform === 'win32' ? `start ${payUrl}` : process.platform === 'darwin' ? `open ${payUrl}` : `xdg-open ${payUrl}`;
      execSync(openCmd, { stdio: 'ignore' });
      console.log(`\x1b[32m[Browser] Launched Pera Wallet Payment Portal: ${payUrl}\x1b[0m`);
    } catch {
      console.log(`\x1b[33m[Browser Notice] Open ${payUrl} in your browser to authorize payment.\x1b[0m`);
    }

    console.log(`\x1b[33m[Pera Wallet] Auto-polling for transaction authorization...\x1b[0m`);

    // Automatic Real-Time Polling for Pera Wallet Transaction Signing (Max 60s)
    let isConfirmed = false;
    const maxPollMs = 60000;
    const pollStart = Date.now();


    while (Date.now() - pollStart < maxPollMs) {
      const current = await fetchBackendPaymentStatus();
      if (current.status === 'rejected') {
        break;
      }
      if (current.confirmed && current.algo_balance > 0) {
        isConfirmed = true;
        algoBalance = current.algo_balance;
        break;
      }
      await new Promise((r) => setTimeout(r, 1000));
    }

    if (!isConfirmed || algoBalance <= 0) {
      console.log(`\n\x1b[31m=========================================================\x1b[0m`);
      console.log(`\x1b[1m\x1b[31m PAYMENT FAILED — PERA WALLET TRANSACTION NOT CONFIRMED\x1b[0m`);
      console.log(`\x1b[31m=========================================================\x1b[0m`);
      console.log(`\x1b[31m Execution aborted. Please authorize payment to proceed.\x1b[0m\n`);
      process.exit(1);
    }

    const usdVal = (algoBalance * 0.2).toFixed(2);
    console.log(`\n\x1b[32m[CONFIRMED] Pera Wallet transaction signed & verified on Algorand Blockchain!\x1b[0m`);
    console.log(`\x1b[32m[Credits] Verified Session Balance: ${algoBalance} ALGO ($${usdVal} USD Equivalent)\x1b[0m\n`);
  }

  // 2. SECOND: Repository URL (Only reached if payment is confirmed OR free tier selected!)
  let repoUrl = flags.repoUrl || '';
  while (!repoUrl) {
    repoUrl = await promptText('\x1b[33m? Enter Git Repository URL\x1b[0m', '');
    if (!repoUrl) {
      console.log('\x1b[31m  Repository URL is required. Please enter a valid URL or path.\x1b[0m');
    }
  }

  // 3. Target Branch Name
  let branch = flags.branch || 'main';
  if (!flags.branch) {
    branch = await promptText('\x1b[33m? Enter Target Branch Name\x1b[0m', 'main');
    if (branch.startsWith('AIzaSy') || branch.startsWith('sk-') || branch.length > 25) {
      console.log('\x1b[33m  [Notice] Detected API key in branch field. Defaulting branch to "main".\x1b[0m');
      branch = 'main';
    }
  }

  // 4. AI Model Provider Choice (Featuring latest models)
  let model = flags.model || 'gemini-3.5-flash-lite';
  if (!flags.model) {
    console.log('\n\x1b[33m? Select AI Model Provider:\x1b[0m');
    console.log('  1) Google Gemini 3.5 Flash Lite (gemini-3.5-flash-lite) [Recommended]');
    console.log('  2) Google Gemini 3.5 Flash (gemini-3.5-flash)');
    console.log('  3) OpenAI ChatGPT (gpt-4o)');
    console.log('  4) Anthropic Claude 3.5 Sonnet (claude-3-5-sonnet)');
    console.log('  5) OpenAI ChatGPT Light (gpt-4o-mini)');
    console.log('  6) Anthropic Claude Haiku (claude-3-haiku)');
    const choice = await promptText('  Enter choice [1-6]', '1');
    if (choice === '2') model = 'gemini-3.5-flash';
    else if (choice === '3') model = 'gpt-4o';
    else if (choice === '4') model = 'claude-3-5-sonnet';
    else if (choice === '5') model = 'gpt-4o-mini';
    else if (choice === '6') model = 'claude-3-haiku';
    else model = 'gemini-3.5-flash-lite';
  }


  // 5. Provider-Specific API Key Prompt
  let apiKey = flags.apiKey || process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || '';
  if (tier === 'free') {
    let apiKeyPrompt = '? Enter Gemini API Key (masked)';
    let envKeyName = 'GEMINI_API_KEY';

    if (model.startsWith('gpt')) {
      apiKeyPrompt = '? Enter OpenAI / ChatGPT API Key (masked)';
      envKeyName = 'OPENAI_API_KEY';
    } else if (model.startsWith('claude')) {
      apiKeyPrompt = '? Enter Anthropic / Claude API Key (masked)';
      envKeyName = 'ANTHROPIC_API_KEY';
    }

    if (!apiKey) {
      apiKey = await promptText(`\x1b[33m${apiKeyPrompt}\x1b[0m`, '', true);
    }

    if (apiKey) {
      process.env[envKeyName] = apiKey;
      if (envKeyName === 'GEMINI_API_KEY') {
        process.env.GOOGLE_API_KEY = apiKey;
      }
    }
  } else {
    console.log('\x1b[32m[Algorand] Verified Pera Wallet credits applied to AI model runner.\x1b[0m');
  }

  console.log('\n\x1b[32m[OK] Multi-model setup complete. Initializing sandbox environment...\x1b[0m\n');
  return { repoUrl, apiKey, branch, model, tier, algoBalance };
}
