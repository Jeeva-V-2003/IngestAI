📘 IngestAI

An intelligent end-to-end web scraper powered by AI that extracts data from webpages via HTML parsing and OCR, summarizes it intelligently using LM Labs, merges duplicates, and exports to a structured Excel sheet.

---

1. Installation of Dependencies

Requirements:

* Python 3.10 or newer
* pip

Install All Required Packages:

Run this batch file to install everything automatically:


install_dependencies.bat


This will:

* Install all Python packages from requirements.txt
* Install Playwright browsers with:


playwright install


---

2. LM Labs Setup (for AI Summarization & Merging)

We use *LM Studio* (LM Labs) to run local LLMs like LLaMA or Mistral. Here’s how to set it up:

Step 1: Download LM Studio

* Go to: [https://lmstudio.ai](https://lmstudio.ai)
* Download and install for Windows / Mac / Linux

Step 2: Download the Model

* Open LM Studio
* Go to Settings → Model Search
* Search: meta-llama-3.1-8b-instruct
* Download the quantized model (Q4\_K\_M or Q5\_K\_M)

Step 3: Start the Server

* Go to the Server tab
* Press Ctrl + R to start the local OpenAI-compatible API
* Note the default URL: http://localhost:1234

Optional: Tweak Hardware Settings

* Go to Settings > Load Settings
* Choose your GPU/CPU configuration for optimized performance

> LM Studio runs fully offline after setup!

---

3. Running the Program

Method : With Graphical UI

Double-click the file:

bat
run_ui.bat


This opens the stylish PyQt5 app UI.

> Output Excel files will be saved to: outputs/excels/

---

4. Further Updates Coming Soon

*  Batch URL support (upload multiple URLs at once)
*  Live preview of OCR/screenshot in UI
*  Export as PDF/HTML in addition to Excel
*  Build a mobile-style compact UI
*  Add self-learning summarizer for fine-tuning output
*  Convert to EXE for portable deployment

Stay tuned!

---

Developed by Jeeva V

Contact: jeevavincent.2003@gmail.com