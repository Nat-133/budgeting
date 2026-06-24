# Budget Dashboard - Requirements Document

## Executive Summary

This document outlines the functional and non-functional requirements for rebuilding the budget dashboard as a modern web application with a FastAPI backend and React frontend.

## Current State Analysis

**Current Stack:**
- Backend: Python (Streamlit)
- Data Processing: Pandas, NumPy
- Visualization: Plotly (via Streamlit)
- Deployment: Streamlit server

**Current Limitations:**
- Page refreshes on interaction (even with `@st.fragment`)
- Scroll position not preserved during updates
- Limited interactivity without server communication
- Coupled UI and data processing
- Not scalable for future enhancements

---

## Proposed Architecture

### FastAPI Backend + React Frontend (Complete Rewrite)

**Backend:**
- FastAPI (Python REST API)
- Pandas/NumPy for data processing
- Automatic API documentation (Swagger)
- Async/await for performance

**Frontend:**
- React 18+ with TypeScript
- React-Plotly.js for visualizations
- Axios for API communication
- React Query for data caching

**Data Storage:**
- CSV files (existing format maintained)
- Future: Optional migration to PostgreSQL/SQLite

---

## Functional Requirements

### FR1: Data Management

#### FR1.1: Data Loading
- **MUST** load budget CSV files from `budgets/YYYY-MM-DD-budget.csv`
- **MUST** load income CSV files from `income/YYYY-MM-DD-income.csv`
- **MUST** load balance records from `balence_record.csv`
- **MUST** parse dates from filenames and CSV content
- **MUST** handle missing or malformed files gracefully

#### FR1.2: Data Processing
- **MUST** calculate fractional months between dates
- **MUST** calculate budgeted spending between any two dates
- **MUST** calculate expected income between any two dates
- **MUST** compute balance analysis (spending deficit, saving rate, etc.)
- **MUST** generate daily prediction timelines for any start date

#### FR1.3: Data Caching
- **SHOULD** cache CSV file reads in memory
- **SHOULD** cache calculated predictions to avoid recomputation
- **MUST** provide cache invalidation endpoint
- **SHOULD** use React Query for client-side caching

---

### FR2: API Endpoints

#### FR2.1: Data Retrieval Endpoints
- **MUST** provide `GET /api/balance` - returns all balance records
- **MUST** provide `GET /api/budgets` - returns all budget files with dates
- **MUST** provide `GET /api/income` - returns all income files with dates
- **MUST** provide `GET /api/balance-analysis` - returns computed analysis
- **MUST** provide `GET /api/health` - health check endpoint

#### FR2.2: Prediction Endpoints
- **MUST** provide `GET /api/predictions/all` - pre-calculates all predictions
- **SHOULD** provide `POST /api/predictions/calculate` - on-demand prediction calculation
- **MUST** return predictions in JSON format with dates and balances

#### FR2.3: API Documentation
- **MUST** provide interactive API documentation at `/docs` (Swagger UI)
- **MUST** include request/response schemas
- **SHOULD** include example requests and responses
- **MUST** document all error responses

---

### FR3: Budget Breakdown Visualization

#### FR3.1: Pie Chart Display
- **MUST** display current budget breakdown by category
- **MUST** show percentages for each category
- **MUST** display category totals in currency format (£)
- **MUST** show hover tooltips with detailed information
- **SHOULD** support interactive legend (toggle categories)

#### FR3.2: Budget Details Table
- **MUST** display itemized budget entries
- **MUST** show: item name, schedule, cost, category
- **MUST** format costs as currency (£)
- **SHOULD** allow sorting by any column
- **SHOULD** support filtering by category

---

### FR4: Saving Analysis Visualization

#### FR4.1: Saving Rate Chart
- **MUST** plot actual saving rate over time
- **MUST** plot predicted saving rate over time
- **MUST** display rates in £/month
- **MUST** show hover tooltips with exact values
- **MUST** allow zoom and pan
- **SHOULD** support date range selection

---

### FR5: Predictions Visualization (Critical - Primary Focus)

#### FR5.1: Interactive Prediction Selection
- **MUST** allow user to click on any balance recording point
- **MUST** display prediction from clicked point to last recording
- **MUST** update prediction line **without page refresh** (client-side only)
- **MUST** preserve scroll position during updates
- **MUST** provide visual feedback for selected point
- **MUST** show current prediction start date and balance
- **MUST** complete prediction switch in <100ms

#### FR5.2: Daily Prediction Timeline
- **MUST** generate predictions for every day (not just month boundaries)
- **MUST** calculate predictions from selected start date
- **MUST** stop predictions at last recording date (no future extrapolation)
- **MUST** include actual last recording date in timeline

