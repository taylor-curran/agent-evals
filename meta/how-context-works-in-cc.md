# How Context Works in Claude Code

## File Access Capabilities
- Direct file system access through tools (Read, Write, Edit, Glob, Grep)
- No vector database or indexing - works directly with files
- No persistent memory between conversations

## File Size Limitations
- **30,000 character limit** for file reads and shell output
- Files exceeding this limit are truncated
- Use `offset` and `limit` parameters for reading large files in sections:
  - `Read file.py offset=1 limit=500` (lines 1-500)
  - `Read file.py offset=501 limit=500` (lines 501-1000)

## Search Strategy and Tools

### Available Tools
1. **Glob** - Find files by pattern (e.g., `**/*.py`, `src/**/*.ts`)
2. **Grep** - Search file contents with regex patterns
3. **Task** - Launch agents for complex multi-step searches
4. **LS** - List directory contents
5. **Read** - Read specific files or sections

### Search Heuristics
- **Simple tasks** (e.g., "find login function"): 3-10 files
- **Complex tasks** (e.g., "understand auth flow"): 20-50+ files
- Stop when:
  - Found the specific code/answer requested
  - Checked all files matching relevant patterns
  - Followed all import chains and dependencies
  - No new relevant files discovered

### Best Practices
1. Start broad with Grep/Glob to identify relevant files
2. Read specific files for detailed context
3. Follow import chains to understand dependencies
4. Check package files (package.json, requirements.txt) before assuming libraries exist

## Code Generation Grounding
- Read existing files to understand conventions and patterns
- Check imports and dependencies before using libraries
- Analyze surrounding code context before making changes
- Verify changes with linting/typechecking when available

## Chunking and Large Files
- No automatic chunking - sees up to 2000 lines at once by default
- 400-line file would be read in one operation
- Very large files require manual chunking with offset/limit
- Default read starts from beginning without parameters

## Effective Usage Tips
1. Be specific about what you're looking for
2. Provide file paths when you know them
3. For large codebases, guide the search with relevant keywords
4. Understand that each conversation starts fresh - no prior context retained