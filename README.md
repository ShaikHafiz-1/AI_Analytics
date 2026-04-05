# Planning Intelligence Dashboard

A comprehensive planning analytics platform combining a Python Azure Functions backend with a React TypeScript frontend. Analyzes supply chain planning data from Excel/Blob Storage and provides AI-driven insights through an interactive dashboard.

## Project Structure

```
planning-intelligence/
├── planning_intelligence/     # Python Azure Functions backend
│   ├── function_app.py        # HTTP trigger entry point
│   ├── normalizer.py          # SAP column mapping
│   ├── comparator.py          # Record comparison & risk derivation
│   ├── analytics.py           # Summary & analytical queries
│   ├── trend_analyzer.py      # Multi-snapshot trend detection
│   ├── ai_insight_engine.py   # LLM-based insights
│   ├── mcp/                   # Model Context Protocol server
│   ├── requirements.txt       # Python dependencies
│   └── tests/                 # Unit tests (39 tests)
│
├── frontend/                  # React TypeScript frontend
│   ├── src/
│   │   ├── pages/            # DashboardPage
│   │   ├── components/       # 18 dashboard components
│   │   ├── services/         # API client & validation
│   │   ├── types/            # TypeScript interfaces
│   │   └── mock/             # Sample data
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
│
├── .github/workflows/         # CI/CD pipelines
│   ├── deploy.yml            # Backend deployment
│   └── deploy-frontend.yml   # Frontend deployment
│
└── README.md                  # This file
```

## Tech Stack

### Backend
- **Runtime**: Python 3.11, Azure Functions (Premium Plan)
- **Data Processing**: pandas, openpyxl, xlrd
- **Cloud**: Azure Blob Storage, Azure OpenAI (optional)
- **Integration**: Model Context Protocol (MCP) for LLM tools

### Frontend
- **Framework**: React 18.2.0 with TypeScript 4.9.5
- **Styling**: Tailwind CSS 3.4.0
- **Build**: react-scripts 5.0.1
- **Type Safety**: Full TypeScript support with strict interfaces

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Azure Storage Account with Blob Storage
- Git

### Backend Setup

1. **Clone and navigate to backend**
   ```bash
   git clone <your-gitlab-repo>
   cd planning_intelligence
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure Blob Storage credentials
   ```

5. **Run locally with Azure Functions Core Tools**
   ```bash
   func start
   ```
   Backend will be available at `http://localhost:7071/api`

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API endpoint
   # REACT_APP_API_URL=http://localhost:7071/api
   # REACT_APP_API_KEY=<your-function-key>
   ```

4. **Start development server**
   ```bash
   npm start
   ```
   Frontend will open at `http://localhost:3000`

## API Endpoints

### Planning Intelligence Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/planning-intelligence` | POST | Two-snapshot analysis with 6 analytical queries |
| `/api/planning-dashboard` | POST | UI-ready dashboard response |
| `/api/planning-dashboard-v2` | POST | Blob-first cached snapshot endpoint |
| `/api/daily-refresh` | POST | Triggers daily refresh from Blob Storage |
| `/api/explain` | POST | LLM-grounded insight endpoint |

### Request Example (Two-Snapshot)
```json
{
  "query_type": "summary",
  "location_id": "LOC001",
  "material_group": "PUMP",
  "current_rows": [...],
  "previous_rows": [...]
}
```

### Request Example (Trend Analysis)
```json
{
  "query_type": "trend_analysis",
  "snapshots": [
    { "snapshot_date": "2026-03-01", "rows": [...] },
    { "snapshot_date": "2026-03-08", "rows": [...] }
  ]
}
```

## Supported Query Types

### Two-Snapshot Queries
- `summary` - All six analytical questions
- `changed_count` - How many records changed?
- `changed_records` - Show changed records
- `changes_by_location` - Which locations changed most?
- `changes_by_material_group` - Which material groups changed?
- `change_driver_analysis` - Qty/supplier/design drivers
- `high_risk_records` - High-risk records
- `supplier_design_changes` - Supplier + design changes

### Trend Queries (Multi-Snapshot)
- `trend_analysis` - Full trend summary
- `consistently_increasing` - Materials with consistent growth
- `recurring_changes` - Materials that changed repeatedly
- `one_off_spikes` - One-time spikes
- `change_streaks` - Consecutive change patterns

## Dashboard Features

### Core Components
- **Planning Health Card** - Overall health score (0-100)
- **Forecast Card** - Demand trends and deltas
- **Trend Card** - Change patterns and drivers
- **Risk Card** - High-risk record summary
- **AI Insight Card** - LLM-generated insights
- **Root Cause Card** - Change driver analysis
- **Datacenter Card** - Location-based breakdown
- **Material Group Card** - Equipment category analysis
- **Supplier Card** - Supplier impact analysis
- **Design Card** - Design change tracking
- **ROJ Card** - Schedule/ROJ analysis

