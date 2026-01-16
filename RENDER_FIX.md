# Render Build Error Fix

## Muammo

```
BackendUnavailable: Cannot import 'setuptools.build_meta'
```

## Sabab

Render Python 3.13 ishlatmoqda, lekin ba'zi paketlar 3.13 bilan mos emas.

## Yechim

### 1. Python Version Fix

✅ `backend/runtime.txt` yaratildi:

```
python-3.11.0
```

### 2. Requirements Update

✅ `backend/requirements.txt` yangilandi:

```python
# Build tools qo'shildi
setuptools>=65.0.0
wheel>=0.38.0
```

### 3. Build Script Update

✅ `backend/render-build.sh` yangilandi:

```bash
pip install --upgrade pip setuptools wheel
```

## Render'da Sozlash

### Environment Variables

Render dashboard'da qo'shing:

```
PYTHON_VERSION=3.11.0
```

### Build Command (yangilangan)

```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

Yoki:

```bash
bash render-build.sh
```

## Test Qilish

Local'da test qiling:

```bash
cd backend

# Virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# Install
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run
uvicorn main:app --reload
```

## Render'da Qayta Deploy

1. GitHub'ga push qiling (allaqachon qilindi)
2. Render dashboard'ga o'ting
3. Backend service'ni oching
4. "Manual Deploy" → "Clear build cache & deploy"
5. Logs'ni kuzating

## Kutilgan Natija

Build muvaffaqiyatli tugashi kerak:

```
✅ Installing system dependencies...
✅ Upgrading pip and installing build tools...
✅ Installing Python dependencies...
✅ Backend build complete!
```

## Agar Yana Xato Bo'lsa

### Option 1: Python Version Tekshirish

Render dashboard → Environment:

```
PYTHON_VERSION=3.11.0
```

### Option 2: Build Command

```bash
pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt
```

### Option 3: Dockerfile Ishlatish

Render dashboard → Settings:

- Docker: Enable
- Dockerfile path: `backend/Dockerfile`

## Qo'shimcha Ma'lumot

- Python 3.11 barqaror va barcha paketlar bilan mos
- Python 3.13 juda yangi, ba'zi paketlar hali mos emas
- `runtime.txt` Render'ga qaysi Python version ishlatishni aytadi
- `setuptools` va `wheel` build tools hisoblanadi

---

**Status:** ✅ Fixed and pushed to GitHub
**Commit:** Latest
