# Official OpenAI Hooks Implementation

This package now matches the **exact hooks** provided in OpenAI's Apps SDK examples.

## ✅ Hooks Included (Matches OpenAI Official)

### Core Hooks
1. **`useOpenAiGlobal(key)`** - Base hook for accessing any global property
2. **`useWidgetProps<T>(defaultState?)`** - Access tool output with optional fallback
3. **`useWidgetState<T>(defaultState)`** - Persistent state management
4. **`useDisplayMode()`** - Get current display mode (inline/pip/fullscreen)
5. **`useMaxHeight()`** - Get maximum height constraint in pixels

## 📁 File Structure

```
chatjs-hooks/src/hooks/
├── types.ts                 # All TypeScript types and window.openai declarations
├── useOpenaiGlobal.ts       # Base hook using useSyncExternalStore
├── useWidgetProps.ts        # Tool output accessor with fallback support
├── useWidgetState.ts        # Persistent state management
├── useDisplayMode.ts        # Display mode convenience hook
└── useMaxHeight.ts          # Max height convenience hook
```

## 🔄 Changes Made

### Removed (Not in OpenAI Official)
- ❌ `useToolInput.ts` - Was only shown as an example in docs
- ❌ `useToolOutput.ts` - Was only shown as an example in docs  
- ❌ `useToolResponseMetadata.ts` - Was only shown as an example in docs

### Added (From OpenAI Official)
- ✅ `useDisplayMode.ts` - Official convenience hook
- ✅ `useMaxHeight.ts` - Official convenience hook

### Updated
- ✅ `useWidgetProps.ts` - Now matches OpenAI's signature with optional `defaultState` parameter and fallback logic
- ✅ `index.ts` - Exports only official hooks
- ✅ `README.md` - Documentation updated to match official hooks

## 📊 Comparison with OpenAI Examples

| Hook | OpenAI Examples | This Package | Status |
|------|----------------|--------------|---------|
| `useOpenAiGlobal` | ✅ | ✅ | ✅ Match |
| `useWidgetProps` | ✅ | ✅ | ✅ Match |
| `useWidgetState` | ✅ | ✅ | ✅ Match |
| `useDisplayMode` | ✅ | ✅ | ✅ Match |
| `useMaxHeight` | ✅ | ✅ | ✅ Match |
| `useToolInput` | ❌ (Example only) | ❌ | ✅ Match |
| `useToolOutput` | ❌ (Example only) | ❌ | ✅ Match |
| `useToolResponseMetadata` | ❌ (Example only) | ❌ | ✅ Match |

## 💡 Creating Custom Convenience Hooks

Users can easily create their own convenience hooks as needed:

```typescript
import { useOpenAiGlobal } from 'fastapps';

// Custom hook for tool input
export function useToolInput() {
  return useOpenAiGlobal('toolInput');
}

// Custom hook for theme
export function useTheme() {
  return useOpenAiGlobal('theme');
}

// Custom hook for locale
export function useLocale() {
  return useOpenAiGlobal('locale');
}
```

## 🎯 API Reference

### useOpenAiGlobal(key)
Base hook that subscribes to any global property from `window.openai`.

**Available keys:**
- `theme` - "light" | "dark"
- `displayMode` - "inline" | "pip" | "fullscreen"
- `locale` - IETF BCP 47 language tag
- `maxHeight` - number (pixels)
- `safeArea` - SafeArea object with insets
- `userAgent` - UserAgent object with device info
- `toolInput` - Tool input parameters
- `toolOutput` - Tool output data
- `toolResponseMetadata` - Response metadata
- `widgetState` - Current persistent state

### useWidgetProps(defaultState?)
Access tool output data with optional fallback.

```typescript
const props = useWidgetProps({ message: "default" });
```

### useWidgetState(defaultState)
Persistent state that syncs with ChatGPT.

```typescript
const [state, setState] = useWidgetState({ count: 0 });
```

### useDisplayMode()
Get current display mode.

```typescript
const displayMode = useDisplayMode(); // "inline" | "pip" | "fullscreen" | null
```

### useMaxHeight()
Get maximum height constraint.

```typescript
const maxHeight = useMaxHeight(); // number | null
```

## ✨ Benefits

1. **Official Compatibility** - Matches OpenAI's examples exactly
2. **Type Safety** - Full TypeScript support with proper types
3. **Reactive** - All hooks use `useSyncExternalStore` for automatic updates
4. **Extensible** - Easy to create custom convenience hooks
5. **Tree-shakable** - ESM build supports tree-shaking

## 📦 Build Output

- `dist/index.js` - CommonJS bundle (3.46 KB)
- `dist/index.mjs` - ES Module bundle (2.25 KB)
- `dist/index.d.ts` - TypeScript definitions
- `dist/index.d.mts` - TypeScript definitions for ESM

## 🔗 References

- [OpenAI Apps SDK Examples](https://github.com/openai/openai-apps-sdk-examples)
- [Apps SDK Documentation](https://platform.openai.com/docs/apps-sdk)

