import logging

import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient
from . import appconfigs
from . import oracle_report

def get_conn_str():
    return appconfigs.get_storage_connection_string()

def get_oracle_auth():
    return appconfigs.get_oracle_auth()

def get_blob_svc():
    conn_str = get_conn_str()
    blob_svc  = BlobServiceClient.from_connection_string(conn_str)
    return blob_svc

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    container_name = "test"
    blob_svc  = get_blob_svc()
    
    report_path = req.params.get('report_path')
    if not report_path:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            report_path = req_body.get('report_path')
            report_file = report_path.split("/")[-1] 
            blob_file_xl = report_file + ".xlsx"
            oracle_auth = get_oracle_auth()
            # query oracle bi publisher for report
            report_data = oracle_report.get_report_data_no_params(
                report_path, 
                oracle_auth 
            )
            blob_client_xl = blob_svc.get_blob_client(
                container=container_name, 
                blob=blob_file_xl
            )
            # upload the excel file
            blob_client_xl.upload_blob(
                data=report_data,
                overwrite=True
            )
            csv_data = oracle_report.get_excel_csv(
                report_data
            )
            blob_file_csv = report_file + ".csv"
            blob_client_csv = blob_svc.get_blob_client(
                container=container_name, 
                blob=blob_file_csv
            )
            blob_client_csv.upload_blob(
                data=csv_data,
                overwrite=True
            )
            return func.HttpResponse(
                csv_data, 
                status_code=200,
                headers={
                "Content-Type": "text/csv"
                }
            )

    if report_path:
        return func.HttpResponse(f"Hello, {report_path}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
