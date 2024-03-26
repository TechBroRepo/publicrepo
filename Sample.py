import requests
from jira import JIRA

def get_jira_data(jql_query, server_url, api_token):
    # Configure JIRA connection
    options = {
        'server': server_url,
        'verify': False,  # Set to True if your JIRA server has SSL enabled
        'headers': {
            'Authorization': 'Bearer ' + api_token
        }
    }

    # Connect to JIRA
    jira = JIRA(options=options)

    # Execute JQL query
    issues = jira.search_issues(jql_query)

    # Initialize variables to store data
    total_cases = len(issues)
    automated_cases = 0
    to_be_automated_cases = 0
    manual_cases = 0

    # Count cases based on automation status
    for issue in issues:
        automatable = issue.fields.get('Automatable', False)
        automated = issue.fields.get('Automated', False)
        if automatable and automated:
            automated_cases += 1
        elif automatable and not automated:
            to_be_automated_cases += 1
        else:
            manual_cases += 1

    # Calculate automation coverage
    if total_cases > 0:
        automation_coverage = (automated_cases / (automated_cases + to_be_automated_cases)) * 100
    else:
        automation_coverage = 0

    return total_cases, automated_cases, to_be_automated_cases, manual_cases, automation_coverage

def generate_html_table(data):
    html = "<table border='1'>\n"
    html += "<tr><th>LABEL</th><th>TOTAL_CASES</th><th>AUTOMATED_CASES</th><th>TO_BE_AUTOMATED_CASES</th><th>MANUAL_CASES</th><th>AUTOMATION_COVERAGE</th><th>REGRESSION_COVERAGE</th></tr>\n"
    html += f"<tr><td>{data[0]}</td><td>{data[1]}</td><td>{data[2]}</td><td>{data[3]}</td><td>{data[4]}</td><td>{data[5]:.2f}%</td><td>TODO</td></tr>\n"
    html += "</table>"
    return html

# Example JQL query (replace with your actual query)
jql_query = 'labels = RBT_GDO'

# Example server URL and API token (replace with your actual credentials)
server_url = 'YOUR_JIRA_SERVER_URL'
api_token = 'YOUR_API_TOKEN'

# Collect data from JIRA
total_cases, automated_cases, to_be_automated_cases, manual_cases, automation_coverage = get_jira_data(jql_query, server_url, api_token)

# Generate HTML content
html_content = generate_html_table(('RBT_GDO', total_cases, automated_cases, to_be_automated_cases, manual_cases, automation_coverage))

# POST HTML content to Confluence page
confluence_page_id = 'YOUR_CONFLUENCE_PAGE_ID'
confluence_url = 'YOUR_CONFLUENCE_API_URL'
headers = {
    'Authorization': 'Bearer YOUR_CONFLUENCE_API_TOKEN',
    'Content-Type': 'application/json'
}
data = {
    'type': 'page',
    'title': 'JIRA Data Report',
    'space': {
        'key': 'YOUR_CONFLUENCE_SPACE_KEY'
    },
    'body': {
        'storage': {
            'value': html_content,
            'representation': 'storage'
        }
    }
}
response = requests.put(f'{confluence_url}/rest/api/content/{confluence_page_id}', headers=headers, json=data)

# Check response
if response.status_code == 200:
    print("HTML webpage posted successfully to Confluence.")
else:
    print("Error occurred while posting HTML webpage to Confluence:", response.text)
