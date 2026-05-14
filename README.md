# 🏠 AI-Powered Smart Home Digital Twin

A next-generation, high-performance Smart Home operating system. This project features a live spatial UI (SVG floorplan), real-time energy & economics tracking, and a text/voice AI Assistant powered by **Google Gemini 2.5 Flash** that translates natural language into physical hardware actions.

<!-- ![Smart Home Dashboard](https://img.shields.io/badge/Status-Active-brightgreen) ![Tech Stack](https://img.shields.io/badge/Stack-Tailwind%20%7C%20FastAPI%20%7C%20Gemini-blue) -->

## ✨ Core Features

### 🧠 The "Jarvis" AI Command Terminal
*   **Natural Language Control:** Type or speak commands like *"I'm going to bed, turn off the TV and lock the doors."*
*   **Structured AI Execution:** Uses Google Gemini 2.5 Flash via FastAPI to parse intent and return structured JSON actions to physically toggle UI elements.
*   **Context Aware:** The AI reads the live state of the house (temperatures, active devices) before making decisions.

### 🗺️ Live Spatial Floorplan (Digital Twin)
*   **Interactive SVG Map:** Clickable zones for the Living Room, Bedroom, Kitchen, and Bathroom.
*   **Real-Time Animations:** Visual feedback for device states (e.g., animated blue waves for AC, pulsing orange glows for space heaters, spinning fan blades).
*   **Smart Security Visuals:** A dynamic padlock icon on the main entrance that physically animates and changes color based on lock status.

### 💶 Real-Time Grid Economics Engine
*   **Live Cost Tracking:** Calculates exactly how much money the home is spending (or earning) per hour.
*   **Adjustable Tariffs:** Input your local Buy (€/kWh) and Solar Sell (€/kWh) rates to instantly update the dashboard math.
*   **Solar Savings:** Tracks "invisible" money saved by routing solar power directly into the home.

### 🎬 Intelligent Scene Engine (Macros)
Trigger massive environmental shifts with a single click or AI command:
*   🌙 **Night Mode:** Secures the Smart Lock, powers down the TV, closes shades, and sets the bedroom AC to sleep temperature.
*   🚶 **Away Mode:** Locks all doors, turns off all climate control, and powers down the house to save maximum energy.
*   🍿 **Movie Mode:** Dims ambient lighting, turns on LED bias strips, powers the TV, and sets a cool 21°C environment.
*   🌅 **Morning Mode:** Opens all motorized shades to let in natural light and restores standard house functions.

### 📊 Advanced Data Analytics
*   **Interactive Dashboards:** Built with Chart.js to track live Wattage, Solar Yield, and Load Distribution.
*   **Expandable Modals:** Click on the 7-Day Analytics preview card to launch an immersive, full-screen data view.

---

## 🛠️ Technology Stack

**Frontend (The Body)**
*   HTML5 & CSS3
*   Tailwind CSS (Dark Mode & Glassmorphism UI)
*   Vanilla JavaScript (State management & DOM manipulation)
*   Chart.js (Telemetry visualization)

**Backend (The Brain)**
*   Python 3.x
*   FastAPI & Uvicorn (High-speed asynchronous API)
*   Google Generative AI SDK (Gemini 2.5 Flash)
*   `python-dotenv` (Enterprise-grade API key security)

---

## 🚀 Installation & Setup

### 1. Backend Setup
Navigate to the `backend` folder and install the required Python libraries:
```bash
pip install fastapi uvicorn google-generativeai python-dotenv