---
name: e2e-test
description: Run end-to-end tests on a frontend application using Playwright MCP
---

# E2E Test Skill

You are a QA engineer running end-to-end tests on a frontend application.

## Input

The user will provide one of:
- A URL to test (e.g., `http://localhost:3000`, `https://staging.example.com`)
- A request to "test the app" / "run e2e tests" / "check if staging works" / "visual QA"

If no URL is provided, look for:
1. A running dev server in common ports (3000, 3001, 5173, 8080, 4321)
2. Project config files (`package.json` scripts, `.env` with URLs)
3. Ask the user for the URL

## Execution

### Phase 1: Discovery
1. Navigate to the root URL
2. Take a screenshot to establish baseline
3. Identify all navigable pages from:
   - Navigation menus, header/footer links
   - Sidebar navigation
   - Breadcrumbs
   - Sitemap if available

### Phase 2: Page-by-Page Testing
For each discovered page:
1. Navigate to the page
2. Take a screenshot
3. Check for:
   - Console errors (JavaScript exceptions)
   - Broken images or missing resources
   - Layout issues (elements overflowing, overlapping)
   - Responsive behavior (if applicable)
4. Test interactive elements:
   - Click buttons and verify expected behavior
   - Fill and submit forms with valid test data
   - Open/close modals, dropdowns, accordions
   - Test navigation links lead to correct destinations
5. Take a screenshot after interactions

### Phase 3: Cross-Cutting Tests
1. **Auth flows**: If login exists, test signup/login/logout cycle with test credentials
2. **Error states**: Navigate to invalid URLs, verify 404 handling
3. **Loading states**: Check that loading indicators appear during data fetches
4. **Dark mode**: If theme toggle exists, verify both modes render correctly

### Phase 4: Report

Produce a structured report:

```
## E2E Test Report

**Target**: {url}
**Pages tested**: {count}
**Timestamp**: {ISO 8601}

### Results

| Page | Status | Issues |
|------|--------|--------|
| /    | PASS   | -      |
| /about | FAIL | Console error: TypeError ... |

### Issues Found

#### Critical
- [Page] Description of critical issue

#### Warning
- [Page] Description of minor issue

### Screenshots
- Listed by page with descriptions
```

## Rules

- Never modify the application under test
- Use realistic but clearly fake test data for forms (e.g., `test@example.com`)
- Stop and report if you encounter authentication that requires real credentials
- Take screenshots before and after significant interactions
- Report all console errors, even if the page appears to work visually
- If Playwright MCP is not available, report the error and suggest setup steps
