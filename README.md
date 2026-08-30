# Skylark Drones Business Intelligence Agent

## Overview

A conversational Business Intelligence agent that connects to
Monday.com and provides founder-level insights across Deals and
Work Orders.

The system retrieves data dynamically from Monday.com rather than
hardcoding the supplied CSV data.

## Features

- Monday.com API integration
- Deals and Work Orders analysis
- Sales pipeline analysis
- Sector-level analysis
- Billing and receivables analysis
- Cross-board customer analysis
- Data-quality reporting
- Leadership updates
- Streamlit conversational interface
- Graceful handling of missing data

## Architecture

User
↓
Streamlit UI
↓
Question Handler
↓
Business Analytics
↓
Monday.com API
↓
Deals + Work Orders

## Technology

- Python
- Pandas
- Streamlit
- Monday.com API
- REST/GraphQL API integration

## Setup

Create a virtual environment:

```bash
python -m venv venv