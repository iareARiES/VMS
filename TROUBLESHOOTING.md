# Troubleshooting Guide

## Live Preview Not Working

### Issue: WebSocket connects but no detections appear

**Causes:**
1. **No models enabled** - You must enable at least one model in the Models page
2. **No webcam available** - Detection service tries to use webcam (device 0)
3. **Models not loaded** - Models need to be in `models/` directory

**Solutions:**

1. **Enable Models:**
   - Go to Models page
   - Toggle at least one model ON
   - Make sure the model file exists in `models/` directory

2. **Check Webcam:**
   - On Windows, webcam should be available as device 0
   - If no webcam, the detection will fail silently
   - Check detection service terminal for errors

3. **Check Model Files:**
   - Ensure ONNX files are in `intrusion-suite/models/`
   - Files should be: `best.onnx`, `yolo11npRETRAINED.onnx`, `Fire_Event_best.onnx`, etc.

4. **Manual Start:**
   - The Dashboard should auto-start detection when opened
   - If not, check browser console for errors
   - Try refreshing the page

## Video Upload/Analysis Not Working

### Issue: Video uploads but no analysis happens

**Causes:**
1. **No models enabled** - At least one model must be enabled
2. **Model files missing** - ONNX files not in `models/` directory
3. **File path issues** - Backend can't find uploaded file

**Solutions:**

1. **Enable Models First:**
   ```
   - Go to Models page
   - Enable at least one model (e.g., yolo11npRETRAINED.onnx)
   - Set confidence threshold (default 0.35)
   ```

2. **Check Model Files:**
   ```bash
   # Windows
   dir intrusion-suite\models\*.onnx
   
   # Should show:
   # best.onnx
   # yolo11npRETRAINED.onnx
   # Fire_Event_best.onnx
   # w600k_mbf.onnx
   ```

3. **Check Upload:**
   - Video should upload to `storage/videos/`
   - Check backend terminal for errors
   - Check detection service terminal for processing status

4. **Check Events:**
   - After analysis, check Events page
   - Events are saved to database automatically
   - Snapshots saved to `storage/snaps/`

## Common Errors

### "No models enabled"
**Fix:** Go to Models page and enable at least one model

### "File not found" (video analysis)
**Fix:** Check that video file was uploaded successfully to `storage/videos/`

### "Failed to load model"
**Fix:** 
- Check model file exists in `models/` directory
- Check file permissions
- Verify ONNX file is valid

### WebSocket connection errors
**Fix:**
- Ensure backend is running on port 8000
- Ensure detection service is running on port 8010
- Check firewall settings

### "Database is locked"
**Fix:**
- Only one process should access SQLite at a time
- Restart backend service
- For production, use PostgreSQL instead

## Testing Steps

1. **Verify Services Running:**
   ```powershell
   netstat -ano | findstr ":8000 :8010 :3000"
   ```

2. **Test Backend:**
   ```powershell
   curl http://localhost:8000/
   # Should return: {"message":"Intrusion Detection Backend API"...}
   ```

3. **Test Detection Service:**
   ```powershell
   curl http://localhost:8010/
   # Should return: {"service":"detection-service"...}
   ```

4. **Check Models:**
   ```powershell
   curl http://localhost:8000/api/models
   # Should return list of models
   ```

5. **Enable a Model:**
   ```powershell
   curl -X PUT http://localhost:8000/api/models/yolo11npRETRAINED.onnx -H "Content-Type: application/json" -d '{"enabled": true}'
   ```

6. **Start Detection:**
   ```powershell
   curl -X POST http://localhost:8000/api/system/detection/start
   ```

## For Live Preview to Work

1. ✅ At least one model must be enabled
2. ✅ Model file must exist in `models/` directory
3. ✅ Detection service must be started (auto-starts from Dashboard)
4. ✅ Webcam must be available (or use test video file)

## For Video Analysis to Work

1. ✅ At least one model must be enabled
2. ✅ Video file must upload successfully
3. ✅ Model files must exist and be loadable
4. ✅ Backend must be accessible from detection service

## Quick Fixes

**No detections in live view?**
- Enable a model in Models page
- Refresh Dashboard
- Check detection service terminal for errors

**Video analysis fails?**
- Enable at least one model
- Check model files exist
- Check backend terminal for errors
- Check detection service terminal for processing status

**WebSocket errors?**
- Restart backend service
- Restart detection service
- Clear browser cache and refresh

