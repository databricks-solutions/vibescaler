---
id: DESIGN_SYSTEM_SPEC
title: Design System Specification
---

import SpecCoverage from '@site/src/components/SpecCoverage';

# Design System Specification

## Overview

This specification defines the visual design system for the Human Evaluation Workshop, including the color palette, typography, component styling, and accessibility requirements. The system uses Tailwind CSS with a Material Design 3-style purple theme.

**Source of truth**: the shipped CSS variables in `client/src/index.css` (consumed via `client/tailwind.config.js`). Token values below quote that file's HSL triplets; hex values are the rendered equivalents. If this document and `index.css` ever disagree, `index.css` wins — update this document, not the CSS.

## Color System

### Primary Palette (Deep Purple)

The primary color is a rich deep purple — `--primary: 262 52% 47%` (`#673AB6`).

> Historical note: earlier revisions of this spec pinned Indigo-500 (`#6366F1`).
> That color never shipped; the product has always rendered the `262`-hue purple
> defined in `client/src/index.css`. (Some stale comments inside `index.css`
> still mention `#6366F1` — the HSL values are authoritative.)

#### Light Mode

| Token | HSL (CSS variable) | Hex | Usage |
|-------|--------------------|-----|-------|
| `primary` | `262 52% 47%` | `#673AB6` | Primary buttons, links, accents |
| `primary-foreground` | `0 0% 100%` | `#FFFFFF` | Text on primary background |
| `primary-container` | `262 90% 95%` | `#EFE7FE` | Subtle backgrounds |
| `primary-container-foreground` | `262 52% 35%` | `#4D2B88` | Text on container background |

#### Dark Mode (roadmap — CSS variables ship, but no toggle applies them; see Dark Mode section)

| Token | HSL (CSS variable) | Hex | Usage |
|-------|--------------------|-----|-------|
| `primary` | `262 70% 75%` | `#B393EC` | Primary buttons, links (lighter for dark bg) |
| `primary-foreground` | `262 52% 15%` | `#21123A` | Text on primary background |
| `primary-container` | `262 47% 30%` | `#432970` | Subtle backgrounds |
| `primary-container-foreground` | `262 90% 88%` | `#D9C5FC` | Text on container background |

### Secondary Palette (Badges & Subtle UI)

#### Light Mode

| Token | HSL (CSS variable) | Hex | Usage |
|-------|--------------------|-----|-------|
| `secondary` | `270 60% 96%` | `#F5EFFB` | Badge backgrounds |
| `secondary-foreground` | `262 52% 47%` | `#673AB6` | Badge text |

#### Dark Mode (roadmap)

| Token | HSL (CSS variable) | Hex | Usage |
|-------|--------------------|-----|-------|
| `secondary` | `270 20% 25%` | `#40334C` | Badge backgrounds |
| `secondary-foreground` | `262 70% 75%` | `#B393EC` | Badge text |

### Extended Purple Scale

The `purple-*` Tailwind classes do NOT use Tailwind's default palette — `client/tailwind.config.js` remaps them to the `--purple-*` CSS variables in `index.css`, keeping the whole scale on the primary 262 hue:

```
purple-50   262 90% 98%   #F9F5FE   Lightest (backgrounds, hover states)
purple-100  262 90% 95%   #EFE7FE   Very light (badges, containers)
purple-200  262 83% 88%   #DAC7FA   Light (borders)
purple-300  262 74% 78%   #BC9DF0   Soft
purple-400  262 63% 65%   #976EDE   Medium-light
purple-500  262 52% 47%   #673AB6   Main (matches primary)
purple-600  262 52% 40%   #58319B   Medium-dark (hover states)
purple-700  262 52% 35%   #4D2B88   Dark (text)
purple-800  262 45% 28%   #3F2768   Darker (emphasis)
purple-900  262 40% 22%   #32224F   Darkest (high contrast)
```

### Semantic Colors

| Token | Light (HSL / hex) | Dark (HSL / hex, roadmap) | Usage |
|-------|-------------------|---------------------------|-------|
| `background` | `0 0% 99%` / `#FCFCFC` | `0 0% 6%` / `#0F0F0F` | Page background |
| `foreground` | `0 0% 10%` / `#1A1A1A` | `0 0% 90%` / `#E6E6E6` | Default text |
| `muted` | `270 12% 93%` / `#EDEBEF` | `270 11% 20%` / `#332D39` | Muted backgrounds |
| `muted-foreground` | `264 7% 29%` / `#49454F` | `270 11% 69%` / `#B0A7B9` | Muted text |
| `destructive` | `0 72% 51%` / `#DC2828` | `0 100% 84%` / `#FFADAD` | Error states |
| `border` | `270 6% 47%` / `#78717F` | `270 11% 40%` / `#665B71` | Borders |

`index.css` also ships `tertiary`, `success`, `warning`, and `info` palettes (with `*-container` variants) following the same Material 3 tonal pattern.

## Component Styling

### Buttons

**Primary Button**:
```tsx
<Button>Add User</Button>
// Uses primary color automatically
```

**Secondary Button**:
```tsx
<Button variant="secondary">Cancel</Button>
// Uses secondary color scheme
```

**Destructive Button**:
```tsx
<Button variant="destructive">Delete</Button>
// Uses destructive color
```

**Outline Button**:
```tsx
<Button variant="outline">View Details</Button>
// Transparent with border
```

### Badges

**Default Badge**:
```tsx
<Badge>Active</Badge>
// Primary purple, prominent
```

