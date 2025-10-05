# Troubleshooting Guide - AI Copilot Backend

## Overview
This guide helps diagnose and fix issues with the POST /api/ask endpoint and frontend-backend communication.

## Quick Diagnostics

### Run Automated Tests
```bash
cd ai-copilot-assistant-4345-4354/fastapi_backend
./test_diagnostics.sh
```

This will verify:
- ✓ Health endpoint responds correctly
- ✓ CORS headers are present for localhost:3000 and 127.0.0.1:3000
- ✓ Empty question validation returns proper 400 error
- ✓ Valid questions return 200 with answer and model
- ✓ Malformed JSON returns proper validation errors
- ✓ CORS headers are included in all responses

### Manual Tests

#### Test Health Endpoint
```bash
curl -i http://localhost:3001/api/health
```
Expected: `200 OK` with `{"ok":true}`

#### Test POST /api/ask
```bash
curl -i -X POST http://localhost:3001/api/ask \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{"question":"What is FastAPI?"}'
```
Expected: `200 OK` with `{"answer":"...","model":"gemini-2.5-flash"}`

#### Test CORS Preflight
```bash
curl -i -X OPTIONS http://localhost:3001/api/ask \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```
Expected: `200 OK` with CORS headers including `access-control-allow-origin: http://localhost:3000`

## Common Issues and Fixes

### Issue 1: Generic "Network Error" in Frontend

**Symptoms:**
- Frontend shows "Network Error" without details
- Browser console shows connection errors or generic axios errors

**Root Causes:**
1. Backend not running
2. Wrong API base URL
3. CORS configuration mismatch
4. Request timeout

**Fixes:**

✓ **Verify backend is running:**
```bash
ps aux | grep uvicorn | grep -v grep
curl http://localhost:3001/api/health
```

✓ **Check frontend API base URL:**
Frontend should have `REACT_APP_API_BASE=http://localhost:3001` in `.env`

✓ **Restart both services:**
- Backend: Stop and restart uvicorn
- Frontend: Stop and restart React dev server

✓ **Check browser console:**
- Open Developer Tools (F12) → Console tab
- Look for detailed error messages including status codes and backend responses

### Issue 2: CORS Errors

**Symptoms:**
- Browser console shows: "Access to XMLHttpRequest at 'http://localhost:3001/api/ask' from origin 'http://localhost:3000' has been blocked by CORS policy"

**Root Causes:**
1. Backend CORS middleware not configured for the frontend origin
2. Frontend running on unexpected port or hostname

**Fixes:**

✓ **Verify allowed origins in backend:**
Backend `main.py` allows:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- Custom origin from `FRONTEND_ORIGIN` env var

✓ **If using a different origin:**
Add to backend `.env`:
```
FRONTEND_ORIGIN=http://your-custom-origin:port
```
Then restart backend.

✓ **Check preflight:**
```bash
curl -i -X OPTIONS http://localhost:3001/api/ask \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"
```
Should return CORS headers.

### Issue 3: 400 Bad Request - Empty Question

**Symptoms:**
- Frontend shows: "[400] Bad request - Question must not be empty."

**Root Cause:**
Frontend is sending an empty question string.

**Fix:**
✓ Ensure the input field has content before submitting.
✓ This is expected behavior - not an error.

### Issue 4: 400 Configuration Error - Missing API Key

**Symptoms:**
- Frontend shows: "[400] Configuration error - Missing GOOGLE_GEMINI_API_KEY..."

**Root Cause:**
Backend `.env` file is missing `GOOGLE_GEMINI_API_KEY`.

**Fix:**

✓ **Add API key to backend `.env`:**
```bash
cd ai-copilot-assistant-4345-4354/fastapi_backend
echo "GOOGLE_GEMINI_API_KEY=your_actual_api_key_here" >> .env
```

✓ **Restart backend:**
```bash
pkill -f "uvicorn.*main:app"
uvicorn src.api.main:app --host 0.0.0.0 --port 3001
```

### Issue 5: 502 Bad Gateway - Upstream AI Provider Error

**Symptoms:**
- Frontend shows: "[502] Upstream AI provider error..."

**Root Causes:**
1. Invalid API key
2. Gemini service unavailable
3. Network connectivity issues
4. Rate limit exceeded
5. Invalid model name

**Fixes:**

✓ **Verify API key is valid:**
Test with curl:
```bash
export GOOGLE_GEMINI_API_KEY="your_key_here"
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_GEMINI_API_KEY"
```

✓ **Check model name in `.env`:**
```
GEMINI_MODEL=gemini-2.5-flash
```

