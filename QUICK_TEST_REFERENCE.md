# Quick Test Reference - POST /api/ask

## One-Line Tests

### Health Check
```bash
curl -s http://localhost:3001/api/health && echo " ✅"
```

### Valid Question
```bash
curl -s -X POST http://localhost:3001/api/ask -H "Content-Type: application/json" -d '{"question":"Hello"}' | jq
```

### Test CORS
```bash
curl -si -X OPTIONS http://localhost:3001/api/ask -H "Origin: http://localhost:3000" | grep access-control
```

### Full Diagnostic Suite
```bash
cd ai-copilot-assistant-4345-4354/fastapi_backend && ./test_diagnostics.sh
```

## Expected Responses

### ✅ Success (200)
```json
{
  "answer": "...",
  "model": "gemini-2.5-flash"
}
```

### ❌ Empty Question (400)
```json
{
  "message": "Bad request",
  "detail": "Question must not be empty."
}
```

### ❌ Missing API Key (400)
```json
{
  "message": "Configuration error",
  "detail": "Missing GOOGLE_GEMINI_API_KEY...",
  "action": "Set GOOGLE_GEMINI_API_KEY in backend environment and retry."
}
```

### ❌ Timeout (502)
```json
{
  "message": "Upstream AI provider error",
  "detail": "Request timeout: AI provider took longer than 30s to respond.",
  "hint": "Verify your model name, API key, and account quota."
}
```

## Service Status

### Check Backend
```bash
ps aux | grep uvicorn | grep -v grep
```

### Check Frontend
```bash
ps aux | grep react-scripts | grep -v grep
```

### Backend Logs
Look for log output in the terminal where uvicorn is running

## Configuration Check

### Backend Environment
```bash
cd ai-copilot-assistant-4345-4354/fastapi_backend
cat .env | grep -E "GOOGLE_GEMINI_API_KEY|GEMINI_MODEL|BACKEND_PORT|FRONTEND_ORIGIN"
```

### Frontend Environment
```bash
cd ai-copilot-assistant-4345-4355/react_frontend
cat .env | grep REACT_APP_API_BASE
```

## Port Verification

```bash
# Check what's listening on ports
netstat -tlnp 2>/dev/null | grep -E "3000|3001"
# or
lsof -i :3000,3001 2>/dev/null
```

## Browser Testing

1. Open: http://localhost:3000
2. Open DevTools (F12) → Network tab
3. Enter a question and click "Ask"
4. Observe request to http://localhost:3001/api/ask
5. Check response status, headers, and payload

## Common Issues Quick Fix

### CORS Error
```bash
# Add origin to backend .env
echo "FRONTEND_ORIGIN=http://your-origin:port" >> ai-copilot-assistant-4345-4354/fastapi_backend/.env
# Restart backend
```

### Connection Refused
```bash
# Verify backend is running
curl http://localhost:3001/api/health
# If not, start it:
cd ai-copilot-assistant-4345-4354/fastapi_backend
uvicorn src.api.main:app --host 0.0.0.0 --port 3001
```

### Timeout
```bash
# Check backend logs for errors
# Verify API key is valid
# Try a simpler question
```

## Status: All Systems Operational ✅
- Backend: Running on port 3001 ✅
- Frontend: Running on port 3000 ✅
- CORS: Configured correctly ✅
- Timeouts: Implemented (frontend 25s, backend 30s) ✅
- Error Handling: Enhanced with detailed messages ✅
- Logging: Active and capturing all requests ✅
