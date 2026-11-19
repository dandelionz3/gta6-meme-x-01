import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

try {
  const bytes = readFileSync(join(botDir, 'POST.json'));
  const post = JSON.parse(bytes.toString('utf8'));
  if (post === null || typeof post.url !== 'string' || !post.url.startsWith('http')) {
    throw new Error('POST.json must contain a string url field starting with http');
  }
  mkdirSync(outputDir, { recursive: true });
  writeFileSync(join(outputDir, 'POST.json'), bytes);
} catch (error) {
  console.error(`Cannot export POST.json: ${error.message}`);
  process.exitCode = 1;
}
