# **IntelliPart User Guide**

## **1. Overview**
Welcome to IntelliPart, your AI-powered conversational assistant for automotive parts. This guide will help you get the demo up and running quickly.

---

## **2. How to Run the Demo**

Running the IntelliPart demo is a simple one-step process.

**Prerequisites:**
*   You have Python installed.
*   You have opened a terminal (like PowerShell or Command Prompt) in the project's root directory.

**Step 1: Install Dependencies**

First, install the necessary Python packages by running:
```bash
pip install -r requirements.txt
```
This command reads the `requirements.txt` file in the main project directory and installs all required libraries, such as Flask, sentence-transformers, and faiss-cpu.

**Step 2: Launch the Demo**

Once the dependencies are installed, run the launcher script:
```bash
python launch_demo.py
```

**What to Expect:**
1.  The script will start the backend Flask server in a new terminal window. You will see log messages indicating the server is running.
2.  Your default web browser will automatically open to `http://127.0.0.1:5000`.
3.  The IntelliPart conversational interface will be ready to use.

---

## **3. Using the Application**

*   **Ask a Question:** Type your question about a car part into the search box (e.g., "I need a brake pad for a Scorpio with high durability").
*   **Suggested Queries:** Click on any of the "Suggested Queries" buttons to see pre-made examples.
*   **Conversational Search:** The assistant will provide an intelligent, summarized answer along with a list of matching parts from the database.
*   **Technical Specs:** Key technical specifications in the results are highlighted for easy identification.

---

## **4. Stopping the Application**

To stop the demo, simply close the terminal window where the Flask server is running, or press `Ctrl+C` in that window.

---

Enjoy exploring IntelliPart!
