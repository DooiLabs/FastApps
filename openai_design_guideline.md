# OpenAI Apps SDK Design Guidelines

> Official design guidelines for building ChatGPT widgets with OpenAI Apps SDK  
> Source: https://developers.openai.com/apps-sdk/concepts/design-guidelines/

---

## Overview

Apps are developer-built experiences embedded in ChatGPT through lightweight cards, carousels, fullscreen views, and other formats that integrate seamlessly while maintaining ChatGPT's clarity and trustworthiness.

---

## 🎯 Core Principles

### 1. **Conversational**
- Extensions should feel natural within chat flow and UI
- Integrate seamlessly into the conversation

### 2. **Intelligent**
- Tools remain aware of conversation context
- Anticipate user needs with individually relevant responses

### 3. **Simple**
- Each interaction targets a **single clear action**
- Present minimal information needed for the task

### 4. **Responsive**
- Experiences should feel **fast and lightweight**
- Enhance conversation, don't overwhelm it

### 5. **Accessible**
- Designs must support users relying on **assistive technologies**
- Follow WCAG AA standards

---

## 🎨 Boundaries

### What ChatGPT Controls (System-Level)
- ❌ Voice and tone
- ❌ Chrome and navigation
- ❌ System styles
- ❌ Composer interface

### What Developers Customize (Content-Level)
- ✅ Widget content
- ✅ Branding (logos, icons)
- ✅ Actions and interactions
- ✅ Data presentation

**Goal:** All apps feel native to ChatGPT while expressing unique value.

---

## ✅ Use Case Evaluation

### Strong Candidates (Build These)
Apps that satisfy most of these criteria:

- ✅ **Tasks fitting naturally into conversation**
  - Booking, ordering, scheduling, quick lookups
  
- ✅ **Time-bound or action-oriented activities**
  - Clear start and end points
  
- ✅ **Immediately actionable information**
  - Content users can act on right away
  
- ✅ **Visually summarizable content**
  - Clear calls-to-action with minimal visual elements
  
- ✅ **Genuinely additive functionality**
  - Differentiated value over ChatGPT's native capabilities

### Avoid Building (Don't Build These)

- ❌ **Long-form content** better suited for websites
- ❌ **Complex multi-step workflows** exceeding display capabilities
- ❌ **Advertisements or upsells**
- ❌ **Sensitive information** in shareable cards
- ❌ **Duplicate ChatGPT's system functions**

---

## 📱 Display Modes

### 1. Inline Cards

**When to use:** Single actions, structured data, self-contained widgets

**Structure:**
```
┌─────────────────────────┐
│ [Icon] Tool Label       │
├─────────────────────────┤
│                         │
│   Widget Content        │
│                         │
├─────────────────────────┤
│ [Primary] [Secondary]   │
└─────────────────────────┘
```

**Layout Requirements:**
- Optional title for document-based content
- Expand button for fullscreen access
- "Show more" for additional items
- Edit controls supporting ChatGPT responses
- **Maximum 2 primary actions** at card bottom

**Constraints:**
- ❌ No deep navigation, tabs, or multi-view drilling
- ❌ No nested scrolling (auto-fit content height)
- ❌ No duplicative inputs mimicking ChatGPT features
- ✅ Edits persist once made

---

### 2. Inline Carousel

**When to use:** Small lists of similar items with visual content

**Appropriate for:**
- Restaurants, playlists, events
- Product galleries
- Search results (3-8 items)

**Layout Requirements:**
- ✅ Image in **every item**
- ✅ Title explaining content
- ✅ Metadata **limited to 2 lines maximum**
- ✅ Optional badge for supporting context
- ✅ **Single clear CTA per item**

**Guidelines:**
- Keep **3–8 items** for scannability
- Use consistent visual hierarchy
- Reduce metadata to most relevant details

---

### 3. Fullscreen

**When to use:** Rich tasks unsuitable for single cards

