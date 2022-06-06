import requests
import base64
from xml.etree import ElementTree
import pandas as pd



def get_report_data_no_params(report_path, auth_config):

    ### build up the API call basic url params
    api_path = "/xmlpserver/services/ExternalReportWSSService?WSDL"
    url_path = auth_config["api_url"] + api_path
    
    ### SOAP body for calling the report - we pass in the report path
    xml_body = f"""
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:pub="http://xmlns.oracle.com/oxp/service/PublicReportService">
    <soap:Header/>
    <soap:Body>
        <pub:runReport>
            <pub:reportRequest>
                <pub:flattenXML>false</pub:flattenXML>
                <pub:reportAbsolutePath>{report_path}</pub:reportAbsolutePath>
                <pub:sizeOfDataChunkDownload>-1</pub:sizeOfDataChunkDownload>
            </pub:reportRequest>
        </pub:runReport>
    </soap:Body>
    </soap:Envelope>
    """
    
    ###  Make the SOAP request
    resp = requests.post(
        url_path, 
        auth=(auth_config["user"], auth_config["pass"]), 
        headers={
            'Content-Type': "application/soap+xml",
            'SOAPAction': "#POST"
        }, 
        data=xml_body
        )
    
    ### the response is returned as a SOAP xml response -- truncated sample below
    """
    <env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope">
    <env:Header/>
    <env:Body>
        <ns2:runReportResponse xmlns:ns2="http://xmlns.oracle.com/oxp/service/PublicReportService">
            <ns2:runReportReturn>
                <ns2:reportBytes>.....</ns2:reportBytes>
                <ns2:reportContentType>application/vnd.openxmlformats-officedocument.spreadsheetml.sheet</ns2:reportContentType>
                <ns2:reportFileID xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
                <ns2:reportLocale xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
                <ns2:metaDataList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
            </ns2:runReportReturn>
        </ns2:runReportResponse>
    </env:Body>
    </env:Envelope>
    """
    ### parse the response to read "reportBytes"
    tree = ElementTree.fromstring(resp.content)
    base64_excel = tree.findall(".//{http://xmlns.oracle.com/oxp/service/PublicReportService}reportBytes")[0].text
    
    ### report bytes are returned as base64 encoded xlsx, so we decode it and write the excel 
    excel_data = base64.b64decode(base64_excel)

    return excel_data


def get_excel_csv(excel_bytes):
    data = pd.read_excel(excel_bytes)
    df = pd.DataFrame(
        data, 
        columns=[
            'NAME',
            'PERSON NUMBER',
            'GENDER',
            'DEPARTMENT NAME',
            'JOB',
            'ASSIGNMENT_NUMBER'
            ]
        )
    output =df.to_csv(index=False, encoding="utf-8")
    return output

