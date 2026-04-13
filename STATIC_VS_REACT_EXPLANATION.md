# Static vs React - What's the Difference?

## Short Answer
**It's still React**, but deployed as **static files**. The React app is "compiled" into static HTML/JS/CSS files.

## How It Works

### Development (Local)
```
npm start → React dev server runs → Hot reload works → Dynamic
```

### Production (Blob Storage)
```
npm run build → Creates static files → Uploads to blob → Served as-is
```

## What Happens During `npm run build`

React compiles your code into:
- `index.html` - Main HTML file
- `static/js/*.js` - Compiled JavaScript (React code bundled)
- `static/css/*.css` - Compiled CSS
- `static/media/*` - Images, fonts, etc.

These are **static files** - they don't change unless you rebuild.

## Is It Still React?

**YES!** The React code is still there, just compiled:

```
Your React Code (TypeScript/JSX)
         ↓
    npm run build
         ↓
Static Files (HTML/JS/CSS)
         ↓
Browser downloads & runs
         ↓
React app runs in browser (client-side)
```

## Key Points

| Aspect | Local Dev | Blob Storage |
|--------|-----------|--------------|
| **Server** | React dev server | Static file server (blob) |
| **React** | Running on server | Running in browser |
| **Hot reload** | ✅ Yes | ❌ No |
| **Build needed** | ❌ No | ✅ Yes (npm run build) |
| **File changes** | Instant | Requires rebuild + redeploy |
| **Cost** | Free (local) | Cheap (blob storage) |

## Example Flow

1. **You write React code** in `frontend/src/pages/DashboardPage.tsx`
2. **You run `npm run build`** → Creates `build/` folder with static files
3. **You upload to blob** → `az storage blob upload-batch`
4. **User visits URL** → Browser downloads `index.html`
5. **Browser runs React** → App loads and works normally
6. **React makes API calls** → Calls backend at `https://pi-planning-intelligence.azurewebsites.net/api`

## Why Use Blob Storage?

✅ **Cheaper** - No server costs  
✅ **Faster** - CDN-ready  
✅ **Simpler** - No server to manage  
✅ **Scalable** - Handles traffic automatically  

## When to Use App Service Instead?

Use App Service (with `server.js`) if you need:
- Server-side rendering
- Environment variables at runtime
- Dynamic content generation
- Backend logic in Node.js

## Your Setup

You're using **Blob Storage** (static deployment):
- Frontend: `https://planningdatapi.z5.web.core.windows.net/` (static files)
- Backend: `https://pi-planning-intelligence.azurewebsites.net/api` (API)
- React runs in browser, calls backend API

This is the **correct and recommended approach** for your use case.
