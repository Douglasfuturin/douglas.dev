---
name: security-audit
description: Use when the user wants a security audit of an application built with Claude Code, Next.js, Supabase or Vercel. Pen-tester mode, ranked by severity.
---

# Security Audit Skill

Comprehensive security audit for vibe-coded applications. Pen tester mode. Designed for apps built with Claude Code, Vercel, Supabase, Next.js, and similar modern stacks.

## Trigger

Use when user says "security audit", "security check", "pentest", "vulnerability scan", "security review", "audit security", "check for vulnerabilities", "is this secure", or provides a URL and asks about security.

## Two Input Modes

### Mode 1: Codebase Audit (Direct Access)
When running inside a project directory with source code access.

### Mode 2: URL Audit (External Reconnaissance)
When given a URL to probe externally.

---

## Instructions

### Determine the Mode

1. If the user provides a URL, run **Mode 2: URL Audit**
2. If running in a codebase with source files, run **Mode 1: Codebase Audit**
3. If both a URL and codebase are available, run both modes and cross-reference findings

---

## Mode 1: Codebase Audit

Run the full 45-point checklist below against the source code. Use Grep, Glob, and Read to inspect files. For each item, report one of:
- **PASS** - No issues found
- **FAIL** - Vulnerability detected (include file path and line number)
- **WARN** - Potential issue, needs manual review
- **N/A** - Not applicable to this stack

### Phase 1: Secrets & Key Exposure (Items 1-8)

1. **Hardcoded API Keys** - Grep for API key patterns (`sk-`, `pk_`, `key-`, `AKIA`, `ghp_`, `glpat-`, `xoxb-`, `xoxp-`, bearer tokens). Check all source files, not just `.env`.
2. **Exposed .env Files** - Check if `.env`, `.env.local`, `.env.production` are committed to git or present in build output. Verify `.gitignore` includes all env files.
3. **Client-Side Secret Leakage** - Check if server-only secrets (database URLs, API secret keys, JWT secrets) are prefixed with `NEXT_PUBLIC_` or otherwise exposed to the browser bundle. Only public-safe values should have `NEXT_PUBLIC_` prefix.
4. **Secrets in Build Output** - Check `.next/`, `dist/`, `build/`, `.vercel/output/` for leaked secrets baked into client bundles.
5. **Git History Secrets** - Check for secrets that were committed and later removed but still exist in git history. Run `git log --all --diff-filter=D -- '*.env*'` and similar.
6. **Hardcoded Database Credentials** - Grep for connection strings, `postgres://`, `mysql://`, `mongodb://`, `redis://` with embedded credentials in source files.
7. **Private Keys in Repo** - Search for `.pem`, `.key`, `.p12`, `.pfx` files or `-----BEGIN (RSA |EC |)PRIVATE KEY-----` patterns.
8. **Third-Party Service Tokens** - Check for Stripe, Twilio, SendGrid, AWS, Firebase, OpenAI, Anthropic tokens hardcoded anywhere.

### Phase 2: Authentication & Authorization (Items 9-16)

9. **Missing Authentication on API Routes** - Check all API routes (`app/api/`, `pages/api/`) for session/auth verification. Every mutating endpoint MUST check auth.
10. **Broken Session Management** - Check JWT configuration (secret strength, expiration, algorithm). Look for `jwt.sign()` with weak secrets or no expiration.
11. **Missing CSRF Protection** - Check if state-changing operations validate CSRF tokens or use SameSite cookies.
12. **Insecure Cookie Configuration** - Check for cookies missing `httpOnly`, `secure`, `sameSite` flags. Search for `setCookie`, `cookies.set`, `Set-Cookie` headers.
13. **Auth Bypass via Direct API Access** - Check if middleware auth checks can be bypassed by hitting API routes directly. Verify middleware matcher patterns cover all protected routes.
14. **Missing Rate Limiting** - Check login, signup, password reset, and API endpoints for rate limiting implementation.
15. **Weak Password Requirements** - Check if signup/password change enforces minimum length, complexity. Look for password validation logic.
16. **OAuth/SSO Misconfiguration** - Check callback URL validation, state parameter usage, token storage for OAuth implementations.

### Phase 3: Supabase-Specific (Items 17-24)