**Appropriate for:**
- Maps with pins
- Editing canvas
- Interactive diagrams
- Detailed content browsing

**Structure:**
```
┌─────────────────────────┐
│ [X Close]          [···]│
├─────────────────────────┤
│                         │
│                         │
│   Full Content Area     │
│                         │
│                         │
├─────────────────────────┤
│ ChatGPT Composer Overlay│
└─────────────────────────┘
```

**Critical Guidelines:**
- ✅ ChatGPT's composer **remains overlaid** for continued conversation
- ✅ Composer "shimmers" during response streaming
- ✅ Ephemeral snippet displays above composer when model responds
- ❌ Don't replicate native app wholesale
- ✅ Use fullscreen to **deepen engagement**, not replace conversation

---

### 4. Picture-in-Picture (PiP)

**When to use:** Parallel activities running alongside conversation

**Appropriate for:**
- Games or collaboration
- Quizzes or learning exercises
- Live sessions
- Situations where widget **reacts to chat input**

**Interaction Patterns:**
- Activates on scroll, fixing window to viewport top
- Remains pinned until dismissed or session ends
- Returns to inline position when session concludes

**Requirements:**
- ✅ PiP state updates responsively to user interactions
- ✅ Automatic closure when session ends
- ❌ No control overload or static content

---

## 🎨 Visual Design Standards

### Color Palette

**System-Defined Colors:**
- ✅ **Use system colors** for text, icons, and dividers
- ✅ Brand accents allowed for: logos, icons, **primary buttons only**
- ❌ **Cannot override** backgrounds or text colors
- ❌ Avoid custom gradients or patterns

**Examples:**
```jsx
// ✅ Good
className="bg-white text-black"
className="border-black/10"

// ❌ Bad
className="bg-[#F46C21]"  // Custom brand orange
style={{ background: '#010304' }}  // Custom colors
```

---

### Typography

**Platform-Native System Fonts:**
- iOS: **SF Pro**
- Android: **Roboto**

**Rules:**
- ✅ **Always inherit the system font stack**
- ✅ Respect system sizing for headings, body text, captions
- ✅ Apply partner styling (bold, italic, highlights) **within content areas only**
- ✅ Minimize font size variation (prefer body and body-small)
- ❌ **Never implement custom fonts**, even in fullscreen

**Examples:**
```jsx
// ✅ Good
<div>Welcome to FastApps</div>

// ❌ Bad
<div style={{ fontFamily: 'monospace' }}>Welcome</div>
<div style={{ fontFamily: 'Comic Sans' }}>Welcome</div>
```

---

### Spacing & Layout

**System Grid Spacing:**
- ✅ Use system grid spacing for cards, collections, panels
- ✅ Maintain consistent padding
- ✅ Avoid cramped or edge-to-edge text
- ✅ Respect system-specified corner radius values
- ✅ Establish clear visual hierarchy

**Examples:**
```jsx
// ✅ Good
className="p-4 rounded-2xl"
className="space-y-3"

// ⚠️ Avoid
style={{ padding: '40px' }}  // Hardcoded values
className="p-[37px]"  // Arbitrary spacing
```

---

### Icons & Imagery

**Guidelines:**
- ✅ Use system icons or custom iconography fitting ChatGPT's visual language
- ✅ **Monochromatic and outlined** style preferred
- ❌ **Never include your logo as part of the response**
  - ChatGPT automatically appends logo and app name
- ✅ All imagery must follow **enforced aspect ratios** (no distortion)

**Examples:**
```jsx
// ❌ Bad - Embedded logo
<img src="https://example.com/logo.png" alt="Company Logo" />

// ✅ Good - Content images only
<img src={item.thumbnail} alt={item.description} />
```

---

### Accessibility (Non-Negotiable)

**Requirements:**
- ✅ **Text and background** maintain **minimum contrast ratio (WCAG AA: 4.5:1)**
- ✅ **Provide alt text for all images**
- ✅ Support **text resizing** without layout breaking
- ✅ All interactive elements must be keyboard accessible

