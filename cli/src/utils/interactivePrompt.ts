import readline from 'readline';

export interface StartupConfig {
  repoUrl: string;
  apiKey: string;
  branch: string;
  model: string;
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

export async function runInteractiveStartup(flags: Partial<StartupConfig>): Promise<StartupConfig> {
  console.log('\x1b[36m=========================================================\x1b[0m');
  console.log('\x1b[1m\x1b[34m Secure AI Code Review Sandbox — Multi-Model Session Setup\x1b[0m');
  console.log('\x1b[36m=========================================================\x1b[0m\n');

  // 1. Repository URL
  let repoUrl = flags.repoUrl || '';
  while (!repoUrl) {
    repoUrl = await promptText('\x1b[33m? Enter Git Repository URL\x1b[0m', '');
    if (!repoUrl) {
      console.log('\x1b[31m  Repository URL is required. Please enter a valid URL or path.\x1b[0m');
    }
  }

  // 2. Target Branch Name
  let branch = flags.branch || 'main';
  if (!flags.branch) {
    branch = await promptText('\x1b[33m? Enter Target Branch Name\x1b[0m', 'main');
    if (branch.startsWith('AIzaSy') || branch.startsWith('sk-') || branch.length > 25) {
      console.log('\x1b[33m  [Notice] Detected API key in branch field. Defaulting branch to "main".\x1b[0m');
      branch = 'main';
    }
  }

  // 3. AI Model Provider Choice (All models included, Gemini is gemini-3.5-flash-lite)
  let model = flags.model || 'gemini-3.5-flash-lite';
  if (!flags.model) {
    console.log('\n\x1b[33m? Select AI Model Provider:\x1b[0m');
    console.log('  1) Google Gemini 3.5 Flash-Lite (gemini-3.5-flash-lite) [Recommended]');
    console.log('  2) OpenAI ChatGPT (gpt-4o)');
    console.log('  3) Anthropic Claude 3.5 Sonnet (claude-3-5-sonnet)');
    console.log('  4) Google Gemini Pro (gemini-1.5-pro)');
    console.log('  5) OpenAI ChatGPT Light (gpt-4o-mini)');
    console.log('  6) Anthropic Claude Haiku (claude-3-haiku)');
    const choice = await promptText('  Enter choice [1-6]', '1');
    if (choice === '2') model = 'gpt-4o';
    else if (choice === '3') model = 'claude-3-5-sonnet';
    else if (choice === '4') model = 'gemini-1.5-pro';
    else if (choice === '5') model = 'gpt-4o-mini';
    else if (choice === '6') model = 'claude-3-haiku';
    else model = 'gemini-3.5-flash-lite';
  }

  // 4. Provider-Specific API Key Prompt (Masked)
  let apiKeyPrompt = '? Enter Gemini API Key (masked)';
  let envKeyName = 'GEMINI_API_KEY';

  if (model.startsWith('gpt')) {
    apiKeyPrompt = '? Enter OpenAI / ChatGPT API Key (masked)';
    envKeyName = 'OPENAI_API_KEY';
  } else if (model.startsWith('claude')) {
    apiKeyPrompt = '? Enter Anthropic / Claude API Key (masked)';
    envKeyName = 'ANTHROPIC_API_KEY';
  }

  let apiKey = flags.apiKey || process.env[envKeyName] || process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY || '';
  if (!apiKey) {
    apiKey = await promptText(`\x1b[33m${apiKeyPrompt}\x1b[0m`, '', true);
  }

  if (apiKey) {
    process.env[envKeyName] = apiKey;
    if (envKeyName === 'GEMINI_API_KEY') {
      process.env.GOOGLE_API_KEY = apiKey;
    }
  }

  console.log('\n\x1b[32m[OK] Multi-model setup complete. Initializing sandbox environment...\x1b[0m\n');
  return { repoUrl, apiKey, branch, model };
}

