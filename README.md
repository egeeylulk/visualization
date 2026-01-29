# BedFlow Diagnostic Dashboard

This project is a data visualization application built with Python and Dash, designed to analyze and diagnose hospital bed flow issues. It implements a structured workflow: Locate → Diagnose → Validate → Explain.

## Project Overview

The dashboard consists of three coordinated views:

1.  **Problem Locator (Heatmap)**: Identified bottlenecks and high-traffic areas.
2.  **Diagnostic Decomposition (Multi-factor Timeline)**: Analyzes trends over time across multiple factors.
3.  **Impact Validation (Morale & Satisfaction)**: Correlates operational metrics with staff and patient satisfaction.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

## Installation & Setup

1.  **Clone the repository** (or download the source code):

    ```bash
    git clone <repository-url>
    cd visualization
    ```

2.  **Create a virtual environment (Optional but recommended):**
    - On macOS/Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
    - On Windows:
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  Start the Dash server by running the main entry script:

    ```bash
    python app.py
    ```

2.  Open your web browser and navigate to the local server address shown in the terminal (usually `http://127.0.0.1:8050/`).

## Usage Guidelines

- Use the **Sidebar Menu** to filter data or navigate sections.
- Interact with the **Heatmap** to identify specific problem areas.
- Analyze the **Timeline** to see how metrics evolve.
- Check the **Impact Validation** view to understand the human side of the data.
