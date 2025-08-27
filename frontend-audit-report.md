# Frontend Code Audit Report & Action Items

This document contains findings from a comprehensive frontend code audit and actionable tasks to improve code quality, performance, and maintainability.

## Quick Wins (Immediate - < 30 minutes)

All done!

## Short-term Improvements (< 2 hours)

### 5. Extract Inline Event Handlers

**Files:** `src/App.tsx`

- Move all inline `onMouseOver`/`onMouseOut` handlers to separate functions or CSS :hover
- Affected lines: 192-198, 237-246, 266-275, 294-303, 334-345
- This will prevent unnecessary re-renders

### 6. Create Reusable Button Component

**Files:** `src/components/Button.tsx` (new file)

- Extract repeated button patterns from `App.tsx`, `UsernameEditModal.tsx`, `AuthCallback.tsx`
- Create variants: primary, secondary, danger
- Include hover states and loading states

### 7. Extract Auth Logic to Custom Hook

**Files:** `src/hooks/useAuth.ts` (new file)

- Move auth state logic from `App.tsx` (lines 35-54) to a reusable `useAuth` hook
- Include user state, loading state, and auth methods

### 8. Consolidate Environment Variables

**Files:** Multiple files use different patterns for BACKEND_URL/WEBSOCKET_URL

- Create `src/config/environment.ts` to centralize environment variable access
- Update imports in: `GameView.tsx`, `gameService.ts`, `cookieAuth.ts`, `AuthCallback.tsx`

## Medium-term Refactoring (< 1 day)

### 9. Convert Inline Styles to CSS Modules

**Priority files to convert:**

- `src/App.tsx` - Landing page styles (lines 116-354)
- `src/components/UsernameEditModal.tsx` - Modal styles (lines 52-219)
- `src/components/AuthCallback.tsx` - Auth callback styles (lines 74-168)

Create corresponding CSS module files and replace inline styles.

### 10. Create Reusable Modal Component

**Files:** `src/components/Modal.tsx` (new file)

- Extract common modal patterns from `UsernameEditModal.tsx`
- Support backdrop click, keyboard events, and custom content
- Make `UsernameEditModal` use the base `Modal` component

### 11. Simplify Complex Conditional Rendering

**Files:** `src/components/GameView.tsx`

- Extract mobile and desktop layouts into separate components (lines 220-341)
- Create `MobileGameLayout.tsx` and `DesktopGameLayout.tsx`

### 12. Extract Utility Functions

**Files:** `src/utils/` (new directory)

- Move timer formatting logic from `Timer.tsx` (lines 72-82) to `src/utils/timeUtils.ts`
- Create other utility functions as needed

## Performance Optimizations

### 13. Add React.memo Where Appropriate

**Files:** Consider memoizing these components:

- `Timer.tsx` - re-renders frequently
- `Tile.tsx` - many instances on board
- `Piece.tsx` - many instances on board

### 14. Optimize Board Rendering

**Files:** `src/components/Board.tsx`

- Fix key generation (lines 231-232) to use stable keys
- Consider virtualization for large boards if performance becomes an issue

## Code Quality Improvements

### 15. Improve Error Boundaries

- Add error boundaries around major components
- Improve error handling in async operations

### 16. Add TypeScript Strict Mode Compliance

- Review and fix any `any` types
- Add proper type definitions where missing

## Testing Considerations

### 17. Remove Unused Test Files

**Files:** `src/setupTests.ts` and `src/reportWebVitals.ts`

- Remove if not actively used in testing pipeline
- Update `src/index.tsx` to remove `reportWebVitals` import if removed

## Instructions for Implementation

To implement these changes with Claude:

1. **For Quick Wins:** "Implement items 1-4 from the frontend audit report"
2. **For Short-term:** "Implement items 5-8 from the frontend audit report"
3. **For Medium-term:** "Implement items 9-12 from the frontend audit report"

Each section can be tackled independently, with Quick Wins providing immediate benefits and later sections providing more substantial improvements.

## Impact Assessment

- **Quick Wins:** Immediate performance improvements, reduced bundle size
- **Short-term:** Better maintainability, reduced code duplication
- **Medium-term:** Improved developer experience, better separation of concerns
- **Performance:** Reduced re-renders, better React optimization

This audit found the codebase to be generally well-structured but suffering from common React anti-patterns around inline styles and event handlers that impact performance.
