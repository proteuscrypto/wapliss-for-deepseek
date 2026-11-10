# Changelog

All notable changes to the Wapliss WhatsApp bundle for DeepSeek Harness.
Created and maintained by netdigitaltech.

## 1.0.1 (2026-11-10)

- Documentation: README rewritten with compatibility table, quick start,
  example prompts, FAQ, troubleshooting and links to the other Wapliss plugins.
- Metadata: author netdigitaltech, homepage `wapliss.com/integrations#deepseek`,
  more search keywords. No change to the bundle row or the tools.


## 1.0.0 (2026-11-10)

- First release: configuration-only DeepSeek Harness bundle for the Wapliss MCP
  server (`https://wapliss.com/mcp/v1`), 16 tools as `mcp__wapliss__*`.
- Authentication with a personal Wapliss API key (`WAPLISS_API_KEY`); the row
  stays disabled without it.
- Locales: en, es, pt, zh, fr, de, ja, ru. Icon 512x512 PNG.
- Skill `wapliss-whatsapp` (dsh skill-filesystem format).
- `scripts/validate.py` with static and `--live` checks.
- Tested with `@deepseek-ai/dsh` 0.2.2-rc.1 (headless and web profiles).
