# Skylark BI Agent

## Monday.com Business Intelligence Agent

A conversational Business Intelligence (BI) agent built for the Skylark Drones full-stack assignment. The system connects directly to Monday.com boards containing **Deal Funnel** and **Work Order Tracker** data, performs deterministic analytics, handles incomplete data, and uses an AI model to convert the results into concise founder-level answers.

## 1. Project Objective

The objective is to build an AI-powered Business Intelligence Agent that allows founders and executives to ask natural-language questions about business data stored in Monday.com.

Example:

> How's our pipeline looking for the energy sector this quarter?

The agent retrieves the required data dynamically from Monday.com, cleans and normalizes it, determines which business data is relevant, performs the required calculations, and generates a concise response.

The implementation addresses:

- Monday.com integration
- Dynamic data retrieval
- Data cleaning and normalization
- Missing/null data handling
- Natural-language query understanding
- Business Intelligence calculations
- Cross-board analysis
- Conversational responses
- API/error handling
- Hosted deployment

## 2. Hosted Application

**Frontend:** https://skylark-bi-agent-1-hc9a.onrender.com  
**Backend API:** https://skylark-bi-agent-xs94.onrender.com

## 3. High-Level Architecture

```text
User / Founder
     |
     v
React + Vite Frontend
     |
     | POST /chat
     v
FastAPI Backend
     |
     +------------------+
     |                  |
     v                  v
Query Router       Monday API Client
     |                  |
     |                  v
     |            Monday.com
     |             /       \
     |       Deal Funnel  Work Orders
     |             \       /
     +--------------+-----+
                    |
                    v
             Data Cleaning
                    |
                    v
          Deterministic Analytics
                    |
                    v
              AI Agent
          Groq / GPT-OSS 20B
                    |
                    v
           Founder-level Answer
```

## 4. Method of Approach

### Step 1 — Connect to Monday.com

The backend connects to Monday.com's GraphQL API using a read-only API token. Two boards are used:

1. `Deal funnel Data`
2. `Work_Order_Tracker Data`

Data is retrieved dynamically at runtime rather than using a hardcoded CSV.

### Step 2 — Retrieve Board Data

The Monday GraphQL API retrieves item IDs, item names, column IDs, column text values, and raw values.

Example query:

```graphql
query ($board_id: ID!) {
  boards(ids: [$board_id]) {
    id
    name
    items_page(limit: 500) {
      items {
        id
        name
        column_values {
          id
          text
          value
        }
      }
    }
  }
}
```

### Step 3 — Clean and Normalize Data

The `data_cleaner.py` module:

- Converts empty strings to `None`.
- Removes unnecessary whitespace.
- Preserves valid values.
- Keeps missing values so they can be reported.

### Step 4 — Map Monday Column IDs

Raw Monday column IDs are mapped to business-friendly names such as:

```text
numeric_mm7bbz6a -> deal_value
date_mm7bcmha    -> close_date
color_mm7bdhg3   -> sector
```

This keeps analytics independent of raw Monday column IDs.

### Step 5 — Route the User's Question

`query_router.py` classifies questions into:

```text
deals
work_orders
both
```

Examples:

| User Question | Route |
|---|---|
| How is our pipeline? | Deals |
| What is our receivable? | Work Orders |
| How much has been collected? | Work Orders |
| Compare sales pipeline and operations | Both |
| Give me an overall business summary | Both |

The current implementation uses deterministic routing and falls back to both datasets for ambiguous questions.

### Step 6 — Perform Deterministic Business Analytics

Business calculations are performed in Python before the AI response is generated. The LLM is not the source of truth for numerical calculations.

#### Deal Analytics

- Total deals
- Open deals
- Pipeline value
- Open deals by sector
- Deal-stage distribution
- Missing-value/data-quality counts

#### Work Order Analytics

- Total work orders
- Active work orders
- Total billed value
- Total collected amount
- Amount receivable
- Missing-value/data-quality counts

#### Cross-Board Analytics

- Open deals by sector
- Active work orders by sector
- Sales pipeline versus operational activity

## 5. Data Resilience

The assignment requires incomplete business data to be handled gracefully. The application therefore does not assume every field is populated.

