# SPA Routing 404 Error & Copilot Prompts

## Part 1: What Does "404 on Refresh" Mean?

### The Problem

When you deploy a React app to blob storage and refresh the page on a route like `/dashboard`, you get a 404 error.

**Why?**

```
User visits: https://planningdatapi.z5.web.core.windows.net/dashboard
                                                                    ↓
Blob storage looks for: /dashboard (file)
                        ❌ File doesn't exist
                        → Returns 404
```

React routes like `/dashboard` don't exist as actual files. They're handled by React in the browser.

### The Solution

Tell blob storage: "If file not found, serve `index.html` instead"

```powershell
az storage blob service-properties update \
  --account-name planningdatapi \
  --static-website \
  --index-document index.html \
  --404-document index.html
```

**What this does:**

```
User visits: https://planningdatapi.z5.web.core.windows.net/dashboard
                                                                    ↓
Blob storage looks for: /dashboard (file)
                        ❌ File doesn't exist
                        ✅ Serves index.html instead
                        ↓
React loads and handles routing
                        ↓
React shows /dashboard page
```

### Why This Works

1. `index.html` is the main React app
2. React has routing logic built-in
3. React reads the URL and shows the right page
4. User sees `/dashboard` page correctly

### When You Need This

- ✅ User refreshes on `/dashboard` → Need this fix
- ✅ User bookmarks `/settings` → Need this fix
- ✅ User shares link to `/reports` → Need this fix
- ❌ User clicks links in app → Works without this (React handles it)

### How to Apply

Run this command on your org laptop:

```powershell
az storage blob service-properties update `
  --account-name planningdatapi `
  --static-website `
  --index-document index.html `
  --404-document index.html
```

Then test:
1. Visit: `https://planningdatapi.z5.web.core.windows.net/`
2. Click around (works)
3. Refresh page (should still work)
4. Manually visit: `https://planningdatapi.z5.web.core.windows.net/dashboard`
5. Refresh (should work now)

---

## Part 2: Can You Ask Prompts in Copilot?

### YES - Absolutely!

You can ask Copilot anything about your code, deployment, or system.

### Examples of Good Prompts

**Technical Questions:**
- "Why is my backend returning 503?"
- "How do I fix CORS errors?"
- "What's the difference between blob storage and app service?"
- "How do I deploy to Azure?"

**Code Questions:**
- "How do I call the backend API from React?"
- "What's wrong with this TypeScript code?"
- "How do I add error handling?"

**Debugging:**
- "The dashboard isn't loading data, what could be wrong?"
- "I'm getting a 404 error, how do I fix it?"
- "The frontend can't connect to the backend"

**Architecture:**
- "Should I use blob storage or app service?"
- "How do I set up CORS?"
- "What's the best way to structure my API?"

### Examples of Prompts You Just Asked

✅ "does it become static or react if we use like this?"  
✅ "can it connect to backend execution if we do so?"  
✅ "what does 404 on refresh mean?"  
✅ "can I not ask prompts in ask copilot?"  

All valid! Keep asking.

### How to Ask Effectively

**Good:**
- "I'm getting a 503 error on my app service. What could cause this?"
- "How do I deploy the frontend to blob storage?"
- "The backend isn't responding. How do I debug?"

**Also Good:**
- "What's SPA routing?"
- "Explain CORS"
- "How does React work?"

**Vague (but still okay):**
- "Help me with deployment"
- "Something's broken"
- "How do I fix this?"

I'll ask clarifying questions if needed.

### What Copilot Can Do

✅ Answer technical questions  
✅ Explain concepts  
✅ Help debug issues  
✅ Review code  
✅ Suggest solutions  
✅ Create documentation  
✅ Write code  
✅ Explain errors  

### What Copilot Cannot Do

❌ Access your actual Azure account (only you can)  
❌ Run commands for you (you run them)  
❌ See your screen (you describe it)  
❌ Access private data (you share what's needed)  

---

## Summary

**SPA Routing Fix:**
```powershell
az storage blob service-properties update --account-name planningdatapi --static-website --index-document index.html --404-document index.html
```

**Copilot Prompts:**
Yes, ask anything! I'm here to help with:
- Technical questions
- Debugging
- Architecture decisions
- Code reviews
- Deployment help
- Explanations
- And more

Just ask naturally. No special format needed.