#### FR5.3: Chart Display
- **MUST** display actual balance line (blue, with markers)
- **MUST** display predicted balance line (orange, dotted)
- **MUST** render actual balance line on top of prediction line
- **MUST** show hover tooltips with date and amount
- **MUST** format currency values as £X,XXX.XX
- **MUST** display chart title showing current prediction start
- **SHOULD** support zoom, pan, and reset interactions

#### FR5.4: Pre-calculation Strategy
- **MUST** pre-calculate predictions for all balance recording points on initial load
- **MUST** store all predictions in client state
- **MUST** switch between pre-calculated predictions instantly (no API call)
- **MUST** show loading indicator during initial calculation
- **SHOULD** cache predictions in browser session

---

### FR6: Metrics Display

#### FR6.1: Summary Metrics
- **MUST** display current monthly budget total
- **MUST** display current monthly income total
- **MUST** display latest account balance
- **MUST** show dates associated with each metric
- **MUST** format all currency values consistently
- **SHOULD** show comparison to previous period

---

### FR7: Raw Data Access

#### FR7.1: Data Explorer
- **MUST** provide expandable section for raw data
- **MUST** display all budget files with dates
- **MUST** display all income files with dates
- **MUST** display complete balance record
- **SHOULD** allow data export (CSV/JSON)
- **SHOULD** support search/filter functionality

---

## Non-Functional Requirements

### NFR1: Performance

#### NFR1.1: Response Time
- **MUST** load initial page within 3 seconds
- **MUST** complete API requests within 500ms (p95)
- **MUST** switch between predictions within 100ms (client-side, zero API call)
- **MUST** complete initial prediction pre-calculation within 5 seconds
- **SHOULD** use HTTP/2 for API communication

#### NFR1.2: Scalability
- **MUST** handle up to 100 balance recording points
- **MUST** handle up to 50 budget files
- **SHOULD** maintain performance with 10 years of historical data
- **MUST** support concurrent API requests

#### NFR1.3: Resource Usage
- **SHOULD** keep backend memory usage under 500MB
- **SHOULD** keep JavaScript bundle size <2MB gzipped
- **MUST** implement code splitting for frontend routes
- **SHOULD** use lazy loading for chart components

---

### NFR2: User Experience

#### NFR2.1: Interactivity
- **MUST** provide zero-refresh interaction for prediction selection
- **MUST** preserve scroll position during all interactions
- **MUST** provide immediate visual feedback for user actions (<100ms)
- **SHOULD** include smooth transitions between states
- **SHOULD** implement optimistic UI updates

#### NFR2.2: Visual Design
- **MUST** maintain consistent color scheme (blue for actual, orange for predicted)
- **MUST** ensure charts are readable on screens 1024px and wider
- **SHOULD** support responsive design for tablet/mobile
- **SHOULD** use clear, accessible color contrasts (WCAG AA)
- **SHOULD** implement dark mode support

#### NFR2.3: Usability
- **MUST** provide clear instructions for interaction (e.g., "Click any blue point")
- **MUST** show current state (e.g., "Predicting from: 2024-12-10")
- **SHOULD** provide keyboard shortcuts for common actions
- **SHOULD** support browser back/forward navigation
- **MUST** display helpful error messages

---

### NFR3: Maintainability

#### NFR3.1: Code Quality
- **MUST** use type hints in Python code (mypy strict mode)
- **MUST** use TypeScript for React components (strict mode)
- **MUST** include unit tests for all calculation functions
- **SHOULD** achieve >80% test coverage for business logic
- **MUST** follow consistent code style (Black for Python, Prettier for TypeScript)
- **MUST** use ESLint for JavaScript/TypeScript linting

#### NFR3.2: Documentation
- **MUST** document all public functions and classes
- **MUST** include README with setup instructions
- **MUST** include architecture diagrams
- **MUST** document API contracts (OpenAPI/Swagger)
- **SHOULD** include development guide
- **SHOULD** include deployment guide

#### NFR3.3: Modularity
- **MUST** separate data loading, calculation, and API layers
- **MUST** allow easy addition of new chart types
- **SHOULD** support plugin architecture for new analysis types
- **MUST** use dependency injection where appropriate

---

### NFR4: Reliability

#### NFR4.1: Error Handling
- **MUST** handle missing CSV files gracefully
- **MUST** display user-friendly error messages
- **MUST** log errors for debugging
- **SHOULD** provide fallback behavior when calculations fail
- **MUST** validate API inputs with Pydantic models
- **SHOULD** implement retry logic for transient failures

