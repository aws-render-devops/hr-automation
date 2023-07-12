from ._google_services import sheet as sheet_service, drive as drive_service
from googleapiclient.discovery import build




def create():
    spreadsheet_details = {
        'properties': {
            'title': 'Python-google-sheets-demo'
            }
    }
    sheet = sheet_service.spreadsheets().create(body=spreadsheet_details, fields='spreadsheetId').execute()
    sheet_id = sheet.get('spreadsheetId')
    print('Spreadsheet ID: {0}'.format(sheet_id))
    permission1 = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'YOUR EMAIL'
    }
    drive_service.permissions().create(fileId=sheet_id, body=permission1).execute()
    return sheet_id


print(create())