**Secondary Badge**:
```tsx
<Badge variant="secondary">2 Participants</Badge>
// Subtle purple background
```

**Custom Badge**:
```tsx
<Badge className="bg-purple-100 text-purple-800 border-purple-200">
  SME
</Badge>
```

### Cards

```tsx
<Card>
  <CardHeader>
    <CardTitle>Workshop Settings</CardTitle>
    <CardDescription>Configure your workshop</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>
```

### Form Elements

**Input**:
```tsx
<Input placeholder="Enter name" />
// Focus ring uses primary color
```

**Select**:
```tsx
<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select option" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="a">Option A</SelectItem>
  </SelectContent>
</Select>
```

## Typography

### Font Stack

```css
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
  "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

### Scale

| Class | Size | Usage |
|-------|------|-------|
| `text-xs` | 0.75rem | Labels, captions |
| `text-sm` | 0.875rem | Secondary text |
| `text-base` | 1rem | Body text |
| `text-lg` | 1.125rem | Subheadings |
| `text-xl` | 1.25rem | Section headers |
| `text-2xl` | 1.5rem | Page titles |

### Weights

| Class | Weight | Usage |
|-------|--------|-------|
| `font-normal` | 400 | Body text |
| `font-medium` | 500 | Emphasized text |
| `font-semibold` | 600 | Subheadings |
| `font-bold` | 700 | Headings |

## Spacing

Consistent spacing scale (rem-based):

| Class | Value | Usage |
|-------|-------|-------|
| `p-1` / `m-1` | 0.25rem | Tight spacing |
| `p-2` / `m-2` | 0.5rem | Compact |
| `p-3` / `m-3` | 0.75rem | Default small |
| `p-4` / `m-4` | 1rem | Default |
| `p-6` / `m-6` | 1.5rem | Comfortable |
| `p-8` / `m-8` | 2rem | Spacious |

## Accessibility

### Color Contrast

All text meets WCAG AA contrast ratios:
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

### Focus States

All interactive elements have visible focus indicators:

```css
.focus-visible:ring-2
.focus-visible:ring-primary
.focus-visible:ring-offset-2
```

### Color Independence

Never rely solely on color to convey information:
- Icons paired with text labels
- Status indicated by text + color
- Error messages use both red and icon

### Keyboard Navigation

- All interactive elements focusable via Tab
- Logical focus order
- Escape closes modals/dropdowns
- Enter/Space activate buttons

## Dark Mode (roadmap)

**Status: not shipped.** Tailwind is configured with `darkMode: ['class']` and `index.css` ships a full `.dark` variable block, but **no UI toggle or theme detection applies the `dark` class** — the app always renders in light mode. Dark mode criteria are roadmap until a toggle (or `prefers-color-scheme` wiring) exists.

### Planned Implementation

Theme controlled via `class` strategy on `<html>`:

```tsx
// Toggle dark mode (no shipped UI invokes this yet)
document.documentElement.classList.toggle('dark');
```

### CSS Variables (shipped in `client/src/index.css`)

```css
/* Light mode (default) */
:root {
  --primary: 262 52% 47%;      /* Deep purple #673AB6 */
  --background: 0 0% 99%;
  --foreground: 0 0% 10%;
}

/* Dark mode (defined but currently unreachable) */
.dark {
  --primary: 262 70% 75%;      /* Lighter purple #B393EC */
  --background: 0 0% 6%;
  --foreground: 0 0% 90%;
}
```

### Component Adaptation

Components use semantic tokens, so they will adapt automatically once the `dark` class can be applied:

```tsx
// Uses dark mode colors when .dark class present
<Card className="bg-background text-foreground">
  {/* Content */}
</Card>
```

## Class Utilities

All components compose Tailwind classes through the `cn()` utility (`client/src/lib/utils.ts`, clsx + tailwind-merge). It merges conditional class inputs (strings, arrays, objects) and resolves conflicting Tailwind utilities with later-value-wins semantics:

```typescript
cn('p-2', 'p-4')                          // → 'p-4'
cn('bg-red-500', condition && 'bg-blue-500')  // conflict resolved, falsy filtered
```

## File Locations

| File | Purpose |
|------|---------|
| `client/src/index.css` | CSS variables, base styles |
| `client/tailwind.config.js` | Tailwind theme configuration |
| `client/src/lib/utils.ts` | `cn()` class-merging utility |
| `client/src/components/ui/` | UI component library |

## Migration Guide

### From Hardcoded Colors

**Before**:
```tsx
className="bg-purple-600 hover:bg-purple-700"
```

**After**:
```tsx
<Button>Action</Button>
// Or for custom styling:
className="bg-primary hover:bg-primary/90"
```

### Using Theme Colors

```tsx
// Use semantic tokens
className="bg-primary text-primary-foreground"
className="bg-muted text-muted-foreground"
className="border-border"

// Or Tailwind purple scale for custom needs
className="bg-purple-500 text-purple-50"
```

## Success Criteria

<SpecCoverage spec="DESIGN_SYSTEM_SPEC" />

- [ ] Primary purple consistent across all components
- [ ] `cn()` utility merges class names and resolves Tailwind conflicts (later value wins)
- [ ] All text meets WCAG AA contrast
- [ ] Focus indicators visible
- [ ] No hardcoded colors in components
- [ ] Badges use secondary color scheme
- [ ] Buttons use appropriate variants
- [ ] Dark mode fully functional (roadmap)
