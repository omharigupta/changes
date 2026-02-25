# Datasynth Chat App

A business intelligence chat application with URL scraping, AI analysis, and knowledge base management.

## Features

- **Dual Input Modes**:
  - Paste URL → Auto-scrape business data → Summarize
  - Conversational flow with guided questions
  
- **Side-by-side Knowledge Base**: Real-time reflection of extracted business understanding, objectives, and constraints

- **Tech Stack**:
  - React + Vite
  - Gemini AI (1.5 Flash)
  - In-memory storage (expandable to ChromaDB)

## Quick Start

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open browser at `http://localhost:3000`

## Usage

- Start chatting about your business
- Paste a URL to scrape business data
- Knowledge base updates automatically in the right panel
- Edit and save insights

## Environment

The `.env` file is already configured with the Gemini API key.
