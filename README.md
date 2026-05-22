# Hermes Engineering Crew

Hermes Engineering Crew is a multi-agent AI engineering assistant that analyzes GitHub repositories using specialized engineering agents coordinated by a Hermes orchestrator.

## Features

- GitHub repository ingestion
- Security analysis agent
- Hermes orchestration workflow
- Structured engineering reports
- Async FastAPI backend

## Architecture

User Repo
→ Hermes Orchestrator
→ Specialized Engineering Agents
→ Final Engineering Report

## Current MVP

- GitHub Loader ✅
- Security Agent ✅
- Hermes Orchestrator ✅
- Structured Report Schema ✅

## Tech Stack

- Python
- FastAPI
- AsyncIO
- Hermes-style orchestration
- Gemma-ready architecture

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
