# Fall Detection ML API

Machine Learning API for fall detection deployed on Render.

## Deployment Steps

### 1. Generate the Model
```bash
cd ..
python create_model.py
```

### 2. Copy Model File
```bash
copy fall_model.pkl ml_api\fall_model.pkl
```

### 3. Test Locally
```bash
cd ml_api
pip install -r requirements.txt
python app.py
```

Test endpoint:
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d "{\"accelerometer\":{\"x\":25.5,\"y\":12.3,\"z\":30.1},\"gyroscope\":{\"x\":2.1,\"y\":1.8,\"z\":3.2}}"
```

### 4. Deploy to Render

1. **Create GitHub Repository**
   - Push this `ml_api` folder to GitHub

2. **Create Render Web Service**
   - Go to https://render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository with ml_api folder

3. **Configure Build Settings**
   - **Name**: fall-detection-ml-api
   - **Root Directory**: ml_api (if not in root)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **Add Environment Variables** (Optional)
   - None required for basic setup

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~5 minutes)
   - Copy your API URL: `https://fall-detection-ml-api.onrender.com`

### 5. Test Production API

```bash
curl -X GET https://your-app.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "service": "Fall Detection ML API",
  "version": "1.0.0"
}
```

## API Endpoints

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "service": "Fall Detection ML API",
  "version": "1.0.0"
}
```

### POST /predict
Predict single sensor reading

**Request:**
```json
{
  "accelerometer": {
    "x": 25.5,
    "y": 12.3,
    "z": 30.1
  },
  "gyroscope": {
    "x": 2.1,
    "y": 1.8,
    "z": 3.2
  }
}
```

**Response:**
```json
{
  "success": true,
  "prediction": true,
  "confidence": 0.95,
  "severity": "critical",
  "probabilities": {
    "normal": 0.05,
    "fall": 0.95
  },
  "method": "random_forest"
}
```

### POST /batch-predict
Predict multiple sensor readings

**Request:**
```json
{
  "data": [
    {
      "accelerometer": {"x": 1.0, "y": 0.5, "z": 9.8},
      "gyroscope": {"x": 0.1, "y": 0.2, "z": 0.1}
    },
    {
      "accelerometer": {"x": 25.5, "y": 12.3, "z": 30.1},
      "gyroscope": {"x": 2.1, "y": 1.8, "z": 3.2}
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "predictions": [
    {"is_fall": false, "confidence": 0.05},
    {"is_fall": true, "confidence": 0.95}
  ],
  "count": 2
}
```

## Update Backend Integration

After deployment, update your backend `.env` file:

```env
ML_API_URL=https://your-app.onrender.com
ML_API_TIMEOUT=5
```

Then update backend/app.py to use the Render API instead of local detection.
