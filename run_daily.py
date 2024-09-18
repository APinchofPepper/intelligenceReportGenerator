import subprocess
import pandas as pd
import os

def generate_summary():
    summary_file = '/Users/jackmustonen/summary.html'
    with open(summary_file, 'w') as file:
        file.write("<html><head><title>Summary of Important Articles</title></head><body>")
        file.write("<h1>Summary of Important Articles</h1>")
        try:
            df = pd.read_csv('/Users/jackmustonen/Intelligence Report Generator/important_articles.csv')
            if 'summary' in df.columns:
                for _, row in df.iterrows():
                    file.write(f"<h2>Title: {row['title']}</h2>")
                    file.write(f"<p>Link: <a href='{row['link']}'>{row['link']}</a></p>")
                    file.write(f"<p>Summary: {row['summary']}</p>")
                    file.write("<hr>")
            else:
                file.write("<p>'summary' column not found in DataFrame.</p>")
        except FileNotFoundError:
            file.write("<p>No important articles found.</p>")
        file.write("</body></html>")
    return summary_file

def send_notification(message, summary_file):
    script = f'''
    display notification "{message}" with title "Daily Report"
    tell application "Safari"
        open POSIX file "{summary_file}"
    end tell
    '''
    subprocess.run(["osascript", "-e", script])

# Run scraper.py
os.system('/usr/local/bin/python3 /Users/jackmustonen/Intelligence\\ Report\\ Generator/scraper.py')

# Run display_summaries.py
os.system('/usr/local/bin/python3 /Users/jackmustonen/Intelligence\\ Report\\ Generator/display_summaries.py')

# Generate the summary file and get its path
summary_file = generate_summary()

# Send a notification with a link to the summary file
send_notification("Your report has been generated successfully.", summary_file)