Missing values are retained and summarized instead of being silently discarded. The AI is instructed to communicate relevant data-quality limitations rather than presenting incomplete information as complete.

Examples of fields containing missing values in the current data include Deal Close Date, Closure Probability, Deal Value, Sector, and several Work Order fields.

## 6. Date-Based Queries

The analytics layer includes date parsing and filtering for:

- `YYYY-MM-DD`
- `DD-MM-YYYY`
- `DD/MM/YYYY`
- `MM/DD/YYYY`

Deal pipeline date filtering currently uses **Tentative Close Date**.

The system can calculate date-specific pipeline metrics when matching dates are available. If the current period has no matching dates, the system returns the actual result rather than inventing data.

## 7. AI Agent

The response layer uses the Groq OpenAI-compatible API with:

```text
Model: openai/gpt-oss-20b
```

The AI receives structured business data calculated by the backend.

The prompt instructs the model to:

- Use only provided business data.
- Never invent values.
- Use backend-calculated metrics.
- Avoid unsupported assumptions.
- Preserve data-quality caveats.
- Keep Deal and Work Order datasets separate unless a cross-board metric is supplied.
- Avoid exposing internal reasoning.
- Produce concise founder-level responses.

Therefore, the AI primarily performs business-language interpretation and response generation, while Python performs the core calculations.

## 8. Conversational Interface

The frontend uses React, Vite, and CSS. The user enters a natural-language question and the frontend sends it to:

```http
POST /chat
```

The backend returns the answer and relevant processing information.

## 9. Monday.com Configuration

Environment variables:

```env
MONDAY_API_TOKEN=your_monday_api_token
DEALS_BOARD_ID=your_deals_board_id
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
```

The actual API token must never be committed to GitHub.

## 10. Environment Variables

```env
MONDAY_API_TOKEN=
DEALS_BOARD_ID=
WORK_ORDERS_BOARD_ID=
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
```

## 11. Project Structure

```text
skylark-bi-agent/
├── backend/
│   ├── main.py
│   ├── monday_client.py
│   ├── data_cleaner.py
│   ├── analytics.py
│   ├── ai_agent.py
│   ├── query_router.py
│   ├── test_ai.py
│   ├── requirements.txt
│   ├── Procfile
│   └── .gitignore
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── App.css
    ├── package.json
    └── .gitignore
```

## 12. Backend API Endpoints

### Health Check

```http
GET /
```

### Deal Data

```http
GET /data/deals
```

### Work Order Data

```http
GET /data/work-orders
```

### Deal Analytics

```http
GET /analytics/deals
```

### Work Order Analytics

```http
GET /analytics/work-orders
```

### Conversational BI

```http
POST /chat
```

Example:

```json
{
  "question": "How is our sales pipeline looking?"
}
```

## 13. Error Handling

The application handles:

- Monday.com API errors
- Missing configuration
- AI service failures
- Invalid backend requests
- Frontend HTTP errors
- Incomplete business data

The frontend displays backend errors rather than silently failing.

## 14. Deployment

### Backend — Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Frontend — Render Static Site

Build command:

```bash
npm run build
```

Publish directory:

```text
dist
```

## 15. Technology Stack

| Component | Technology |
|---|---|
| Frontend | React |
| Build Tool | Vite |
| Backend | FastAPI |
| Language | Python |
| Business Analytics | Python |
| Data Source | Monday.com |
| Integration | Monday GraphQL API |
| AI API | Groq |
| AI Model | GPT-OSS 20B |
| Hosting | Render |
| Version Control | Git + GitHub |

## 16. Architectural Decisions

### Deterministic analytics before AI

Numerical calculations such as pipeline value, billed amount, collected amount, and receivables are calculated by Python. This improves reproducibility and reduces numerical hallucination.

### Rule-based query router

The assignment has clear business domains: Deals, Work Orders, and cross-board questions. A lightweight router is fast, predictable, and avoids unnecessary AI requests for simple intent classification.

### API-based Monday integration

The assignment requires dynamic Monday.com data rather than hardcoded CSV files. The application therefore reads the configured boards at runtime.

### Groq

