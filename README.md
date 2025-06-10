# 🧭 OBI Tracker

**OBI Tracker** is a lightweight desktop application that visually monitors the **Order Book Imbalance (OBI)** and **delta** for various cryptocurrency trading pairs in real-time. It's designed for active traders who want a quick, clean overview of market dynamics using Binance data.

<p align="center">
  <img src="screenshot.png" alt="OBI Tracker Screenshot" width="600">
</p>

---

## 🚀 Features

- 📊 Displays OBI and Delta (Δ) for multiple trading pairs
- ⚡ Real-time updates (via Binance WebSocket or REST)
- 🖼️ Logo display for each asset (with fallback icons)
- 💡 Clean, dark-themed grid UI
- ✅ Color-coded metrics:
  - Green for positive Δ
  - Red for negative Δ

---

## 📦 Installation

### Requirements

- Python 3.8+
- `PyQt5` or `PySide6`
- `websockets`, `requests`, or `binance` client (depending on data source)

### Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/obi-tracker.git
   cd obi-tracker
