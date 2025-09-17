# Clean Frontend Fixes

This document outlines the fixes that will be applied to the frontend application. These fixes have been reviewed and are not expected to have any conflicts with each other.

## 1. `ETradeTradeWidget.tsx`

*   **Action:** Wrap the `checkAuthStatus` function in a `useCallback` hook and import `useCallback` from `react`.
*   **Reason:** This will resolve the `Block-scoped variable 'checkAuthStatus' used before its declaration` error and the related `useEffect` dependency warning.

## 2. `ETradeWidget.tsx`

*   **Action:** Wrap the `checkAuthStatus` function in a `useCallback` hook, import `useCallback` from `react`, and remove the `use_sandbox` parameter from the `initiateOAuth` function.
*   **Reason:** This will resolve the `Block-scoped variable 'checkAuthStatus' used before its declaration` error, the `useEffect` dependency warning, and the `Cannot find name 'useSandbox'` error.

## 3. `PortfolioWidget.tsx`

*   **Action:** Remove the unused `Position` import.
*   **Reason:** This will clean up the code and eliminate the unused variable warning.

## 4. `WatchlistWidget.tsx`

*   **Action:** Change the `color` prop of the `LinearProgress` component from `"default"` to `"primary"` in the `getRSIColor` function.
*   **Reason:** This will fix the `Type ... is not assignable to type ...` error.

## 5. Unused Variables

*   **Action:** Remove all remaining unused variables from all files.
*   **Reason:** This will clean up the code and eliminate the remaining ESLint warnings.
