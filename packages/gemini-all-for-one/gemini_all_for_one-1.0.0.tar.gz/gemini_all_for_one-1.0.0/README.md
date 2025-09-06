# 🎨 Gemini All-for-One

A comprehensive AI image platform powered by Google's Gemini AI. Provides image generation, analysis, editing, and multimodal chat capabilities.

## ✨ Features

- **🎨 Image Generation**: Create AI-generated images using Pollinations.ai (no API key needed)
- **💬 AI Chat**: Interactive chat with Google Gemini AI (requires GEMINI_API_KEY)
- **📊 API Status**: Real-time service health monitoring
- **☁️ Serverless Ready**: Optimized for Vercel deployment

## 🚀 Quick Deploy to Vercel

1. **Fork/Clone this repository**

2. **Connect to Vercel**:
   - Visit [vercel.com](https://vercel.com)
   - Click "New Project" 
   - Import your repository

3. **Add Environment Variables** (optional):
   - `GEMINI_API_KEY`: For AI chat functionality
   - `SECRET_KEY`: Flask session security

4. **Deploy**: Vercel automatically detects the configuration!

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Optional | Google Gemini AI API key for chat functionality |
| `SECRET_KEY` | Optional | Flask session secret (auto-generated if not set) |

## 🏃‍♂️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Visit http://localhost:5000
```

## 📁 Project Structure

```
├── api/
│   └── index.py          # Vercel serverless entry point
├── templates/
│   └── index.html        # Web interface
├── library_backup/       # Original library development files
├── app.py                # Main Flask application
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── .vercelignore        # Files to exclude from deployment
```

## 🔌 API Endpoints

- `GET /` - Web interface
- `GET /api/health` - Service status check
- `POST /api/generate` - Generate images with Pollinations
- `POST /api/chat` - Chat with Gemini AI
- `POST /api/analyze` - Image analysis (requires GEMINI_API_KEY)

## 🎯 Core Features

### Image Generation (Free)
```javascript
// Generate an image
fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        prompt: 'A beautiful sunset over mountains',
        style: 'photorealistic'
    })
})
```

### AI Chat (Requires API Key)
```javascript
// Chat with AI
fetch('/api/chat', {
    method: 'POST', 
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'Hello, how are you?',
        model: 'gemini-2.5-flash-lite'
    })
})
```

## 📚 Using the Library

This demo uses the published `ai-image-platform==1.0.0` library:

```python
from ai_image_platform import PollinationsClient, GeminiChatClient

# Free image generation
pollinations = PollinationsClient()
result = pollinations.generate_image(
    prompt="A futuristic city",
    style="cyberpunk"
)

# AI chat (requires API key) 
chat = GeminiChatClient()
response = chat.ask_question("What is AI?")
```

## 🛠️ Built With

- **ai-image-platform**: Core AI functionality
- **Flask**: Web framework  
- **Vercel**: Serverless deployment platform
- **Pollinations.ai**: Free image generation
- **Google Gemini**: Advanced AI chat

## 📞 Support

For library documentation and examples, visit the [ai-image-platform PyPI page](https://pypi.org/project/ai-image-platform/).

---

**Ready to deploy!** 🚀 Your serverless AI image platform is optimized and ready for production.