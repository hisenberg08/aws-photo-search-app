import json
import boto3
import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
import urllib
import  requests
from requests_aws4auth import AWS4Auth

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host='vpc-photos-fir4ubzacprlorbo4qrbmlpbq4.us-east-1.es.amazonaws.com'
index = 'photos'
doc_type = 'lambda-type'
url = host + '/' + index + '/' + doc_type
headers = { "Content-Type": "application/json" }

# Create the elastic search connection
es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        analyzer =  {
                    "tokenizer": "standard",
                    "filter": ["standard", "lowercase", "stop", "porter_stem"]},        
        search_analyzer = {
                    "tokenizer": "standard",
                    "filter": ["standard", "lowercase", "stop", "porter_stem"]},   
        connection_class=RequestsHttpConnection)
        
def search(label):
    res = es.search(index=index, doc_type=doc_type, body={"query": {"match": {"labels": label}}})
    return res
    
def insert(document):
    print("inside insert")
    res = es.index(index=index, doc_type=doc_type, body=document)
    print("inserted!")
    return res
    
def delete(label):
    res = es.delete_by_query(index=index, doc_type=doc_type, body={"query": {"match": {"labels": label}}})
    print(res)
    
def lambda_handler(event, context):
    finalObj = {}
    alLabels = []
    
    fileName = event['Records'][0]['s3']['object']['key']
    bucket = event['Records'][0]['s3']['bucket']['name']
    
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':fileName}})
    print("recognition response:", response)
    
    for label in response['Labels']:
        alLabels.append(label['Name'])
    finalObj['labels'] = alLabels
    finalObj['objectKey'] = fileName
    finalObj['bucket'] = bucket
    finalObj['createdTimeStamp'] = datetime.datetime.now().isoformat().split(".")[0]
    
    print(finalObj)
    
    # insert the finalObj in elastic search
    result = insert(finalObj)
    print(result)
    print("Inserted")
    # print("RAETREIVING THE INSERTED JSON")
    # result = search('Dog')
    # print(result)
    
    # result = delete('Dog')
    # print(result)
    
    
