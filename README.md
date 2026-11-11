<p align="center">
  <img src="icon.png" alt="Wapliss logo" width="120" />
</p>

<h1 align="center">Wapliss WhatsApp for DeepSeek</h1>

<p align="center">
  <strong>Connect your own WhatsApp to DeepSeek with the Wapliss MCP server.</strong><br />
  Read and summarize chats and groups, and send messages, files, locations and polls, always with your confirmation.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-25D366" alt="License: MIT" />
  <img src="https://img.shields.io/badge/MCP-2026--07--28%20%7C%202025--11--25-128C7E" alt="MCP" />
  <img src="https://img.shields.io/badge/DeepSeek-plugin-128C7E" alt="DeepSeek" />
  <img src="https://img.shields.io/badge/version-1.0.1-25D366" alt="Version" />
  <img src="https://img.shields.io/badge/DeepSeek%20Harness-%3E%3D0.2.2--rc.1-4D6BFE" alt="dsh" />
</p>

<p align="center">
  <a href="https://wapliss.com/">Website</a> ·
  <a href="https://wapliss.com/integrations#deepseek">DeepSeek guide</a> ·
  <a href="https://wapliss.com/integraciones#deepseek">Guía en español</a> ·
  <a href="#example-prompts">Examples</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="#wapliss-plugins">Other assistants</a>
</p>

---

## What is Wapliss?