#### NFR4.2: Data Integrity
- **MUST** validate CSV file formats
- **MUST** validate date parsing
- **MUST** handle edge cases (empty files, single data point, etc.)
- **SHOULD** detect and warn about data inconsistencies
- **MUST** return 4xx errors for invalid requests
- **MUST** return 5xx errors for server failures

---

### NFR5: Security

#### NFR5.1: API Security
- **MUST** implement CORS correctly
- **SHOULD** implement rate limiting
- **SHOULD** validate all inputs (prevent injection attacks)
- **SHOULD** implement API authentication (if deployed publicly)
- **MUST** use HTTPS in production

#### NFR5.2: Data Privacy
- **MUST** not expose sensitive financial data in logs
- **SHOULD** implement access controls if multi-user
- **MUST** sanitize error messages (no stack traces in production)

---

### NFR6: Deployment

#### NFR6.1: Environment
- **MUST** run on Linux (tested on Linux 6.12.58-1-lts)
- **MUST** support Python 3.13+
- **MUST** support Node.js 18+
- **SHOULD** provide Docker container option
- **SHOULD** include deployment documentation

#### NFR6.2: Dependencies
- **MUST** document all dependencies
- **MUST** pin dependency versions
- **SHOULD** minimize dependency count
- **MUST** use virtual environment for Python
- **MUST** use package-lock.json for Node.js

---

## Architecture Details

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│         React Frontend (TypeScript)                 │
│  - Create React App / Vite                          │
│  - React-Plotly.js for interactive charts           │
│  - Axios for HTTP requests                          │
│  - React Query for caching & state management       │
│  - TypeScript for type safety                       │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ HTTP/JSON REST API
                  │ (CORS enabled)
                  │
┌─────────────────▼───────────────────────────────────┐
│         FastAPI Backend (Python)                    │
│  - API routes & endpoints                           │
│  - Request/response validation (Pydantic)           │
│  - Business logic (calculations)                    │
│  - Data loading (CSV files)                         │
│  - Automatic API documentation (Swagger)            │
└─────────────────┬───────────────────────────────────┘
                  │
                  │ File I/O
                  │
