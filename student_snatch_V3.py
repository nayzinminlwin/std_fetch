import asyncio
import csv
import os
import urllib.parse
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Track which IDs have already been processed so we don't trigger multiple downloads for the same class
processed_ids = set()

async def fetch_all_pages(page, course_id):
    current_page = 1
    filename = f"student_list_{course_id}.csv"
    
    # Initialize a fresh CSV file with headers
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["NO", "MATRIC NO.", "STUDENT NAME"])
        
    print(f"\n--- Starting Auto-Fetch for ID: {course_id} ---")
    
    while True:
        # Construct the exact API request for the current page
        url = "https://esmp.upm.edu.my/smp/action/portal/student/myregistra/popupSearchRegisteredStudentSetup"
        post_data = f"zsemcId={course_id}&currentPage={current_page}&filterColumn=0&filterValue="
        
        # Send a background POST request using the browser's logged-in session
        response = await page.request.post(
            url,
            data=post_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        html_content = await response.text()
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        
        # If no table exists on the page, we've gone past the last page
        if not table:
            break

        tbody = table.find('tbody')
        rows = tbody.find_all('tr') if tbody else table.find_all('tr')[1:]
        
        student_count = 0
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    no = cols[0].text.strip()
                    matric = cols[1].text.strip()
                    name = cols[2].text.strip()
                    
                    # Verify it is a valid row containing student data
                    if no.isdigit():
                        writer.writerow([no, matric, name])
                        student_count += 1
                        
        # If the page loads but has zero students, we are done
        if student_count == 0:
            break
            
        print(f"  -> Page {current_page}: Extracted {student_count} students.")
        current_page += 1
        
    print(f"--- Finished! All pages saved to {filename} ---\n")

async def handle_response(response, page):
    TARGET_API_URL = "/action/portal/student/myregistra/popupSearchRegisteredStudentSetup"
    
    if TARGET_API_URL in response.url and response.ok and response.request.method == "POST":
        try:
            payload = urllib.parse.parse_qs(response.request.post_data)
            if 'zsemcId' in payload:
                course_id = payload['zsemcId'][0]
                
                # If this is a new course ID, launch the auto-fetcher
                if course_id not in processed_ids:
                    processed_ids.add(course_id)
                    # Run the active fetching in the background without freezing the browser
                    asyncio.create_task(fetch_all_pages(page, course_id))
                    
        except Exception as e:
            print(f"An error occurred: {e}")

async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Pass the 'page' object into the listener so it can make active requests later
        page.on("response", lambda response: asyncio.create_task(handle_response(response, page)))
        
        await page.goto("https://esmp.upm.edu.my/smp/")
        print("Auto-Pagination Scraper Ready.")
        print("Log in, and click the student count ONCE for each class.")
        print("The script will automatically hunt down the rest of the pages.")
        
        try:
            await page.wait_for_event("close", timeout=0)
        except Exception:
            pass

asyncio.run(run_scraper())