[Wapliss](https://wapliss.com/), by [NetDigitalTech LLC](https://netdigitaltech.com/), is a WhatsApp gateway for AI assistants. You
link your WhatsApp number once with a QR code, authorize your assistant, and
the assistant can read your chats and groups and send WhatsApp messages for
you through a standard [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) server. A free plan is available, with no credit card required.

This repository is the official **DeepSeek package** of Wapliss
(configuration-only DeepSeek Harness (`dsh`) bundle). It only points DeepSeek to the hosted Wapliss MCP
server; it stores no account data, messages or credentials.

## Compatibility

| Surface | How | Status |
| --- | --- | --- |
| DeepSeek Harness (`dsh web`, TUI, headless) with DeepSeek V4 | `dsh plugin --profile web add "github:proteuscrypto/wapliss-for-deepseek#main"` | Works (tested with `dsh` 0.2.2-rc.1) |
| DeepSeek chat (chat.deepseek.com, mobile apps) | Not possible: no MCP connectors | — |
| Your own agent on the DeepSeek API | Any MCP client: see [wapliss.com/integrations#mcp](https://wapliss.com/integrations#mcp) | Works |

## Quick start

1. Create a free account at [wapliss.com](https://wapliss.com/) and link your
   phone once at [wapliss.com/app/connect](https://wapliss.com/app/connect).
2. Create a personal API key in **Settings → API keys**
   ([wapliss.com/app/settings#api-keys](https://wapliss.com/app/settings#api-keys)).
   It is shown only once.
3. Store it and install the bundle:

   ```sh
   echo 'WAPLISS_API_KEY=wp_live_your_key' >> ~/.dsh/.env && chmod 600 ~/.dsh/.env
   npx -y @deepseek-ai/dsh plugin --profile web add "github:proteuscrypto/wapliss-for-deepseek#main"
   npx -y @deepseek-ai/dsh web
   ```

   Web UI alternative: **Settings → Plugins → Add** with
   `github:proteuscrypto/wapliss-for-deepseek#main`.
4. Ask: *"Check my Wapliss account"*. Tools appear as `mcp__wapliss__*`.

Without `WAPLISS_API_KEY` the Wapliss row stays disabled: the harness starts
normally and nothing is sent to Wapliss.

Optional skill: `mkdir -p ~/.agents/skills && cp -r skills/wapliss-whatsapp ~/.agents/skills/`.

## Example prompts

| Goal | Ask  |
| --- | --- |
| Catch up | "Show me my latest WhatsApp messages" |
| Summarize a group | "Summarize what was said today in my family group" |
| Read a chat | "Read my last 20 messages with Ana and tell me what she needs" |
| Group info | "Who are the admins of the work group?" |
| Send a message | "Send 'On my way, 10 minutes' to +1 555 010 2030" |
| Send a file | "Send this PDF to Laura: https://example.com/quote.pdf" |
| Share a location | "Send the office location to the project group" |
| Run a poll | "Create a poll in the team group: Friday or Monday?" |
| Check the account | "Check my Wapliss account and today's usage" |

Tips: name the chat or group as it appears in WhatsApp, or use the number with
country code. The assistant shows you the recipient and the text before
sending when anything is ambiguous.

## What it can do (16 tools)

| Area | Tools | What they do |
| --- | --- | --- |
| Chats and groups | `get_chats`, `get_chat_history`, `get_message` | List and search your conversations, read a chat or group in order, get one message |
| Latest activity | `get_last_incoming_messages`, `get_last_outgoing_messages` | What you received or sent recently, across all chats |
| Groups | `get_group` | Name, description, admins and participants |
| Send | `send_text_message`, `send_image`, `send_document`, `send_audio`, `send_video`, `send_location`, `send_contact`, `send_poll`, `forward_messages` | Text, files by public URL, locations, contact cards, polls and forwards |
| Account | `get_account_status` | Plan, linked number, daily usage and quota |

Every tool declares MCP annotations (`readOnlyHint`, `destructiveHint`,
`idempotentHint`, `openWorldHint`). Send tools are marked destructive, so the
assistant asks for confirmation. A successful send means the message was
**queued** (with a `queue_id`), not yet delivered.

## How it works

```text
DeepSeek Harness (dsh web / tui / headless, DeepSeek V4)
        |  @deepseek-ai/dsh-mcp-client, Streamable HTTP
        |  Authorization: Bearer $WAPLISS_API_KEY
        v
https://wapliss.com/mcp/v1   (MCP 2026-07-28 and 2025-11-25)
        |
Wapliss WhatsApp engine  --->  WhatsApp
```

`cordis.patch.yml` inserts a single row:

```yaml
- insert:
    - id: wapliss-whatsapp
      name: '@deepseek-ai/dsh-mcp-client'
      disabled: !!js '!process.env.WAPLISS_API_KEY'
      config:
        serverName: wapliss
        transport: streamable-http
        url: https://wapliss.com/mcp/v1
        headers:
          Authorization: !!js '`Bearer ${process.env.WAPLISS_API_KEY}`'
        toolCallTimeoutMs: 60000
        failOnStartupError: false
```

To change a setting, override the row by `id` in your profile's
`cordis.patch.yml`, restating the whole `config`.

## Security and privacy

- **Your own account only.** The assistant can reach only the WhatsApp account
  linked to your Wapliss account, and only when you ask.
- **No credentials in the chat.** Never paste passwords, API keys, QR data or
  session data into a conversation; this package contains none either.
- **Confirmation before sending.** Ambiguous recipients or texts are confirmed
  first; bulk or unsolicited messaging is not allowed.
- **Revocable at any time** from the Wapliss dashboard.
- **Limits:** daily plan quota and 60 MCP calls per minute per user.
- [Privacy policy](https://wapliss.com/privacy-policy) ·
  [Terms of service](https://wapliss.com/terms-of-service)

## FAQ

**Is it free?** Yes, there is a free plan to start, with no credit card.

**Does it use the official WhatsApp Business Platform?** No. Wapliss links
your number as a WhatsApp linked device, like WhatsApp Web, so it works with
your personal or business number without a Meta Business account. Use it for
your own conversations and follow WhatsApp's terms.

**Can the assistant send messages on its own?** No. It only acts when you ask,
confirms ambiguous sends and refuses bulk or unsolicited messages.

**Where are my messages stored?** In your private Wapliss account, so the
assistant can read them when you ask. What the assistant reads is processed by
its AI provider. See the [privacy policy](https://wapliss.com/privacy-policy).

**Can I use several assistants at once?** Yes. Each one is authorized
separately and can be revoked separately.

**Why an API key instead of OAuth?** The DeepSeek Harness MCP client only
sends static headers. Your key is read from `WAPLISS_API_KEY`, never written in
the profile or the conversation, and can be revoked instantly; a key cannot
create or list other keys.

**Does it work in the DeepSeek chat app?** No, that app has no MCP connectors.
Use DeepSeek Harness, DeepSeek's open-source agent.

## Troubleshooting

| Message from Wapliss | What it means | What to do |
| --- | --- | --- |
| `account_awaiting_qr` / `instance_not_connected` | No phone is linked to this Wapliss account | Link it at [wapliss.com/app/connect](https://wapliss.com/app/connect) |
| `account_disconnected` | WhatsApp closed the linked session | Scan the QR code again |
| `quota_exceeded` | Daily message quota reached | Wait for the reset or upgrade the plan |
| Rate limit (`-32300` / HTTP 429) | More than 60 calls in a minute | Wait the seconds indicated |
| `chat_not_found` | No chat matches the name or number | Search with another name or the full number with country code |

## Package layout

```text
package.json                      dsh bundle manifest (dsh.bundle.patch, engines.dsh, exports, files)
cordis.patch.yml                  One @deepseek-ai/dsh-mcp-client row for the Wapliss MCP server
locale/*.json                     Title and description in en, es, pt, zh, fr, de, ja, ru
icon.png                          512 × 512 icon
skills/wapliss-whatsapp/SKILL.md  dsh skill (name, description, whenToUse)
listing/plugin-index.json         Plugin index (format 1) for the dsh Discover tab
scripts/validate.py               Static and --live checks
```

## Validate and uninstall

```bash
pip install pyyaml
python3 scripts/validate.py          # static checks of the bundle
python3 scripts/validate.py --live   # + public endpoint checks (WAPLISS_API_KEY optional)
npx -y @deepseek-ai/dsh plugin --profile web remove dsh-plugin-wapliss   # uninstall
```

## Wapliss plugins

Wapliss works the same way in every assistant: one account, one linked phone,
the same 16 tools.

| Assistant | Where it works | Format | Get it |
| --- | --- | --- | --- |
| Claude | Claude.ai, Claude Desktop, Claude Code | Custom connector / Claude plugin | [github.com/proteuscrypto/wapliss-whatsapp-for-claude](https://github.com/proteuscrypto/wapliss-whatsapp-for-claude) |
| ChatGPT | ChatGPT web and desktop | ChatGPT plugin (Agent Plugins) / custom MCP connector | [github.com/proteuscrypto/wapliss-for-chatgpt](https://github.com/proteuscrypto/wapliss-for-chatgpt) |
| Gemini | Gemini app, Gemini CLI, Antigravity | Connected app, Gemini CLI extension, Antigravity plugin | [github.com/proteuscrypto/wapliss-for-gemini](https://github.com/proteuscrypto/wapliss-for-gemini) |
| **DeepSeek** | DeepSeek Harness (dsh) | dsh bundle | this repository |
| GitHub Copilot | VS Code, Copilot CLI, Copilot app | Agent Plugins 1.0 | [github.com/proteuscrypto/wapliss-for-copilot](https://github.com/proteuscrypto/wapliss-for-copilot) |
| Grok | Grok Build, grok.com connectors, xAI API | Grok Build plugin / custom MCP connector | [github.com/proteuscrypto/wapliss-for-grok](https://github.com/proteuscrypto/wapliss-for-grok) |
| Any MCP client | Clients with remote MCP (Streamable HTTP) | OAuth 2.1, or a personal API key | [wapliss.com/integrations#mcp](https://wapliss.com/integrations#mcp) |

## Credits and support

- **Created and maintained by [NetDigitalTech LLC](https://netdigitaltech.com/)**
  ([GitHub](https://github.com/netdigitaltech)), the company that created and owns
  [Wapliss](https://wapliss.com/). NetDigitalTech builds web, mobile and AI
  applications. Albuquerque, New Mexico, USA · commerce@netdigitaltech.com
- Support: [open an issue](https://github.com/proteuscrypto/wapliss-for-deepseek/issues) in this repository.
- Integration guides: [English](https://wapliss.com/integrations#deepseek) ·
  [Español](https://wapliss.com/integraciones#deepseek)

## Español

**Wapliss WhatsApp para DeepSeek**: conecta tu propio WhatsApp a
DeepSeek con el servidor MCP de Wapliss. Lee y resume chats y grupos y
envía mensajes, archivos, ubicaciones y encuestas, siempre con tu confirmación.

Cómo empezar: crea tu cuenta gratis y vincula tu teléfono, crea una API Key en
[wapliss.com/app/settings#api-keys](https://wapliss.com/app/settings#api-keys),
guárdala como `WAPLISS_API_KEY` en `~/.dsh/.env` e instala con
`npx -y @deepseek-ai/dsh plugin --profile web add "github:proteuscrypto/wapliss-for-deepseek#main"`.
El chat web de DeepSeek no admite conectores MCP: se usa DeepSeek Harness.

Ejemplos: *"Muéstrame mis últimos mensajes de WhatsApp"*, *"Resume lo que se
habló hoy en el grupo de la familia"*, *"Envía 'Llego en 10 minutos' a
+54 9 11 5555 0100"*. Creado y mantenido por **[NetDigitalTech LLC](https://netdigitaltech.com/)**,
la empresa creadora y dueña de [Wapliss](https://wapliss.com/). Guía completa:
[wapliss.com/integraciones#deepseek](https://wapliss.com/integraciones#deepseek).

## Trademarks and license

DeepSeek is a trademark of Hangzhou DeepSeek Artificial Intelligence Co., Ltd. WhatsApp is a trademark of Meta Platforms, Inc. Wapliss is
an independent service and is not affiliated with, sponsored or endorsed by
Meta, WhatsApp or DeepSeek.

Released under the [MIT License](LICENSE). © 2026 NetDigitalTech LLC, creator and owner of Wapliss.
