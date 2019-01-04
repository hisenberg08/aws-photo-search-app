import os
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
        analyzer = "english",
        search_analyzer = "english"   ,
        connection_class=RequestsHttpConnection)
        
def search(label):
    res = es.search(index=index, doc_type=doc_type, body={"query": {"match": {"labels": label}}})
    return res
    
def insert(document):
    res = es.index(index=index, doc_type=doc_type, body=document)
    return res
    
def delete(label):
    res = es.delete_by_query(index=index, doc_type=doc_type, body={"query": {"match": {"labels": label}}})
    print(res)

def lambda_handler(event, context):
    result = ""
    urls = []
    client = boto3.client('lex-runtime', region_name = 'us-east-1')
    print("event",event)
    uiMessage = event["queryStringParameters"]['q']
    print("ui message: ",uiMessage)
    messages = ["Hi"]
    messages.append(uiMessage)
    for message in messages:
        response = client.post_text(
        botName='SearchSubject',
        botAlias='SearchSubject',
        userId ='1234',
        sessionAttributes={},
        requestAttributes={},
        inputText=message
        )
        if(response['message']!="Hi"):
            result = response['message']
    
    #break result into list and remove irrelavent items
    result = result.replace(","," ")
    search_terms = result.split(" ")
    print("search_terms",search_terms)

    #for all items search elastic search, get bucket name and image path and append to url list
    for term in search_terms:
        if term != "and":
            print(term)
            result =  search(term)
            for hit in result['hits']['hits']:
                urls.append("https://"+ hit["_source"]['bucket'] + ".s3.amazonaws.com/"+hit["_source"]['objectKey'])
    print("URLS",urls)
    data =  {
                "response": urls
            }
            
    str1 = ' '.join(urls)
    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
        "body": str1,
    }
    
    print(response)
    
    return response
