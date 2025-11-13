# fastapps (React Hooks)

React hooks for building interactive ChatGPT widgets with the FastApps framework.

## Installation

```bash
npm install fastapps
```

## Usage

### useWidgetProps

Get data passed from your Python MCP tool to your React widget:

```jsx
import React from 'react';
import { useWidgetProps } from 'fastapps';

export default function MyWidget() {
  const { message, count } = useWidgetProps();
  
  return (
    <div>
      <h1>{message}</h1>
      <p>Count: {count}</p>
    </div>
  );
}
```

### useWidgetState

Manage stateful data that persists across ChatGPT sessions:

```jsx
import React from 'react';
import { useWidgetState } from 'fastapps';

export default function Counter() {
  const [state, setState] = useWidgetState({ count: 0 });
  
  return (
    <button onClick={() => setState({ count: state.count + 1 })}>
      Count: {state?.count || 0}
    </button>
  );
}
```

### useOpenAiGlobal

Access ChatGPT environment information like theme, display mode, locale, and more:

```jsx
import React from 'react';
import { useOpenAiGlobal } from 'fastapps';

export default function ThemedWidget() {
  const theme = useOpenAiGlobal('theme');
  const displayMode = useOpenAiGlobal('displayMode');
  const locale = useOpenAiGlobal('locale');
  const maxHeight = useOpenAiGlobal('maxHeight');
  
  return (
    <div 
      className={`theme-${theme} mode-${displayMode}`}
      style={{ maxHeight: `${maxHeight}px` }}
    >
      <h1>Themed Widget ({locale})</h1>
    </div>
  );
}
```

### useDisplayMode

Access the current display mode (inline, pip, or fullscreen):

```jsx
import React from 'react';
import { useDisplayMode } from 'fastapps';

export default function ResponsiveWidget() {
  const displayMode = useDisplayMode();
  
  return (
    <div className={`mode-${displayMode}`}>
      {displayMode === 'fullscreen' ? (
        <div>Full screen layout</div>
      ) : (
        <div>Compact layout</div>
      )}
    </div>
  );
}
```

### useMaxHeight

Access the maximum height constraint for the widget:

```jsx
import React from 'react';
import { useMaxHeight } from 'fastapps';

export default function ScrollableWidget() {
  const maxHeight = useMaxHeight();
  
  return (
    <div style={{ maxHeight: `${maxHeight}px`, overflow: 'auto' }}>
      <p>Content that respects the max height constraint</p>
      {/* More content... */}
    </div>
  );
}
```

## Available Hooks

### Core Hooks

- **`useOpenAiGlobal(key)`** - Access any ChatGPT environment property
- **`useWidgetProps<T>(defaultState?)`** - Access tool output data from your Python tool
- **`useWidgetState<T>(defaultState)`** - Persistent state management that syncs with ChatGPT
- **`useDisplayMode()`** - Get current display mode (inline/pip/fullscreen)
- **`useMaxHeight()`** - Get maximum height constraint in pixels

### Available OpenAI Globals

Use `useOpenAiGlobal(key)` to access:
  - `theme` - Light or dark mode
  - `displayMode` - inline, pip, or fullscreen
  - `locale` - User's locale (IETF BCP 47)
  - `maxHeight` - Layout height constraint
  - `safeArea` - Mobile safe area insets
  - `userAgent` - Device and capabilities
  - `toolInput` - Input parameters
  - `toolOutput` - Tool response data
  - `toolResponseMetadata` - Response metadata
  - `widgetState` - Current persistent state

### Custom Convenience Hooks

You can easily create your own convenience hooks:

```typescript
// Access tool input
export function useToolInput() {
  return useOpenAiGlobal('toolInput');
}

// Access theme
export function useTheme() {
  return useOpenAiGlobal('theme');
}
```

## Advanced: Direct window.openai API

```jsx
// Call backend tools
await window.openai.callTool('refresh_data', { city: 'NYC' });

// Send follow-up messages
await window.openai.sendFollowUpMessage({ 
  prompt: 'Tell me more' 
});

// Request display mode changes
await window.openai.requestDisplayMode({ 
  mode: 'fullscreen' 
});

// Open external links
window.openai.openExternal({ href: 'https://example.com' });
```

## TypeScript Support

This package is written in TypeScript and includes full type definitions:

```tsx
import { 
  useWidgetProps, 
  useOpenAiGlobal,
  useDisplayMode,
  useMaxHeight 
} from 'fastapps';
import type { Theme, DisplayMode, UserAgent } from 'fastapps';

interface MyWidgetProps {
  message: string;
  count: number;
}

export default function MyWidget() {
  const props = useWidgetProps<MyWidgetProps>();
  const theme = useOpenAiGlobal('theme');
  const displayMode = useDisplayMode();
  const maxHeight = useMaxHeight();
  
  // Fully typed!
  return (
    <div 
      className={`theme-${theme}`}
      style={{ maxHeight: `${maxHeight}px` }}
    >
      {props.message} (Mode: {displayMode})
    </div>
  );
}
```

## Documentation

Full documentation available at [fastapps.org](https://fastapps.org)

## Part of FastApps Framework

This package is the React hooks component of the FastApps framework for building ChatGPT widgets.

- **Python SDK**: `pip install fastapps`
- **React Hooks**: `npm install fastapps`

## License

MIT