┌─────────────────▼───────────────────────────────────┐
│         CSV Files (Data Storage)                    │
│  - budgets/YYYY-MM-DD-budget.csv                    │
│  - income/YYYY-MM-DD-income.csv                     │
│  - balence_record.csv                               │
└─────────────────────────────────────────────────────┘
```

### Project Structure

```
budgeting/
├── backend/                    # FastAPI application
│   ├── main.py                 # API entry point & routes
│   ├── models.py               # Pydantic request/response models
│   ├── config.py               # Configuration management
│   ├── calculations/           # Business logic
│   │   ├── __init__.py
│   │   ├── balance_analyzer.py
│   │   ├── calculations.py
│   │   └── loaders.py
│   ├── requirements.txt        # Python dependencies
│   └── tests/                  # Backend tests
│       ├── test_api.py
│       ├── test_calculations.py
│       └── conftest.py
│
├── frontend/                   # React application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── PredictionChart.tsx
│   │   │   ├── BudgetPieChart.tsx
│   │   │   ├── SavingRateChart.tsx
│   │   │   └── MetricsCard.tsx
│   │   ├── api/                # API client
│   │   │   └── client.ts       # Axios configuration
│   │   ├── types/              # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx             # Main app component
│   │   └── index.tsx           # Entry point
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   └── .env                    # Environment variables
│
├── data/                       # CSV data files
│   ├── budgets/
│   ├── income/
│   └── balence_record.csv
│
├── docker-compose.yml          # Docker orchestration
├── .gitignore
└── README.md                   # Setup & usage guide
```

### Technology Stack

**Backend:**
- **Framework:** FastAPI 0.104+
- **Language:** Python 3.13+
- **Data Processing:** Pandas 2.0+, NumPy 1.24+
- **Validation:** Pydantic 2.0+
- **Date Handling:** python-dateutil 2.8+
- **Server:** Uvicorn (ASGI server)
- **Testing:** pytest 7.0+, httpx (async client)

**Frontend:**
- **Framework:** React 18.2+
- **Language:** TypeScript 5.0+
- **Build Tool:** Vite 4.0+ or Create React App
- **Charting:** react-plotly.js 2.6+ (plotly.js 2.27+)
- **HTTP Client:** Axios 1.4+
- **State Management:** React Query 4.0+ (TanStack Query)
- **Styling:** CSS Modules or Tailwind CSS

**Development Tools:**
- **Package Manager:** npm 10+ / pnpm 8+
- **Python Env:** venv or poetry
- **Linting:** ESLint, mypy, Black, Prettier
- **Version Control:** git

---

## API Specification

### Core Endpoints

#### GET /api/health
**Description:** Health check endpoint
**Response:** `{ "status": "ok", "version": "1.0.0" }`

#### GET /api/balance
**Description:** Retrieve all balance records
**Response:**
```json
[
  {
    "date": "2024-06-15",
    "nationwide": 5000.00,
    "secure_trust": 1000.00,
    "monzo": 500.00,
    "revolut": 200.00,
    "total": 6700.00
  }
]
```

#### GET /api/budgets
**Description:** Retrieve all budget files
**Response:**
```json
[
  {
    "date": "2024-06-15",
    "items": [
      { "name": "Rent", "schedule": "monthly", "cost": 1200.00, "category": "Housing" }
    ],
    "total": 2500.00
  }
]
```

#### GET /api/predictions/all
**Description:** Pre-calculate predictions for all balance points
**Response:**
```json
[
  {
    "startDate": "2024-06-15",
    "startBalance": 5000.00,
    "timeline": {
      "dates": ["2024-06-15", "2024-06-16", ...],
      "balances": [5000.00, 5010.50, ...]
    }
  }
]
```

#### GET /api/balance-analysis
**Description:** Get complete balance analysis with metrics
**Response:**
```json
{
  "savingRate": 500.00,
  "averageMonthlySpending": 2000.00,
  "predictedVsActual": {
    "deficit": -150.00
  }
}
```

---

## Implementation Phases

### Phase 1: Backend Setup (4 hours)

**Tasks:**
1. Create FastAPI project structure
2. Set up virtual environment and dependencies
3. Migrate calculation logic from Streamlit to FastAPI
4. Implement core API endpoints
5. Add Pydantic models for validation
6. Set up CORS for frontend communication
7. Write unit tests for API endpoints
8. Test API with Swagger UI

**Deliverables:**
- Working FastAPI backend with all endpoints
- Automatic API documentation at `/docs`
- Unit tests passing

---

### Phase 2: Frontend Setup (3 hours)

**Tasks:**
1. Create React + TypeScript project (Vite/CRA)
2. Set up project structure and routing
3. Configure Axios for API communication
4. Set up React Query for data fetching/caching
5. Create base layout and navigation
6. Implement error boundaries
7. Configure TypeScript strict mode

**Deliverables:**
- React app with routing and API integration
- TypeScript types for API responses
- Error handling framework

---

### Phase 3: Core Visualizations (6 hours)

**Tasks:**
1. Implement Budget Breakdown tab (pie chart + table)
2. Implement Saving Analysis tab (line chart)
3. Implement Metrics cards (summary stats)
4. Implement Raw Data expander
5. Style components consistently
6. Add loading states and spinners
7. Implement responsive design

**Deliverables:**
- 3 out of 4 tabs fully functional
- Consistent styling and UX

---

### Phase 4: Predictions Tab (4 hours)

**Tasks:**
1. Implement PredictionChart component
2. Fetch all predictions on mount (React Query)
3. Implement click handler for balance points
4. Implement instant prediction switching (no API call)
5. Add visual feedback for selected point
6. Display current prediction info
7. Test performance with many data points

**Deliverables:**
- Fully interactive predictions with zero refresh
- Scroll position preserved
- Sub-100ms switching performance

---

### Phase 5: Testing & Polish (3 hours)

**Tasks:**
1. Test with real CSV data
2. Add integration tests
3. Fix bugs and edge cases
4. Improve error messages
5. Add loading skeletons
6. Optimize bundle size
7. Performance profiling and optimization

**Deliverables:**
- Stable, polished application
- All tests passing
- Performance benchmarks met

---

### Phase 6: Deployment (2 hours)

**Tasks:**
1. Create Dockerfile for backend
2. Create Dockerfile for frontend
3. Set up docker-compose for local development
4. Write deployment documentation
5. Configure production environment variables
6. Set up reverse proxy (if needed)

**Deliverables:**
- Deployment-ready application
- Complete deployment documentation

---

**Total Estimated Time: 22 hours**

---

## Success Criteria

The implementation is considered successful when:

1. ✅ User can click any blue point on predictions chart
2. ✅ Prediction line updates **instantly** (no page refresh, <100ms)
3. ✅ Scroll position remains **exactly** where it was
4. ✅ All tabs (Budget, Saving, Predictions, Raw Data) work correctly
5. ✅ API provides all required data via REST endpoints
6. ✅ All backend unit tests pass (>80% coverage)
7. ✅ Frontend is responsive and accessible
8. ✅ API documentation is complete and accurate
9. ✅ Performance benchmarks are met
10. ✅ Application can be deployed via Docker

---

## Risks & Mitigations

### Risk 1: CORS Configuration Issues
**Impact:** Medium
**Probability:** Low
**Mitigation:**
- FastAPI has excellent CORS middleware built-in
- Test CORS early in development
- Use proper CORS config for development vs production

### Risk 2: Large Data Performance
**Impact:** Medium
**Probability:** Medium
**Mitigation:**
- Implement pagination for large datasets
- Use React Query for efficient caching
- Add loading skeletons for better perceived performance
- Profile and optimize calculation algorithms

### Risk 3: TypeScript Learning Curve
**Impact:** Low
**Probability:** Low
**Mitigation:**
- TypeScript strict mode catches errors early
- Use auto-generated types from API responses
- Leverage IDE autocomplete and IntelliSense

### Risk 4: State Management Complexity
**Impact:** Low
**Probability:** Low
**Mitigation:**
- Use React Query (handles most state automatically)
- Keep local state minimal
- Avoid complex state management libraries (Redux not needed)

### Risk 5: Deployment Complexity
**Impact:** Medium
**Probability:** Low
**Mitigation:**
- Use Docker for consistent deployments
- Document deployment process thoroughly
- Test in production-like environment

---

## Future Enhancements

**Phase 2 Features (Post-MVP):**
- Database migration (PostgreSQL/SQLite) instead of CSV
- User authentication and multiple accounts
- Data export functionality (CSV, PDF reports)
- Mobile responsive design
- Dark mode support
- Budget forecasting with ML
- Automated CSV import (watch folder)
- Email/push notifications for milestones
- Comparison views (month-over-month)
- Custom date range selection

---

## Appendix A: Why FastAPI?

### Technical Justification

**Performance:**
- Async/await support (handles concurrent requests efficiently)
- ~3x faster than Flask for I/O-bound operations
- Built on Starlette (high-performance ASGI framework)

**Developer Experience:**
- Automatic API documentation (Swagger UI + ReDoc)
- Type hints throughout (catches errors at development time)
- Pydantic validation (automatic request/response validation)
- Modern Python (leverages latest language features)

**Ecosystem:**
- Active development and community
- Excellent documentation
- Wide adoption in industry
- Production-ready (used by Microsoft, Uber, Netflix)

**Compatibility:**
- Works with existing Pandas/NumPy code
- Easy migration from Streamlit logic
- No major rewrites needed for calculations

---

## Appendix B: Data Flow

### Initial Page Load

```
User → Frontend → GET /api/predictions/all → Backend
                                           ↓
                                    Load CSVs
                                           ↓
                                    Calculate all predictions
                                           ↓
