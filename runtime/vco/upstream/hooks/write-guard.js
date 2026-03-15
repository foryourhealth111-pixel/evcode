#!/usr/bin/env node
/**
 * Write Guard Hook (PreToolUse)
 * 
 * Blocks unnecessary .md/.txt file creation while allowing:
 * - Special files: README.md, CLAUDE.md, AGENTS.md, CONTRIBUTING.md
 * - System directories: ~/.claude/(skills|plans|commands)/
 * - Project working directories (any path outside home root)
 * 
 * Only blocks .md/.txt files created directly in the home directory root.
 */

let data = '';
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(data);
    const p = (input.tool_input && input.tool_input.file_path) || '';

    const isMdOrTxt = /\.(md|txt)$/i.test(p);

    if (isMdOrTxt) {
      // Always allow special filenames
      const isSpecialFile = /(README|CLAUDE|AGENTS|CONTRIBUTING|CHANGELOG)\.md$/i.test(p);
      if (isSpecialFile) { /* allow-console */ console.log(data); return; }

      // Always allow system directories
      const isSystemDir = /[\/]\.claude[\/](skills|plans|commands|hooks)[\/]/i.test(p);
      if (isSystemDir) { /* allow-console */ console.log(data); return; }

      // Allow project working directories (any path with depth > 2 from drive root)
      // e.g., D:\table\project\file.md = 4 segments = allowed
      // e.g., C:\Users\name\file.md = 4 segments but is home root = check further
      const segments = p.replace(/\/g, '/').split('/').filter(Boolean);
      const isHomeRoot = /[\/]Users[\/][^\/]+$/i.test(p.replace(/[\/][^\/]+$/, ''));
      
      if (isHomeRoot) {
        // File is directly in home directory root - block it
        console.error('[Hook] BLOCKED: Unnecessary documentation file in home directory');
        console.error('[Hook] File: ' + p);
        console.error('[Hook] Tip: Move to a project directory or use README.md');
        process.exit(2);
        return;
      }

      // All other paths (project directories, subdirectories) - allow
      /* allow-console */ console.log(data);
      return;
    }

    // Non-.md/.txt files - always allow
    /* allow-console */ console.log(data);
  } catch (e) {
    // Parse error - pass through
    /* allow-console */ console.log(data);
  }
});