**Contrast Ratio Examples:**
```jsx
// ❌ Bad - Low contrast
className="text-black/40"  // 40% opacity fails WCAG AA
className="text-black/60"  // 60% likely fails

// ✅ Good - High contrast
className="text-black/80"  // 80% likely passes
className="text-black"     // 100% passes
```

**Alt Text Examples:**
```jsx
// ❌ Bad
<img src={photo.url} alt={photo.title} />
// Problem: photo.title might be undefined

// ✅ Good
<img 
  src={photo.url} 
  alt={photo.title || photo.description || 'Photo'} 
/>
```

---

## ✍️ Tone & Communication

### Ownership Framework

| Element | Owner |
|---------|-------|
| Overall voice | ChatGPT |
| Content within framework | Partner/Developer |
| Result | Seamless, feels like ChatGPT |

### Content Standards

**Do:**
- ✅ Keep content **concise and scannable**
- ✅ Ensure **context-driven responses** to user requests
- ✅ Prioritize **helpfulness and clarity**

**Don't:**
- ❌ Use spam, jargon, or promotional language
- ❌ Overwhelm with brand personality
- ❌ Include irrelevant messaging

---

### Proactivity Rules

#### ✅ Allowed (Contextual Nudges)
- Order ready notifications
- Delivery arrival alerts
- Status updates tied to user intent

#### ❌ Not Allowed (Unsolicited Promotions)
- Upsells without context
- Repeated re-engagement campaigns
- Irrelevant push notifications

#### Transparency Requirements
When using proactive features:
1. **Show why** the tool is resurfacing
2. **Show when** it will notify again
3. Provide **sufficient context** for nudge purpose
4. Ensure proactivity feels like **natural conversation continuation**, not interruption

---

## 📋 Quick Reference Checklist

### ✅ Do's

- [ ] Use system colors for backgrounds, text, dividers
- [ ] Inherit platform-native fonts (SF Pro, Roboto)
- [ ] Limit to 2 primary actions per inline card
- [ ] Keep carousel items between 3-8
- [ ] Provide alt text for all images
- [ ] Maintain WCAG AA contrast ratios (4.5:1 minimum)
- [ ] Design for conversation flow integration
- [ ] Keep content concise and scannable
- [ ] Support keyboard navigation
- [ ] Use system spacing and corner radius

### ❌ Don'ts

- [ ] Use custom fonts (including monospace)
- [ ] Override system background/text colors
- [ ] Include logo in widget content
- [ ] Create nested scrolling
- [ ] Use opacity below 70% for text
- [ ] Build long-form content experiences
- [ ] Display sensitive info in shareable cards
- [ ] Duplicate ChatGPT's native functions
- [ ] Use promotional language
- [ ] Send unsolicited notifications

---

## 🎯 FastApps Template Compliance

### Current Status

| Template | Compliant | Issues |
|----------|-----------|--------|
| **Default** | ⚠️ | Custom font (`monospace`), hardcoded colors |
| **List** | ⚠️ | Embedded logo, custom colors (`#F46C21`), low contrast |
| **Carousel** | ⚠️ | Custom button color (`#010304`), no item limit |
| **Albums** | ✅ | Minor: contrast ratios need review |

### Priority Fixes

1. **Remove embedded logo** from List template
2. **Replace custom colors** with system colors
3. **Fix contrast ratios** (60% → 80% opacity minimum)
4. **Add carousel item limit** (max 8)
5. **Remove custom fonts** or use system fonts

---

## 📚 Additional Resources

- [OpenAI Apps SDK Documentation](https://developers.openai.com/apps-sdk/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [ChatGPT Apps SDK Design Guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines/)

---

**Last Updated:** 2025-01-14  
**Version:** Based on OpenAI Apps SDK Design Guidelines (2025-03-26)
