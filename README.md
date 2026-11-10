<p align="center">
  <img src="icon.png" alt="Wapliss logo" width="120" />
</p>

# Wapliss WhatsApp for DeepSeek Harness

Use your own WhatsApp from [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)
(`dsh`) through [Wapliss](https://wapliss.com/). This repository is a
configuration-only dsh **bundle**: it mounts the in-box MCP client
(`@deepseek-ai/dsh-mcp-client`) against the hosted Wapliss MCP server at
`https://wapliss.com/mcp/v1`. It ships no code, no build step and no
credentials.

[Español](#español) · [Integration guide](https://wapliss.com/integrations#deepseek)

> The DeepSeek chat app (chat.deepseek.com) does not support MCP connectors.
> Wapliss works with DeepSeek through DeepSeek Harness, DeepSeek's open-source
> agent (Web UI, TUI and headless), with DeepSeek V4 models.

## Requirements

- DeepSeek Harness `>=0.2.2-rc.1 <0.3.0` (Node.js 22+): `npx @deepseek-ai/dsh web`
- A Wapliss account (free plan available) with your phone linked
- A personal Wapliss API key (`wp_live_...`)

## Install

1. **Create an API key.** Sign in at [wapliss.com](https://wapliss.com/), open
   **Settings > API keys** ([wapliss.com/app/settings#api-keys](https://wapliss.com/app/settings#api-keys))
   and create a key named "DeepSeek Harness". Copy it: it is shown only once.
2. **Store it as `WAPLISS_API_KEY`** in `~/.dsh/.env` (or `$DSH_HOME/.env`, a
   project `.env`, or the launch environment):

   ```sh
   echo 'WAPLISS_API_KEY=wp_live_your_key' >> ~/.dsh/.env
   chmod 600 ~/.dsh/.env
   ```

3. **Install the bundle** into your profile (`web`, `tui` or `headless`):

   ```sh
   npx -y @deepseek-ai/dsh plugin --profile web add "github:proteuscrypto/wapliss-for-deepseek#main"
   ```

   or from the Web UI: **Settings > Plugins > Add** with
   `github:proteuscrypto/wapliss-for-deepseek#main`.
4. **Restart** `dsh web` (or your profile). Check the composition with
   `dsh --profile web --dump-config` (look for `# == dsh-plugin-wapliss`).
5. **Link your phone** once at [wapliss.com/app/connect](https://wapliss.com/app/connect):
   WhatsApp > Linked devices > Link a device, then scan the QR code.
6. Ask: *"Check my Wapliss account"* or *"Show my latest WhatsApp messages"*.

Without `WAPLISS_API_KEY` the Wapliss row stays disabled: the harness starts
normally and nothing is sent to Wapliss.

### Optional: install the skill

`skills/wapliss-whatsapp/SKILL.md` teaches the agent when and how to use the
tools safely. dsh discovers skills in `~/.agents/skills`, `~/.dsh/skills` and
`<project>/.dsh/skills`:

```sh
git clone https://github.com/proteuscrypto/wapliss-for-deepseek
mkdir -p ~/.agents/skills && cp -r wapliss-for-deepseek/skills/wapliss-whatsapp ~/.agents/skills/
```

The server also sends its own instructions on connect, so the tools work
without the skill.

## What it can do (16 tools)

Tools appear in dsh as `mcp__wapliss__<tool>`.

| Area | Tools |
| --- | --- |
| Read chats and groups | `get_chats`, `get_chat_history`, `get_message` |
| Latest activity | `get_last_incoming_messages`, `get_last_outgoing_messages` |
| Groups | `get_group` (name, description, admins, participants) |
| Send | `send_text_message`, `send_image`, `send_document`, `send_audio`, `send_video`, `send_location`, `send_contact`, `send_poll`, `forward_messages` |
| Account | `get_account_status` (plan, usage, quota) |

Every tool declares `readOnlyHint`, `destructiveHint`, `idempotentHint` and
`openWorldHint`. Sends are queued: a successful call returns a `queue_id`, not
a delivery receipt. Bulk or unsolicited messaging is not allowed.

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

`cordis.patch.yml` inserts one row:

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

To change settings (for example the timeout), override the row by `id` in your
profile's `cordis.patch.yml`, restating the whole `config`:

```yaml
- id: wapliss-whatsapp
  config:
    serverName: wapliss
    transport: streamable-http
    url: https://wapliss.com/mcp/v1
    headers:
      Authorization: !!js '`Bearer ${process.env.WAPLISS_API_KEY}`'
    toolCallTimeoutMs: 120000
```

## Security and privacy

- The API key gives access to your WhatsApp through Wapliss: treat it like a
  password. Never paste it into a chat; the agent never needs to see it.
- dsh tool processes run as your OS user, so keep `.env` files private
  (`chmod 600`).
- Revoke a key at any time in **Settings > API keys**; access stops
  immediately. Keys cannot create or revoke other keys.
- Same limits as every Wapliss client: daily plan quota and 60 MCP calls per
  minute.
- [Privacy policy](https://wapliss.com/privacidad) ·
  [Terms of service](https://wapliss.com/terminos)

## Uninstall

```sh
npx -y @deepseek-ai/dsh plugin --profile web remove dsh-plugin-wapliss
```

Then revoke the API key in the Wapliss dashboard.

## Validate

```sh
pip install pyyaml
python3 scripts/validate.py          # static checks of the bundle
python3 scripts/validate.py --live   # + public endpoint checks (WAPLISS_API_KEY optional)
```

## Support

- Issues: <https://github.com/proteuscrypto/wapliss-for-deepseek/issues>
- Integration guide: <https://wapliss.com/integrations#deepseek>

---

## Español

**Wapliss WhatsApp para DeepSeek Harness.** Usa tu propio WhatsApp desde
DeepSeek Harness (`dsh`), el agente open source de DeepSeek, con los modelos
DeepSeek V4. El chat de DeepSeek (chat.deepseek.com) no admite conectores MCP.

1. Crea una API Key en [wapliss.com/app/settings#api-keys](https://wapliss.com/app/settings#api-keys)
   (se muestra una sola vez).
2. Guárdala como `WAPLISS_API_KEY` en `~/.dsh/.env`
   (`echo 'WAPLISS_API_KEY=wp_live_tu_clave' >> ~/.dsh/.env`).
3. Instala el plugin:
   `npx -y @deepseek-ai/dsh plugin --profile web add "github:proteuscrypto/wapliss-for-deepseek#main"`
4. Reinicia `dsh web`.
5. Vincula tu teléfono una vez en [wapliss.com/app/connect](https://wapliss.com/app/connect).
6. Pide: *"Revisa mi cuenta de Wapliss"* o *"Muéstrame mis últimos mensajes de WhatsApp"*.

Nunca pegues la API Key en un chat. Puedes revocarla cuando quieras desde el
panel; el acceso se corta al instante. Guía completa:
[wapliss.com/integraciones#deepseek](https://wapliss.com/integraciones#deepseek).

## License

MIT
