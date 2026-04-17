# Frontend Copilot Integration Guide

## Quick Start

### 1. Update CopilotPanel.tsx

Add initialization logic to call the backend when the component mounts:

```typescript
import { useEffect, useState } from 'react';

export function CopilotPanel() {
  const [copilotReady, setCopilotReady] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [initError, setInitError] = useState<string | null>(null);

  // Initialize copilot on component mount
  useEffect(() => {
    const initializeCopilot = async () => {
      try {
        setIsInitializing(true);
        setInitError(null);
        
        const response = await fetch(
          `${process.env.REACT_APP_API_URL}/initialize-copilot`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          }
        );
        
        if (!response.ok) {
          throw new Error(`Initialization failed: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Copilot initialized:', data);
        setCopilotReady(true);
      } catch (error) {
        console.error('❌ Copilot initialization failed:', error);
        setInitError(error instanceof Error ? error.message : 'Unknown error');
        // Still allow questions even if initialization fails
        setCopilotReady(true);
      } finally {
        setIsInitializing(false);
      }
    };
    
    initializeCopilot();
  }, []);

  // Show loading state during initialization
  if (isInitializing) {
    return (
      <div className="copilot-initializing">
        <div className="spinner" />
        <p>🔄 Initializing Copilot with dataset analysis...</p>
        <p className="subtitle">This happens once when you load the dashboard</p>
      </div>
    );
  }

  // Show error if initialization failed (but still allow questions)
  if (initError) {
    return (
      <div className="copilot-warning">
        <p>⚠️ Copilot initialization warning: {initError}</p>
        <p>Questions will still work, but may be slower</p>
        <CopilotChat />
      </div>
    );
  }

  // Show ready state
  return (
    <div className="copilot-ready">
      <div className="copilot-header">
        <h3>🤖 Planning Intelligence Copilot</h3>
        <span className="status-badge">Ready</span>
      </div>
      <CopilotChat />
    </div>
  );
}

// Existing chat component (no changes needed)
function CopilotChat() {
  // ... existing implementation
}
```

### 2. Update CSS for Loading State

```css
.copilot-initializing {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  min-height: 200px;
}

.copilot-initializing .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.copilot-initializing p {
  margin: 8px 0;
  font-size: 14px;
}

.copilot-initializing .subtitle {
  font-size: 12px;
  opacity: 0.8;
}

.copilot-warning {
  padding: 16px;
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  margin-bottom: 16px;
}

.copilot-warning p {
  margin: 4px 0;
  color: #856404;
}

.copilot-ready {
  border-radius: 8px;
  overflow: hidden;
}

.copilot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.copilot-header h3 {
  margin: 0;
  font-size: 16px;
}

.status-badge {
  background-color: rgba(255, 255, 255, 0.3);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
```

### 3. Update DashboardPage.tsx (if using separate component)

```typescript
import { CopilotPanel } from './components/CopilotPanel';

export function DashboardPage() {
  return (
    <div className="dashboard">
      <div className="dashboard-main">
        {/* Existing dashboard content */}
      </div>
      
      <div className="dashboard-copilot">
        <CopilotPanel />
      </div>
    </div>
  );
}
```

## Timeline

### User Experience Flow

1. **User opens dashboard** (0s)
   - Dashboard loads
   - Copilot panel shows "Initializing..." spinner

2. **Backend initializes** (0-60s)
   - LLM reads all 10,000 records
   - LLM generates comprehensive analysis
   - Analysis is cached

3. **Copilot ready** (60s)
   - Spinner disappears
   - "Ready" badge appears
   - User can start asking questions

4. **User asks question** (60s+)
   - Question sent to backend
   - Backend uses cached analysis
   - Response in 1-3 seconds

## Error Handling

The implementation gracefully handles errors:
- If initialization fails, copilot still works (just slower)
- Warning message shown to user
- Questions can still be asked
- No blocking errors

## Performance Metrics

### Before (Without Caching)
- First question: 10-30 seconds
- Subsequent questions: 10-30 seconds each
- Total for 5 questions: 50-150 seconds

### After (With Caching)
- Initialization: 30-60 seconds (one-time)
- First question: 1-3 seconds
- Subsequent questions: 1-3 seconds each
- Total for 5 questions: 35-75 seconds (including init)

## Testing

### Test in Browser Console
```javascript
// Check if copilot is ready
fetch('http://localhost:7071/api/initialize-copilot', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
})
.then(r => r.json())
.then(data => console.log('Copilot initialized:', data))
.catch(e => console.error('Error:', e));
```

### Test Question
```javascript
fetch('http://localhost:7071/api/explain', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'What is the planning health?' })
})
.then(r => r.json())
.then(data => console.log('Answer:', data.answer))
.catch(e => console.error('Error:', e));
```

## Status
✅ Ready for frontend integration
