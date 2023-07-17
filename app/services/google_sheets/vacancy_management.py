from ._google_services import sheet as sheet_service, drive as drive_service
from googleapiclient.discovery import build


def create():
    spreadsheet_details = {"properties": {"title": "Python-google-sheets-demo"}}
    sheet = (
        sheet_service.spreadsheets()
        .create(body=spreadsheet_details, fields="spreadsheetId")
        .execute()
    )
    sheet_id = sheet.get("spreadsheetId")
    print(
        "===============SHHEETT ID: ===============SHHEETT ID: ===============SHHEETT ID: "
    )
    print(sheet_id)
    print(
        "===============SHHEETT ID: ===============SHHEETT ID: ===============SHHEETT ID: "
    )
    print("Spreadsheet ID: {0}".format(sheet_id))
    permission1 = {
        "type": "user",
        "role": "writer",
        "emailAddress": "hr-automation-service-name@hr-automation-392708.iam.gserviceaccount.com",
    }
    drive_service.permissions().create(fileId=sheet_id, body=permission1).execute()
    return sheet_id


print(create())
