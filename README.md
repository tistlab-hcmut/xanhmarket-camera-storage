## Xanhmarket Camera Storage Service

This is a small **FastAPI** service for receiving and serving images from camera devices.  
Each device uploads images to the `/camera` endpoint, and the most recent image can be queried and fetched via HTTP.

### Features

- **Upload endpoint**: `POST /camera`  
  - Accepts a `multipart/form-data` request with:
    - **field** `device` (string): device identifier (alphanumeric, `-`, `_` are allowed).
    - **field** `image` (file): image file to store.
  - Stores files under a `camera_data/<device>/` folder (relative to `main.py`) with timestamped filenames.
- **Latest image metadata**: `GET /camera/latest-image?device=<deviceId>`  
  - Returns the timestamp and a public URL pointing to the latest image for that device.
- **Static image serving**: `GET /images/{device}/{filename}`  
  - Serves stored image files directly.
- **CORS enabled**: Allows requests from any origin (for easy integration with web frontends).

### Requirements

- Python 3.9+ (recommended)
- Dependencies listed in `pip.txt`:

```bash
pip install fastapi uvicorn python-multipart
```

Or, using `pip.txt` directly:

```bash
pip install -r pip.txt
```

### Project Structure

- `main.py` - FastAPI application with all endpoints.
- `pip.txt` - Minimal dependency installation command.
- `camera_data/` - Automatically created at runtime; holds per-device image folders.

### Running the Server

From the project root:

```bash
python main.py
```

By default, this starts uvicorn on `0.0.0.0:8000`.

Alternatively, you can run uvicorn explicitly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Usage

#### 1. Upload Image

**Request**

- **Method**: `POST`
- **URL**: `/camera`
- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `device`: string (e.g. `"camera-01"`)
  - `image`: file (binary)

**Example with `curl`:**

```bash
curl -X POST "http://localhost:8000/camera" \
  -F "device=camera-01" \
  -F "image=@/path/to/image.jpg"
```

**Example JSON response:**

```json
{
  "status": "success",
  "device": "camera-01",
  "saved_as": "20260311_101530.jpg"
}
```

#### 2. Get Latest Image Metadata

**Request**

- **Method**: `GET`
- **URL**: `/camera/latest-image?device=camera-01`

**Example with `curl`:**

```bash
curl "http://localhost:8000/camera/latest-image?device=camera-01"
```

**Example JSON response:**

```json
{
  "timestamp": "2026-03-11T10:15:30Z",
  "url": "http://localhost:8000/images/camera-01/20260311_101530.jpg"
}
```

> In production, the `url` will be based on the incoming request host (for example `https://xanhmarket-camera.hpcc.vn`).

#### 3. Fetch Image by URL

Use the `url` from `/camera/latest-image` directly in a browser, `img` tag, or HTTP client.  
The path maps to the `GET /images/{device}/{filename}` endpoint.

### Notes

- Device names are sanitized to allow only alphanumeric characters, `-`, and `_`.
- The `camera_data` directory and per-device subdirectories are created automatically if they do not exist.
- Ensure the process has write permission to the project directory so images can be saved.

