# Pizzaz FastApps Example

End-to-end port of the [OpenAI Apps SDK “Pizzaz” gallery](https://github.com/openai/openai-apps-sdk-examples) built entirely with FastApps.

This example demonstrates:

- Multiple widgets + tools in a single FastApps app (map, carousel, albums, list, shop)
- Shared React utilities (routing, widget state, Tailwind 4 styling)
- Custom build pipeline (`build-all.mts`) with Tailwind CSS 4 (`@tailwindcss/vite`)

## Prerequisites

- Python 3.11+ (for FastApps CLI)
- Node.js 18+ / npm 8+
- `fastapps` CLI installed globally (`uv tool install fastapps` or `pipx install fastapps`)

## Quick Start

```bash
cd examples/pizzaz
npm install          # install React/Tailwind deps
npm run build        # or: fastapps build
fastapps dev         # starts MCP server + Cloudflare tunnel
```

`fastapps dev` prints the public tunnel URL (e.g. `https://xxx.trycloudflare.com/mcp`). Add that URL to ChatGPT Connectors or use [MCPJam Inspector](https://www.npmjs.com/package/@mcpjam/inspector) to view each widget.

> **Note:** Mapbox GL uses the demo token baked into `widgets/pizza-map/index.jsx`. Replace `mapboxgl.accessToken` with your own for production use.

## Scripts

| Command            | Description                            |
| ------------------ | -------------------------------------- |
| `npm run build`    | Runs `build-all.mts` to bundle widgets |
| `fastapps build`   | Same as above (calls the script)       |
| `fastapps dev`     | Dev server + Cloudflare tunnel         |

## Widget/Tool Mapping

| Tool identifier  | Widget path                        | Description                     |
| ---------------- | ---------------------------------- | ------------------------------- |
| `pizza-map`      | `widgets/pizza-map/`               | Mapbox map + inspector sidebar |
| `pizza-carousel` | `widgets/pizza-carousel/`          | Embla carousel of places       |
| `pizza-albums`   | `widgets/pizza-albums/`            | Photo albums + fullscreen view |
| `pizza-list`     | `widgets/pizza-list/`              | Ranked list UI                 |
| `pizza-shop`     | `widgets/pizza-shop/`              | Cart/checkout demo             |

Python backend lives in `server/tools/*.py` (one `BaseWidget` per identifier). Shared inputs/constants are in `server/tools/pizzaz_common.py`.

## Project Structure

```
examples/pizzaz
├── build-all.mts             # Vite build orchestrator (with Tailwind plugin)
├── package.json              # npm deps (Tailwind, mapbox-gl, etc.)
├── server/
│   ├── main.py               # FastApps auto-discovery server
│   └── tools/                # Backend widgets (pizzaz_common, pizza_*_tool.py)
├── widgets/
│   ├── pizza-map/            # Mapbox widget + inspector/sidebar
│   ├── pizza-carousel/       # Carousel widget
│   ├── pizza-albums/         # Albums widget
│   ├── pizza-list/           # List widget
│   ├── pizza-shop/           # Cart widget
│   ├── shared/               # Shared JSON data (markers)
│   └── styles/index.css      # Tailwind 4 entrypoint
└── tailwind.config.ts        # Tailwind content configuration
```

Generated assets are ignored (`assets/`)—run `npm run build` whenever widgets change.

## Learn More

- **FastApps Framework**: https://pypi.org/project/fastapps/
- **FastApps React hooks**: https://www.npmjs.com/package/fastapps
- **Docs**: https://docs.fastapps.org/

## License

MIT (same as FastApps)
