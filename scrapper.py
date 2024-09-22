import requests
import sys
import json
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime

def main(link, class_name):
    # Get configs
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/tasks']

    # Authenticate and build the services
    flow = InstalledAppFlow.from_client_secrets_file(config['keyPath'], SCOPES)
    creds = flow.run_local_server(port=0)
    calendar_service = build('calendar', 'v3', credentials=creds)
    tasks_service = build('tasks', 'v1', credentials=creds)

    tasklists = tasks_service.tasklists().list().execute()
    id, tasklist = None, None
    
    for tasklist in tasklists.get('items', []):
        id, tasklist = tasklist['id'], tasklist['title']

    if id is None:
        print("No tasklist found.")
        return

    # Making a GET request
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Find the table
    table = soup.find('table')

    # Set class name
    class_name = class_name
    # Check if table is found
    if table is not None:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols_text = [col.get_text() for col in cols]
            
            for text in cols_text:
                if 'due' in text.lower():
                    split = text.split("\n")
                    print(split)
                    if len(split) > 2:
                        assignment_name = split[1]
                        for date in split[2:]:
                            if date != '':
                                current_year = datetime.now().year
                                if date.startswith('Due'):
                                    date = date.split(' ')[1]
                                else:
                                    assignment_name += ' ' + date
                                    date = date.split('Due')[1].strip()
                                date = date.strip() + '/' + str(current_year)
                                try:
                                    date = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%dT00:00:00Z')
                                except ValueError:
                                    print(f"Date parsing error: {date}")
                                    continue

                                # Define the task
                                task = {
                                    'title': f'{class_name} {assignment_name}',
                                    'notes': f'{assignment_name}',
                                    'due': date
                                }

                                print(task)
                                
                                # Insert the task into Google Tasks
                                try:
                                    result = tasks_service.tasks().insert(tasklist=id, body=task).execute()
                                    print(f"Task created: {result['title']} due on {result['due']}")
                                except Exception as e:
                                    print(f"Error creating task: {e}")

    else:
        print("No table found")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scrapper.py <URL> <CLASS_NAME>")
        sys.exit(1)
    
    url = sys.argv[1]
    class_name = sys.argv[2]
    main(url, class_name)