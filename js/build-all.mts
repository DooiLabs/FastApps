import { build, type InlineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import fg from "fast-glob";
import path from "path";
import fs from "fs";
import crypto from "crypto";

// Read package.json from current working directory (project root)
const pkgPath = path.join(process.cwd(), "package.json");
const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf-8"));

// Auto-detect and import Tailwind CSS if available
let tailwindcss: any = null;
try {
  const tailwindModule = await import("@tailwindcss/vite");
  tailwindcss = tailwindModule.default;
  console.log("✓ Tailwind CSS detected");
} catch (e) {
  // Tailwind not installed, skip
}

// Find all widget directories with index.{tsx,jsx}
const widgetDirs = fg.sync("widgets/*/", { onlyDirectories: true });
const entries = widgetDirs.map((dir) => {
  const dirPath = dir.endsWith('/') ? dir : dir + '/';
  const indexFiles = fg.sync(`${dirPath}index.{tsx,jsx}`);
  return indexFiles[0];
}).filter(Boolean);
const outDir = "assets";

// Determine build mode: 'hosted' (default) or 'inline'
const modeEnv = (process.env.MODE ?? "").toLowerCase();
const MODE: "hosted" | "inline" = modeEnv === "inline" ? "inline" : "hosted";

// Global CSS that applies to all widgets
const GLOBAL_CSS_PATH = path.resolve("widgets/index.css");
const PER_ENTRY_CSS_GLOB = "**/*.{css,pcss,scss,sass}";
const PER_ENTRY_CSS_IGNORE = ["**/*.module.*"];

function wrapEntryPlugin(
  virtualId: string,
  entryFile: string,
  widgetName: string,
  cssPaths: string[]
): Plugin {
  return {
    name: `virtual-entry-wrapper:${entryFile}`,
    resolveId(id) {
      if (id === virtualId) return id;
    },
    load(id) {
      if (id !== virtualId) {
        return null;
      }

      // Import CSS files (global first, then per-entry)
      const cssImports = cssPaths
        .map((css) => `import ${JSON.stringify(css)};`)
        .join("\n");

      // Automatically add mounting logic - no _app.jsx needed!
      return `
    ${cssImports}
    import React from 'react';
    import { createRoot } from 'react-dom/client';
    import Component from ${JSON.stringify(entryFile)};

    // Auto-mount the component
    const rootElement = document.getElementById('${widgetName}-root');
    if (rootElement) {
      const root = createRoot(rootElement);
      root.render(React.createElement(Component));
    } else {
      console.error('Root element #${widgetName}-root not found!');
    }
  `;
    },
  };
}

fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

const builtNames: string[] = [];

for (const file of entries) {
  const name = path.basename(path.dirname(file));

  const entryAbs = path.resolve(file);
  const entryDir = path.dirname(entryAbs);

  // Collect CSS paths: global first, then per-entry
  const cssPaths: string[] = [];

  // Add global CSS if it exists
  if (fs.existsSync(GLOBAL_CSS_PATH)) {
    cssPaths.push(GLOBAL_CSS_PATH);
  }

  // Add per-entry CSS
  const perEntryCss = fg.sync(PER_ENTRY_CSS_GLOB, {
    cwd: entryDir,
    absolute: true,
    dot: false,
    ignore: PER_ENTRY_CSS_IGNORE,
  });
  cssPaths.push(...perEntryCss);

  const virtualId = `\0virtual-entry:${entryAbs}`;

  const createConfig = (): InlineConfig => ({
    plugins: [
      wrapEntryPlugin(virtualId, entryAbs, name, cssPaths),
      react(),
      ...(tailwindcss ? [tailwindcss()] : []),
      {
        name: "remove-manual-chunks",
        outputOptions(options) {
          if ("manualChunks" in options) {
            delete (options as any).manualChunks;
          }
          return options;
        },
      },
    ],
    esbuild: {
      jsx: "automatic",
      jsxImportSource: "react",
      target: "es2022",
    },
    build: {
      target: "es2022",
      outDir,
      emptyOutDir: false,
      chunkSizeWarningLimit: 2000,
      minify: "esbuild",
      cssCodeSplit: false,
      rollupOptions: {
        input: virtualId,
        output: {
          format: "es",
          entryFileNames: `${name}.js`,
          inlineDynamicImports: true,
          assetFileNames: (info) =>
            (info.name || "").endsWith(".css")
              ? `${name}.css`
              : `[name]-[hash][extname]`,
        },
        preserveEntrySignatures: "allow-extension",
        treeshake: true,
      },
    },
  });

  console.group(`Building ${name} (react)`);
  await build(createConfig());
  console.groupEnd();
  builtNames.push(name);
  console.log(`Built ${name}`);

  // Ensure CSS file exists (create empty one if not generated)
  const cssFile = path.join(outDir, `${name}.css`);
  if (!fs.existsSync(cssFile)) {
    fs.writeFileSync(cssFile, "", "utf8");
    console.log(`Created empty CSS file for ${name}`);
  }
}

const outputs = fs
  .readdirSync("assets")
  .filter((f) => f.endsWith(".js") || f.endsWith(".css"))
  .map((f) => path.join("assets", f))
  .filter((p) => fs.existsSync(p));

const renamed = [];

const h = crypto
  .createHash("sha256")
  .update(pkg.version, "utf8")
  .digest("hex")
  .slice(0, 4);

console.group("Hashing outputs");
for (const out of outputs) {
  const dir = path.dirname(out);
  const ext = path.extname(out);
  const base = path.basename(out, ext);
  const newName = path.join(dir, `${base}-${h}${ext}`);

  fs.renameSync(out, newName);
  renamed.push({ old: out, neu: newName });
  console.log(`${out} -> ${newName}`);
}
console.groupEnd();

console.log("new hash: ", h);

if (MODE === "inline") {
  for (const name of builtNames) {
    const dir = outDir;
    const htmlPath = path.join(dir, `${name}-${h}.html`);
    const cssPath = path.join(dir, `${name}-${h}.css`);
    const jsPath = path.join(dir, `${name}-${h}.js`);

    const css = fs.existsSync(cssPath)
      ? fs.readFileSync(cssPath, { encoding: "utf8" })
      : "";
    const js = fs.existsSync(jsPath)
      ? fs.readFileSync(jsPath, { encoding: "utf8" })
      : "";

    const cssBlock = css ? `\n  <style>\n${css}\n  </style>\n` : "";
    const jsBlock = js ? `\n  <script type="module">\n${js}\n  </script>` : "";

    const html = [
      "<!doctype html>",
      "<html>",
      `<head>${cssBlock}</head>`,
      "<body>",
      `  <div id="${name}-root"></div>${jsBlock}`,
      "</body>",
      "</html>",
    ].join("\n");
    fs.writeFileSync(htmlPath, html, { encoding: "utf8" });
    console.log(`${htmlPath} (generated inline)`);
  }
} else {
  // Use relative /assets path to work with the proxy server
  // This allows assets to be served through the same origin, avoiding CORS/PNA/mixed content issues
  const defaultBaseUrl = "/assets";
  const baseUrlCandidate = process.env.BASE_URL?.trim() ?? "";
  const baseUrlRaw = baseUrlCandidate || defaultBaseUrl;
  const normalizedBaseUrl = baseUrlRaw.replace(/\/+$/, "");
  console.log(`Using BASE_URL: ${normalizedBaseUrl}`);
  for (const name of builtNames) {
    const dir = outDir;
    const htmlPath = path.join(dir, `${name}-${h}.html`);
    const html = `<!doctype html>
<html>
<head>
  <script type="module" src="${normalizedBaseUrl}/${name}-${h}.js"></script>
  <link rel="stylesheet" href="${normalizedBaseUrl}/${name}-${h}.css">
</head>
<body>
  <div id="${name}-root"></div>
</body>
</html>
`;
    fs.writeFileSync(htmlPath, html, { encoding: "utf8" });
    console.log(`${htmlPath} (generated)`);
  }
}
