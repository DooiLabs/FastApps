import { build, type InlineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import fg from "fast-glob";
import path from "path";
import fs from "fs";
import crypto from "crypto";

// Read package.json from current working directory (project root)
const pkgPath = path.join(process.cwd(), "package.json");
const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf-8"));

// Find all widget directories with index.{tsx,jsx}
const widgetDirs = fg.sync("widgets/*/", { onlyDirectories: true });
const entries = widgetDirs
  .map((dir) => {
    const dirPath = dir.endsWith("/") ? dir : dir + "/";
    const indexFiles = fg.sync(`${dirPath}index.{tsx,jsx}`);
    return indexFiles[0];
  })
  .filter(Boolean);
const outDir = "assets";

function wrapEntryPlugin(
  virtualId: string,
  entryFile: string,
  widgetName: string,
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

      // Automatically add mounting logic - no _app.jsx needed!
      return `
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

  const virtualId = `\0virtual-entry:${entryAbs}`;

  const createConfig = (): InlineConfig => ({
    plugins: [
      wrapEntryPlugin(virtualId, entryAbs, name),
      tailwindcss(),
      react(),
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
  console.log(`${htmlPath} (generated)`);
}
