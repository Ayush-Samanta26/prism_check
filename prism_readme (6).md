# 🎨 Prism

> **See Beyond the Information. Discover Reality — An AI-powered verification platform that helps creators and everyday users detect fake, misleading, and manipulated content with transparent evidence before sharing.**

🏆 **Hackathon:** GeNarrative Clash 2026 (Open Track)

🔗 **Live Prototype:** [Prism App Preview](https://prism-factcheck--76p5r4m4.preview.emergentagent.com/)

💻 **GitHub Repository:** [Ayush-Samanta26 GitHub](https://github.com/Ayush-Samanta26-)

🎥 **Public Demo Video:** [Watch the 2–4 Minute Prototype Walkthrough](https://youtu.be/4g9CaXvF99k?si=Ey8kouzx6MqxNQoN)

## 💡 Problem & Solution

Misleading claims, edited images, and deepfake videos spread rapidly across social platforms like Instagram, Facebook, and WhatsApp, leaving creators and everyday users struggling to verify authenticity through tedious manual cross-referencing.

**Prism** solves this by accepting multi-format inputs—raw text, image URLs, video uploads, and suspicious links—and delivering clear, evidence-backed verdicts, probabilistic confidence scores, and verifiable source citations.

## 🏗️ System Architecture

```
[ User Input: Text / Image URL / Video / Link ]
                      │
                      ▼
       [ React.js Frontend Interface ]
                      │
                      ▼
     [ Node.js + Express API Gateway ]
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
 [ NLP Claim ]  [ OpenCV Image ] [ Fact-Check ]
 [ Extraction ] [  Forensics   ] [  DB APIs   ]
  (FastAPI)        (FastAPI)      (External)
        │             │             │
        └─────────────┼─────────────┘
                      ▼
   [ Confidence Engine & Nuance Handler ]
                      │
                      ▼
[ Verifiable Verdict + Citations + Audit Card ]
```

## ⚖️ 50/50 Build Plan

**✅ Completed (50% Pre-Build):**

* Responsive UI wireframes and interactive frontend layout built in React.js

* Core system architecture and multi-format input workflows established

* Initial AI verification prompt templates and nuance-handling logic ("Unable to Verify") tested

**🚧 To Be Built Live (50% Offline Sprint):**

* Connecting live NLP claim extraction and OpenCV image forensic microservices via Python/FastAPI

* Integrating real-time global fact-checking database APIs and citation indexing

* Finalizing audit report export and shareable verification cards

## 🧠 AI & Tech Stack

* **AI / LLMs:** NLP / ML Models (Contextual & Claim Analysis), OpenCV (Digital Image Manipulation Detection), Multilingual Code-Mixed NLP (English, Bengali, Hindi)

* **Frontend:** React.js, HTML5, CSS3, JavaScript

* **Backend & Microservices:** Node.js + Express (API Gateway), Python + FastAPI

* **Data & Verification:** Global Fact-Checking APIs

## ⚙️ Local Setup Instructions

Follow these steps to run the current 50% MVP locally:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Ayush-Samanta26-.git
   cd prism
   ```

2. **Install frontend dependencies:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm start
   ```

4. **Open in browser:**
   Navigate to `http://localhost:3000` to explore the prototype.

## 🎥 Demo & Pre-Build Preview

* **Video Walkthrough:** [Watch on YouTube](https://youtu.be/4g9CaXvF99k?si=Ey8kouzx6MqxNQoN)

## 👥 Team

* **Avirup Dasgupta** – Team Leader

* **Ridhima Mukherjee** – Team Member

* **Debarpan Biswas** – Team Member

* **Ayush Samanta** – Team Member