Frontend ← JSON response (all predictions) ← Backend
   ↓
Cache in React Query
   ↓
Render chart (default: second-to-last point)
```

### User Clicks Balance Point

```
User clicks blue point → React event handler
                              ↓
                      Update local state (selectedIndex)
                              ↓
                      Switch visible prediction line
                              ↓
                      Re-render chart (instant, <100ms)
                              ↓
                      NO API CALL - purely client-side
```

---

## Questions for Decision Making

Before proceeding, confirm:

1. ✅ **Ready for complete rewrite?** (vs. hybrid Streamlit approach)
2. ✅ **Comfortable with 22-hour time investment?** (vs. 6-hour hybrid)
3. ✅ **Want fully decoupled frontend/backend?** (vs. Streamlit coupling)
4. ✅ **Need professional, scalable architecture?** (vs. simple solution)
5. ✅ **Willing to learn React + TypeScript basics?** (if not familiar)

If all answers are yes → **Proceed with FastAPI + React**

If #1-2 are no → Consider hybrid Streamlit + React component approach

If #5 is no → May need additional time for learning

---

## Approval & Next Steps

**Decision:** Proceed with **FastAPI + React** complete rewrite

**Estimated Timeline:** 22 hours over 3-4 days

**Next Actions:**
1. [ ] Set up backend project structure
2. [ ] Implement FastAPI endpoints
3. [ ] Set up frontend React project
4. [ ] Begin Phase 1 implementation
5. [ ] Schedule progress reviews after each phase

---

**Document Version:** 2.0
**Last Updated:** 2025-11-24
**Status:** Approved - Ready for Implementation
