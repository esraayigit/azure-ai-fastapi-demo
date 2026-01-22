# Azure AI FastAPI Demo

🚀 **FastAPI tabanlı AI API** - Azure cloud servisleri ile entegre duygu analizi, metin sınıflandırma ve AI chat uygulaması.

## 📋 Proje Hakkında

Bu proje, Azure cloud servisleriyle entegre edilmiş, production-ready bir AI API demonstrasyonudur. FastAPI framework'ü kullanılarak geliştirilmiş olup, Azure'un enterprise-grade servislerini kullanır.

### ✨ Özellikler

- **🤖 Duygu Analizi (Sentiment Analysis)**: Metinlerin pozitif, negatif veya nötr olduğunu analiz eder
- **📊 Metin Sınıflandırma**: Metinleri kategorilere ayırır (Technology, Business, Sports, vb.)
- **💬 AI Chat**: Azure OpenAI ile sohbet tamamlama
- **📝 Request/Response Logging**: Tüm istekler Blob Storage'da saklanır
- **📈 Monitoring**: Application Insights ile real-time izleme
- **🔒 Production-Ready**: Güvenli, ölçeklenebilir mimari

## 🏗️ Mimari

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│     Azure App Service               │
│  ┌────────────────────────────┐    │
│  │     FastAPI Application     │    │
│  │  ┌──────────────────────┐  │    │
│  │  │   AI Endpoints       │  │    │
│  │  │  - /sentiment        │  │    │
│  │  │  - /classify         │  │    │
│  │  │  - /chat             │  │    │
│  │  └──────────────────────┘  │    │
│  └────────────────────────────┘    │
└─────────────────────────────────────┘
         │           │          │
         │           │          │
    ┌────▼─────┐ ┌──▼────────┐ ┌▼────────────────┐
    │  Azure   │ │   Azure   │ │  Application    │
    │ OpenAI   │ │   Blob    │ │   Insights      │
    │ Service  │ │  Storage  │ │  (Monitoring)   │
    └──────────┘ └───────────┘ └─────────────────┘
```

### 🔧 Kullanılan Azure Servisleri

1. **Azure App Service** → API hosting ve deployment
2. **Azure OpenAI Service** → AI inference (GPT modelleri)
3. **Azure Blob Storage** → Request/response logging ve data persistence
4. **Azure Application Insights** → Real-time monitoring, telemetry ve analytics

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.11+
- Azure hesabı
- Azure CLI (deployment için)
- Git

### Lokal Kurulum

1. **Repository'yi klonlayın**
```bash
git clone https://github.com/your-username/azure-ai-fastapi-demo.git
cd azure-ai-fastapi-demo
```

2. **Virtual environment oluşturun**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Bağımlılıkları yükleyin**
```bash
pip install -r requirements.txt
```

4. **Environment değişkenlerini ayarlayın**
```bash
cp .env.example .env
# .env dosyasını düzenleyerek Azure credentials'larınızı ekleyin
```

5. **Uygulamayı çalıştırın**
```bash
uvicorn app.main:app --reload
```

6. **API dokümantasyonunu açın**
```
http://localhost:8000/docs
```

## 📁 Proje Yapısı

```
azure-ai-fastapi-demo/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI uygulaması
│   ├── config.py            # Configuration yönetimi
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic modelleri
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py    # Azure OpenAI entegrasyonu
│   │   ├── blob_storage.py  # Blob Storage servisi
│   │   └── monitoring.py    # Application Insights
│   └── routers/
│       ├── __init__.py
│       ├── health.py        # Health check endpoints
│       └── ai_endpoints.py  # AI API endpoints
├── deploy/
│   ├── azure-deploy.json    # ARM template
│   └── DEPLOYMENT.md        # Deployment guide
├── .env.example             # Environment template
├── .gitignore
├── requirements.txt
├── startup.sh              # Azure startup script
└── README.md
```

## 🔌 API Endpoints

### Health Check
```http
GET /health
```

### Duygu Analizi
```http
POST /api/v1/sentiment
Content-Type: application/json

{
  "text": "Bu ürünü çok beğendim, harika!",
  "language": "tr"
}
```

**Response:**
```json
{
  "text": "Bu ürünü çok beğendim, harika!",
  "sentiment": "positive",
  "confidence": 0.95,
  "scores": {
    "positive": 0.95,
    "negative": 0.02,
    "neutral": 0.03
  },
  "processing_time": 0.234,
  "request_id": "uuid-here"
}
```

### Metin Sınıflandırma
```http
POST /api/v1/classify
Content-Type: application/json

{
  "text": "Apple released new iPhone with advanced AI features"
}
```

### AI Chat
```http
POST /api/v1/chat
Content-Type: application/json

{
  "prompt": "Azure cloud computing nedir?",
  "max_tokens": 200,
  "temperature": 0.7
}
```

## ☁️ Azure'a Deployment

### Otomatik Deployment (ARM Template)

```bash
# Resource group oluştur
az group create --name rg-ai-api --location eastus

# Deploy et
az deployment group create \
  --resource-group rg-ai-api \
  --template-file deploy/azure-deploy.json \
  --parameters webAppName=my-ai-api
```

### Manuel Deployment

Detaylı deployment adımları için [DEPLOYMENT.md](deploy/DEPLOYMENT.md) dosyasına bakın.

## 📊 Monitoring ve Analytics

### Application Insights

Uygulama otomatik olarak şunları izler:
- HTTP request/response süreleri
- API kullanım istatistikleri
- Exception'lar ve hatalar
- Custom events ve metrics

### Logs

Azure Portal'da Application Insights → Logs bölümünden KQL sorguları çalıştırabilirsiniz:

```kql
requests
| where timestamp > ago(24h)
| summarize count() by name, resultCode
| order by count_ desc
```

### Blob Storage Logs

Her request/response otomatik olarak Blob Storage'a kaydedilir:
```
ai-api-logs/
  └── logs/
      └── 20260122/
          ├── request-uuid-1.json
          ├── request-uuid-2.json
          └── ...
```

## 🔐 Environment Variables

```bash
# Azure AI Services
AZURE_AI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_AI_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER_NAME=ai-api-logs

# Application Insights
APPINSIGHTS_INSTRUMENTATIONKEY=your-key-here
APPINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

## 🎯 Mülakat için Anlatım Noktaları

### Teknik Mimari
> "Bu projede FastAPI kullanarak bir AI API geliştirdim. Model inference Azure OpenAI Service üzerinden yapılıyor ve uygulama Azure App Service'de host ediliyor. Request/response'lar Blob Storage'da loglanıyor ve Application Insights ile real-time monitoring yapıyorum."

### Azure Entegrasyonu
> "Projem 4 temel Azure servisi kullanıyor: App Service (hosting), OpenAI Service (AI inference), Blob Storage (data persistence) ve Application Insights (monitoring). Bu servisleri Python SDK'ları ile entegre ettim."

### Production-Ready Özellikler
> "API'de exception handling, request validation (Pydantic), background tasks (async logging), CORS middleware ve comprehensive logging var. Application Insights ile tüm metrikleri izliyorum."

### Ölçeklenebilirlik
> "App Service otomatik scaling destekliyor. Blob Storage'da partition key stratejisi kullanarak büyük data volume'leri yönetebilirim. Async/await pattern'i ile concurrent request'leri handle ediyorum."

## 📚 Kaynaklar

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)

## 📝 Lisans

MIT License

## 👤 İletişim

Sorularınız için: [your-email@example.com]

---

⭐ Bu projeyi beğendiyseniz star vermeyi unutmayın!
