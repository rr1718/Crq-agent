# CRQ Agent

This project contains a Cyber Risk Quantification (CRQ) agent designed to automate and assist in the CRQ process.

## Prerequisites

- Python 3.10 or higher

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd 14.012-crq-agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *On Windows, use `venv\Scripts\activate`*

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your environment variables:**
    -   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    -   Open the `.env` file and add your API keys for the Google and NVD services.

## How to Run the Agent

To start the CRQ agent, run the `main.py` script:

```bash
python main.py
```

The agent will begin the CRQ process with a predefined scenario ("Start the CRQ process for a data breach scenario.") and log its progress and final report location to the console.

## Project Structure

-   `main.py`: The main entry point to run the CRQ agent.
-   `web.py`: (Placeholder) Intended for a future web interface.
-   `.env`: Contains the API keys and other secrets. (Ignored by Git).
-   `.env.example`: An example file for the environment variables.
-   `requirements.txt`: A list of all the Python libraries required for the project.
-   `crq_agent/`: The core directory for the agent.
    -   `agent.py`: Defines the root agent and its main functionalities.
    -   `sub_agents/`: Contains specialized agents for different tasks within the CRQ workflow (e.g., vulnerability intelligence, risk scoping).
    -   `tools/`: Holds the tools and utilities the agent can use.
-   `Security Manifesto.md`: Outlines the security principles for the development of this agent.