17. **Row Level Security (RLS) Disabled** - Check Supabase migrations and SQL files for tables WITHOUT `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`. Every table with user data MUST have RLS enabled.
18. **Missing RLS Policies** - Check if RLS is enabled but no policies are defined (effectively blocks all access, or worse, was disabled to "fix" it).
19. **Overly Permissive RLS Policies** - Look for policies using `true` as the check expression, or `auth.role() = 'authenticated'` without filtering by `auth.uid()`.
20. **Service Role Key on Client** - Check if `SUPABASE_SERVICE_ROLE_KEY` or `supabase_service_role` is exposed to the client. This key bypasses RLS entirely. MUST only be used server-side.
21. **Anon Key Misuse** - Verify the anon key is only used for operations that should be publicly accessible. Check if it's used for admin operations.
22. **Direct Database URL Exposure** - Check if `DATABASE_URL` or direct Postgres connection strings are accessible client-side.
23. **Storage Bucket Permissions** - Check Supabase storage bucket policies. Look for public buckets that should be private.
24. **Missing Database Triggers/Constraints** - Check if critical data validation only exists client-side but not enforced at the database level.

### Phase 4: Server vs Client Boundary (Items 25-31)

25. **Server Actions Without Validation** - Check Next.js Server Actions (`"use server"`) for input validation. Every server action must validate and sanitize inputs independently of client-side validation.
26. **Sensitive Logic on Client** - Check for pricing calculations, permission checks, discount logic, or business rules running in client components (`"use client"`) that should be server-side.
27. **Client-Side Authorization Checks** - Look for authorization logic that only runs in the browser (checking roles/permissions in React components without server verification).
28. **Unprotected Server Actions** - Check if Server Actions verify the user's session/auth before performing operations.
29. **Data Overfetching** - Check API responses for returning more data than needed (full user objects with hashed passwords, internal IDs, metadata the client doesn't need).
30. **Missing Input Validation** - Check API routes and server actions for Zod/Yup schema validation on all inputs. Raw `req.body` usage without validation is a red flag.
31. **Prototype Pollution** - Check for deep merge utilities, `Object.assign` with user input, or spread operators on unvalidated objects.

### Phase 5: Infrastructure & Deployment (Items 32-38)

32. **Permissive CORS Configuration** - Check for `Access-Control-Allow-Origin: *` or overly broad origin allowlists. Check `next.config.js` headers and API route headers.
33. **Missing Security Headers** - Check for `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`, `Referrer-Policy`, `Permissions-Policy` headers in `next.config.js` or middleware.
34. **Open Redirects** - Check for redirect endpoints that accept user-controlled URLs without validation. Search for `redirect(`, `router.push(`, `window.location` with dynamic values.
35. **Vercel Environment Variables** - Check `vercel.json` for leaked secrets. Verify preview deployments don't expose production secrets.
36. **Exposed Debug/Dev Endpoints** - Check for `/api/debug`, `/api/test`, `/api/seed`, GraphQL Playground, or Prisma Studio left accessible in production.
37. **Missing Error Handling** - Check if error responses leak stack traces, database schema, or internal paths. Look for raw error messages sent to clients.
38. **Insecure Dependencies** - Run `npm audit` or `pnpm audit`. Flag critical/high severity vulnerabilities. Check for known vulnerable package versions.

### Phase 6: Injection & Data Safety (Items 39-45)

39. **SQL Injection** - Check for raw SQL queries with string interpolation/concatenation. Verify parameterized queries or ORM usage. Check Supabase `.rpc()` calls with user input.
40. **XSS (Cross-Site Scripting)** - Check for `dangerouslySetInnerHTML`, unescaped user content rendering, `eval()`, `innerHTML` assignments with user data.
41. **Path Traversal** - Check file serving endpoints for `../` traversal. Look for `fs.readFile`, `fs.createReadStream` with user-controlled paths.
42. **SSRF (Server-Side Request Forgery)** - Check if any endpoint fetches URLs provided by users without validating the destination (internal network access, cloud metadata endpoints).
43. **Insecure File Upload** - Check file upload handlers for type validation, size limits, and storage location. Verify uploaded files aren't served with executable content types.
44. **Mass Assignment** - Check if API routes directly pass request body to database create/update operations without whitelisting allowed fields.
45. **Logging Sensitive Data** - Check if `console.log`, logging libraries, or error tracking (Sentry) capture passwords, tokens, credit card numbers, or PII.

### Output Format for Codebase Audit

After running all 45 checks, produce:

```
# Security Audit Report

## Summary
- Critical: X issues
- High: X issues
- Medium: X issues
- Low: X issues
- Passed: X checks
- N/A: X checks

## Critical Issues (Fix Immediately)
[List each with file path, line number, and specific fix]

## High Issues (Fix Before Launch)
[List each with file path, line number, and specific fix]

## Medium Issues (Fix Soon)
[List each with details]

## Low Issues (Best Practice)
[List each with details]

## Passed Checks
[List checks that passed]

## Recommended Fix Plan

### Step 1: [Most critical fix]
- Files to modify: [list]
- What to do: [specific instructions]

### Step 2: [Next critical fix]
...
[Continue for all issues found]
```

---

## Mode 2: URL Audit (External Reconnaissance)

When given a URL, perform external security reconnaissance. Use WebFetch, Bash (for curl commands), and web tools to probe the target.

### External Checks to Perform:

1. **Response Headers Analysis** - Fetch the URL and analyze all security headers (CSP, HSTS, X-Frame-Options, etc.)
2. **Exposed Source Maps** - Try fetching `.js.map` files linked from JavaScript bundles
3. **Common Sensitive Paths** - Probe for:
   - `/.env`, `/.env.local`, `/.env.production`
   - `/.git/config`, `/.git/HEAD`
   - `/api/debug`, `/api/test`, `/api/health`
   - `/graphql` (with introspection query)
   - `/_next/data/` directory listing
   - `/sitemap.xml`, `/robots.txt` (for hidden paths)
   - `/.well-known/` endpoints
   - `/wp-admin`, `/admin`, `/dashboard` (without auth redirect)
4. **CORS Testing** - Send requests with various Origin headers to check CORS policy
5. **Cookie Analysis** - Check cookie flags (Secure, HttpOnly, SameSite)
6. **SSL/TLS Check** - Verify certificate validity and configuration
7. **Technology Fingerprinting** - Identify framework, hosting platform, and services from headers and HTML
8. **Open API Endpoints** - Check if API routes respond without authentication
9. **Error Response Analysis** - Send malformed requests and check if error messages leak information
10. **Client Bundle Analysis** - Fetch JavaScript bundles and search for:
    - Hardcoded API keys or tokens
    - Internal API endpoint URLs
    - Debug/development code left in production
    - Source map references

### Output Format for URL Audit

After running all external checks, produce:

```
# External Security Audit: [URL]

## Summary
- Critical: X issues
- High: X issues
- Medium: X issues
- Low: X issues
- Info: X findings

## Findings
[List each finding with severity and evidence]

## Technology Stack Detected
- Framework: [detected]
- Hosting: [detected]
- Services: [detected]

---

## Fix Prompt for Claude Code

Copy and paste the following prompt into Claude Code while in your project directory:

> I need you to fix the following security vulnerabilities found during an external audit:
>
> **Critical:**
> 1. [Issue description with specific fix instructions]
>
> **High:**
> 1. [Issue description with specific fix instructions]
>
> **Medium:**
> 1. [Issue description with specific fix instructions]
>
> **Low:**
> 1. [Issue description with specific fix instructions]
>
> For each fix:
> - Show me the current vulnerable code
> - Apply the fix
> - Explain what the vulnerability was and why the fix works
>
> Start with Critical issues first, then work down.
```

---

## Severity Classification

- **Critical**: Actively exploitable, data breach risk, secrets exposed publicly (hardcoded API keys, RLS disabled, auth bypass)
- **High**: Exploitable with some effort, significant security gap (missing auth on routes, SSRF, SQL injection)
- **Medium**: Defense-in-depth gaps, could be chained with other issues (missing headers, permissive CORS, weak session config)
- **Low**: Best practices not followed, minimal direct risk (missing rate limiting, verbose errors in staging)

## Important Notes

- This is an authorized security review. Only test targets you have permission to audit.
- For URL mode, only perform non-destructive reconnaissance. Do not attempt exploitation, DoS, or active attacks.
- Flag but do not exploit any vulnerabilities found.
- When in doubt about severity, err on the side of higher severity.
- Always check for the "vibe code" classics: the developer said "make it work" and the AI happily obliged without security considerations.
