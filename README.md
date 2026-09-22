# UPM SMP Student Roster Auto-Scraper

This script automates the extraction of student rosters from the UPM SMP portal. It intercepts background API calls and automatically fetches all paginated data to generate clean CSV files for each course group.

## Prerequisites

### 1. Install Python
If you do not have Python installed on your computer, open your Command Prompt (CMD) and run this command:
```cmd
winget install Python.Python.3.12
```
*Note: Close and reopen the Command Prompt after the installation finishes so the system registers the new `python` command.*

### 2. Install Dependencies
In your newly opened Command Prompt, run these two commands to install the required scraping tools:

1. Install the required Python libraries:
   ```cmd
   pip install playwright beautifulsoup4
   ```
2. Download the Playwright browser binaries:
   ```cmd
   python -m playwright install
   ```

## How to Use

1. Run the script from your terminal:
   ```cmd
   python student_scraper.py
   ```
2. A visible Chromium browser window will open. **Log in to the SMP portal manually.**
3. Navigate to the page containing your course list.
4. Click the hyperlinked number under the **NO. OF STUDENT REGISTERED** column for the class you want to extract.
5. **Stop and wait.** You only need to click the link once. The script will capture the unique class ID and automatically fetch page 1, 2, 3, etc., in the background without needing you to click "Next".
6. Watch the terminal. It will print out its progress and save a file formatted as `student_list_[ID].csv` in the same folder as the script.
7. Repeat for any other classes you need.
8. Close the browser window to terminate the script.