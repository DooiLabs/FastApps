/**
 * FastApps React Hooks - React hooks for building ChatGPT widgets
 * 
 * @packageDocumentation
 */

export { useOpenAiGlobal } from './hooks/useOpenaiGlobal';
export { useWidgetProps } from './hooks/useWidgetProps';
export { useWidgetState } from './hooks/useWidgetState';
export { useDisplayMode } from './hooks/useDisplayMode';
export { useMaxHeight } from './hooks/useMaxHeight';

export type {
  OpenAiGlobals,
  UnknownObject,
  Theme,
  SafeArea,
  SafeAreaInsets,
  DeviceType,
  UserAgent,
  DisplayMode,
  CallToolResponse,
} from './hooks/types';