✓ **Check rate limits:**
Visit Google Cloud Console to verify quota and usage.

✓ **Check network connectivity:**
```bash
curl -I https://generativelanguage.googleapis.com
```

### Issue 6: Request Timeout

**Symptoms:**
- Frontend shows: "Request timeout - the server took too long to respond"
- Request takes longer than 25 seconds

**Root Causes:**
1. Large/complex question taking too long to process
2. Gemini API slow response
3. Network latency

**Current Timeouts:**
- Frontend (axios): 25 seconds
- Backend (gemini_client): 30 seconds

**Fixes:**

✓ **Increase timeout if needed:**

Frontend (`src/api.js`):
```javascript
export const api = axios.create({ 
  baseURL: API_BASE,
  timeout: 60000, // 60 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});
```

Backend (`routers/gemini_client.py`):
```python
answer_text, model_used = await get_answer(q, timeout=60.0)
```

✓ **Simplify the question** if it's very long or complex.

### Issue 7: Frontend Not Showing Backend Error Details

**Symptoms:**
- Frontend only shows "Request failed" or generic error

**Root Cause:**
Old error handling code not extracting backend error details.

**Fix:**
✓ **Already fixed!** The updated `App.js` now extracts:
- `message` field
- `detail` field
- `hint` field
- `action` field
- HTTP status code

Errors now display as: `[status] message - detail - Hint: ... - Action: ...`

### Issue 8: Backend Logs Not Showing Requests

**Symptoms:**
- No request logs in backend terminal

**Root Cause:**
Logging middleware not enabled or misconfigured.

**Fix:**
✓ **Already fixed!** Backend `main.py` now includes request/response logging middleware.

Check logs in backend terminal for:
```
INFO: Incoming request: POST /api/ask from 127.0.0.1 (Origin: http://localhost:3000)
INFO: Request completed: POST /api/ask -> 200 (2.543s)
```

## Enhanced Error Handling Features

### Frontend Enhancements (src/App.js)
- ✓ Extracts detailed error messages from backend responses
- ✓ Shows HTTP status codes
- ✓ Displays structured error fields (message, detail, hint, action)
- ✓ Handles network errors with helpful messages
- ✓ Detects timeout errors (ECONNABORTED)
- ✓ Console logging for debugging

### Backend Enhancements

#### main.py
- ✓ Request/response logging middleware
- ✓ Tracks request duration
- ✓ Logs origin headers for CORS debugging
- ✓ Catches unhandled exceptions and returns JSON

#### routers/ask.py
- ✓ Maps exceptions to appropriate HTTP status codes
- ✓ Returns structured JSON errors with message, detail, hint, action
- ✓ Distinguishes between client errors (400), upstream errors (502), and server errors (500)

#### routers/gemini_client.py
- ✓ Server-side timeout (30s default, configurable)
- ✓ Async execution with proper timeout handling
- ✓ Detailed error logging with stack traces
- ✓ Custom exception types for better error classification

### API Client Enhancements (src/api.js)
- ✓ Explicit Content-Type header
- ✓ 25-second timeout
- ✓ Configurable base URL via REACT_APP_API_BASE

## Verification Checklist

Before considering the issue resolved, verify:

- [ ] Backend health endpoint responds: `curl http://localhost:3001/api/health`
- [ ] CORS headers present for localhost:3000
- [ ] CORS headers present for 127.0.0.1:3000
- [ ] POST /api/ask with valid question returns 200
- [ ] POST /api/ask with empty question returns 400 with proper error
- [ ] Frontend can successfully ask a question and get an answer
- [ ] Frontend displays detailed error messages (not just "Network Error")
- [ ] Backend logs show incoming requests and responses
- [ ] Browser console shows no CORS errors
- [ ] Timeout handling works (try a very long question if needed)

## Getting Help

If issues persist after following this guide:

1. **Check backend logs** in the terminal where uvicorn is running
2. **Check browser console** (F12 → Console) for detailed error messages
3. **Run diagnostic tests**: `./test_diagnostics.sh`
4. **Verify environment variables**:
   - Backend: `cat .env` in `fastapi_backend/`
   - Frontend: `cat .env` in `react_frontend/`
5. **Check network tab** in browser DevTools to see actual request/response

## Related Files

- Backend main: `src/api/main.py`
- Ask endpoint: `src/api/routers/ask.py`
- Gemini client: `src/api/routers/gemini_client.py`
- Frontend API: `react_frontend/src/api.js`
- Frontend UI: `react_frontend/src/App.js`
- Backend config: `src/api/deps.py`
- Diagnostic tests: `test_diagnostics.sh`
