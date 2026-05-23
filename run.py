import uvicorn
import os

if __name__ == "__main__":
    print("[STARTING] Starting AI Automated Code Review Pipeline Server...")
    print("[INFO] Dashboard will be available at: http://127.0.0.1:8000")
    print("[INFO] GitHub webhook receiver URL: http://127.0.0.1:8000/webhook")
    print("Press Ctrl+C to terminate.")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
