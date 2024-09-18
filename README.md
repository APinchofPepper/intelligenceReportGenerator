# Automated Intelligence Report Generator

This project automates the daily generation of intelligence reports by scraping and summarizing news articles from sources like Yahoo News. Using Python, machine learning models, and scheduling tools, it generates concise summaries of relevant news articles, making it easier to stay informed.

## Features

- **News Scraping**: Fetches news articles from selected RSS feeds or websites.
- **Article Summarization**: Uses the HuggingFace `transformers` library to generate concise summaries of news articles.
- **Daily Automation**: Automatically runs each morning using macOS Automator or terminal scheduling tools.
- **Browser Output**: Summaries are pushed directly to the web browser for easy access.
- **CSV Export**: Summarized articles are saved to a CSV file for future reference.

## Installation

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/your-username/Intelligence-Report-Generator.git
    ```

2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure the Summarizer Model**:
   - The project uses the `distilbart-cnn-12-6` model from HuggingFace. Ensure it's installed:

    ```bash
    pip install transformers
    ```

4. **Set Up Cron or Automator**:
   - To run the script daily, you can either use `launchctl` on macOS or set it up with Automator.

## Usage

### Running the Script Manually

You can run the main script manually using:

```bash
python run_daily.py