### Advanced Features
- **Copilot Panel** - Chat-based Q&A with context grounding
- **Drill-Down Panel** - Detailed record inspection
- **Alert Banner** - Real-time alerts and notifications
- **Tooltip** - Contextual help and explanations

## Testing

### Backend Tests
```bash
cd planning_intelligence
pytest tests/ -v
```

39 unit tests covering:
- Column normalization and null handling
- Change detection and risk classification
- Filtering and analytics
- Trend detection and pattern analysis

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### GitHub Actions CI/CD

**Backend Deployment** (`.github/workflows/deploy.yml`)
- Triggers on push to `main`
- Builds Python package
- Deploys to Azure Functions: `pi-planning-intelligence`
- Requires: `AZUREAPPSERVICE_PUBLISHPROFILE` secret

**Frontend Deployment** (`.github/workflows/deploy-frontend.yml`)
- Triggers on changes to `frontend/` or workflow file
- Builds React app
- Deploys to Azure Blob Storage (`$web` container)
- Requires: `AZURE_STORAGE_CONNECTION_STRING` secret

### Required GitHub Secrets
```
AZUREAPPSERVICE_PUBLISHPROFILE    # Azure Functions publish profile
AZURE_STORAGE_CONNECTION_STRING   # Blob Storage connection string
REACT_APP_API_URL                 # Backend API endpoint
REACT_APP_API_KEY                 # Azure Function key
```

## Environment Configuration

### Backend (.env)
```env
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
BLOB_CONTAINER_NAME=planning-data
BLOB_CURRENT_FILE=current.csv
BLOB_PREVIOUS_FILE=previous.csv
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
SNAPSHOT_FILE_PATH=/home/data/planning_snapshot.json
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_API_KEY=<your-function-key>
REACT_APP_USE_MOCK=false
```

## Data Flow

```
Excel/SharePoint
        ↓
Power Automate Flow
        ↓
Azure Functions (planning_intelligence)
  ├─ Normalize (SAP columns → clean fields)
  ├─ Filter (location/material group)
  ├─ Compare (current vs previous)
  ├─ Analyze (6 analytical queries)
  └─ Trend (multi-snapshot patterns)
        ↓
Blob Storage (snapshot cache)
        ↓
React Frontend
  ├─ Dashboard Cards
  ├─ Copilot Q&A
  └─ Drill-Down Details
```

## Architecture Highlights

### Backend
- **Modular Design**: Separate modules for normalization, comparison, analytics, trends
- **Composite Key Matching**: `location_id + material_group + material_id`
- **Risk Classification**: Automatic risk level derivation based on change types
- **Trend Detection**: Multi-snapshot analysis with spike/streak/recurring detection
- **LLM Integration**: MCP server for AI-powered insights
- **Snapshot Caching**: Fast retrieval with blob fallback

### Frontend
- **Type-Safe**: Full TypeScript with strict interfaces
- **Component-Based**: 18 reusable dashboard components
- **Advanced UX**: Copilot integration, drill-down panels, alerts
- **Responsive Design**: Mobile-friendly with Tailwind CSS
- **Mock Data Support**: Development without backend

## Troubleshooting

### Backend Issues

**"No snapshot found"**
- Run `/api/daily-refresh` to load data from Blob Storage
- Check `BLOB_CONNECTION_STRING` in `.env`

**"Invalid JSON body"**
- Ensure request body is valid JSON
- Check `current_rows` and `previous_rows` format

**"Blob load failed"**
- Verify Blob Storage connection string
- Check container name and file names
- Ensure CSV files exist in Blob Storage

### Frontend Issues

**"API error 401"**
- Check `REACT_APP_API_KEY` in `.env`
- Verify Azure Function key is correct

**"Cannot reach backend"**
- Ensure backend is running (`func start`)
- Check `REACT_APP_API_URL` points to correct endpoint
- Verify CORS is enabled in Azure Functions

**"Mock data not loading"**
- Set `REACT_APP_USE_MOCK=true` in `.env`
- Check `src/mock/sample_payload.json` exists

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit with clear messages: `git commit -m "Add feature description"`
4. Push to GitLab: `git push origin feature/your-feature`
5. Create a merge request

## Documentation

- **Backend Design**: See `planning_intelligence/DESIGN.md`
- **API Samples**: See `planning_intelligence/samples/`
- **Type Definitions**: See `frontend/src/types/dashboard.ts`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs: `func start` output
3. Check browser console for frontend errors
4. Review Azure Functions logs in Azure Portal

## License

[Your License Here]

## Contact

[Your Contact Information]