Groq provides a fast OpenAI-compatible interface suitable for a responsive conversational prototype.

### Render

Render provides a straightforward way to host both the FastAPI backend and React frontend, satisfying the hosted-prototype requirement.

## 17. Security Considerations

- Monday API token is stored in environment variables.
- Groq API key is stored in environment variables.
- `.env` is excluded from Git.
- Credentials are not embedded in frontend code.
- Monday access is used for read-only data retrieval.

## 18. Current Data Snapshot

At the time of development/testing:

### Deal Funnel

```text
Total Deals: 346
Open Deals: 49
Pipeline Value: 688,152,293.1748
```

### Work Orders

```text
Total Work Orders: 176
Active Work Orders: 59
Total Billed: 126,719,936.37383
Total Collected: 90,428,187.50384
Amount Receivable: 36,291,748.8714228
```

These values are dynamic and may change as Monday.com is updated. The monetary fields are masked in the provided assignment data, so the application does not assume a currency.

## 19. Known Limitations

### Natural-language clarification

The current implementation uses deterministic routing and a fallback to both datasets for ambiguous queries. A future version can explicitly ask follow-up questions when the intent, date range, sector, or metric is unclear.

### Advanced trend analysis

The current implementation focuses on the required business metrics. Future versions could add month-over-month trends, quarter-over-quarter trends, forecasting, conversion rates, and sector trends.

### Authentication

The hosted prototype is intended for demonstration. A production system should include authentication, role-based access, and secure session management.

### Caching

Caching could reduce repeated Monday.com API calls while maintaining acceptable freshness.

### Leadership updates

A dedicated automated leadership-update workflow was not implemented within the assignment time constraint. The existing structured analytics can be extended to generate concise leadership summaries.

## 20. Future Improvements

1. Advanced semantic query understanding
2. Automatic clarification questions
3. Flexible date-range interpretation
4. Sector/customer trend analysis
5. Revenue forecasting
6. Pipeline conversion analysis
7. Automated leadership reports
8. Scheduled executive summaries
9. Authentication and role-based access
10. Caching/background synchronization
11. Automated analytics/API tests
12. Additional Monday.com boards
13. Visualization dashboards
14. Exportable reports
15. Audit logs

## 21. Assignment Requirement Mapping

| Assignment Requirement | Implementation |
|---|---|
| Monday.com integration | Monday GraphQL API |
| Read both boards | Deal Funnel + Work Order Tracker |
| Dynamic retrieval | Monday API at runtime |
| No hardcoded CSV dependency | Live board retrieval |
| Missing/null handling | Data cleaner + quality summaries |
| Date normalization | `parse_date()` |
| Query understanding | Query router |
| Founder-level questions | Conversational `/chat` interface |
| Pipeline analytics | Deterministic analytics |
| Operational metrics | Work Order analytics |
| Cross-board analysis | Combined analytics |
| AI response | Groq + GPT-OSS 20B |
| Error handling | Backend + frontend handling |
| Hosted prototype | Render |
| Source code | GitHub |
| README | This document |

## 22. Running Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` with the required credentials and IDs, then run:

```bash
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 23. Example Questions

### Deal Questions

```text
How is our sales pipeline looking?
How many open deals do we have?
What are the current deal stages?
What is the pipeline value?
```

### Work Order Questions

```text
How much have we collected?
What is the amount receivable?
How many active work orders are there?
What is our billed value?
```

### Cross-Board Questions

```text
Compare our sales pipeline with operational activity.
Show me the relationship between deals and work orders.
Give me an overall business summary.
```

## 24. Repository Safety

Do not commit:

```text
.env
node_modules/
dist/
__pycache__/
*.pyc
```

API keys and credentials must remain in environment variables.

## 25. Conclusion

The Skylark BI Agent provides a hosted conversational interface over live Monday.com business data.

The architecture separates:

```text
Data Retrieval
      ↓
Data Cleaning
      ↓
Query Routing
      ↓
Deterministic Analytics
      ↓
AI Interpretation
      ↓
Founder-Level Response
```

This provides a practical balance between reliability, speed, explainability, and conversational usability while satisfying the core requirements of the Monday.com Business Intelligence Agent assignment.
