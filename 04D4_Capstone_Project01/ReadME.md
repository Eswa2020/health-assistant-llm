# AfyaPlus Triage Engine - Week 1 Capstone

## Overview

A production-ready medical triage engine that processes unstructured patient messages through AI, extracts structured triage data, and routes patients to appropriate care pathways. Features dual-pathway architecture (cloud + local fallback) with defensive prompt engineering.

## Business Problem

AfyaPlus Health serves rural communities in Kenya where patients send unstructured SMS messages describing symptoms. The backend requires machine-readable structured data for automated routing. Initial prototypes failed due to:
- Conversational fluff in AI responses
- Clinical hallucinations (fake diagnoses)
- System crashes during network outages

## Architecture

```mermaid
flowchart TD
    A[Patient Message SMS/Text] --> B[Triage Engine app.py]
    B --> C{☁️ Cloud Pathway<br/>GPT-4o-mini<br/>4s timeout}
    C -->|Success| E[🛡️ Defensive Prompt<br/>Role + CoT + Guardrails]
    C -->|Fail/Timeout| D[💻 Local Pathway<br/>Ollama/Llama3.2<br/>10s timeout]
    D --> E
    E --> F[📋 Structured JSON Output]
    F --> G{Routing Decision}
    G -->|Critical| H[🚑 Ambulance Dispatch]
    G -->|Urgent| I[🏥 Clinic Appointment]
    G -->|Routine| J[🏠 Home Care]
    
    style C fill:#e1f5fe
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#e8f5e9
    style H fill:#ff5252,color:#fff
    style I fill:#ff9800,color:#fff
    style J fill:#4caf50,color:#fff
    
## Prompt Engineering Evolution

### Version 1: Naive Zero-Shot
