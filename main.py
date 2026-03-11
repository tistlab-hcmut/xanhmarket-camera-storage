import os
import glob
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- DYNAMIC STORAGE CONFIGURATION ---
# This ensures the 'camera_data' folder is always in the same folder as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_STORAGE = os.path.join(SCRIPT_DIR, "camera_data")

# Enable CORS for website access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def ensure_dir(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# --- API ENDPOINTS ---

@app.post("/camera")
async def upload_camera_image(
    device: str = Form(...), 
    image: UploadFile = File(...)
):
    # Create device-specific folder inside camera_data
    safe_device = "".join(c for c in device if c.isalnum() or c in ("-", "_")).strip()
    device_folder = os.path.join(BASE_STORAGE, safe_device)
    ensure_dir(device_folder)
    
    # Filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(image.filename)[1] or ".jpg"
    filename = f"{timestamp}{ext}"
    file_path = os.path.join(device_folder, filename)
    
    try:
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)
        return {"status": "success", "device": safe_device, "saved_as": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write error: {e}")

@app.get("/camera/latest-image")
async def get_latest_image(device: str, request: Request):
    safe_device = "".join(c for c in device if c.isalnum() or c in ("-", "_")).strip()
    device_folder = os.path.join(BASE_STORAGE, safe_device)
    
    if not os.path.exists(device_folder):
        raise HTTPException(status_code=404, detail="Device not found")
        
    files = glob.glob(os.path.join(device_folder, "*"))
    if not files:
        raise HTTPException(status_code=404, detail="No images found")
        
    latest_file = max(files, key=os.path.getmtime)
    filename = os.path.basename(latest_file)
    
    # Response data
    mtime = os.path.getmtime(latest_file)
    dt_iso = datetime.fromtimestamp(mtime).isoformat() + "Z"
    
    # Generate the URL based on the domain (xanhmarket-camera.hpcc.vn)
    base_url = str(request.base_url).rstrip("/")
    full_url = f"{base_url}/images/{safe_device}/{filename}"
    
    return {
        "timestamp": dt_iso,
        "url": full_url
    }

@app.get("/images/{device}/{filename}")
async def serve_image(device: str, filename: str):
    # Securely find the file
    file_path = os.path.normpath(os.path.join(BASE_STORAGE, device, filename))
    
    # Security check to prevent accessing files outside the storage folder
    if not file_path.startswith(BASE_STORAGE) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
        
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)