####################################################
# Author:Sathish Kumar Srinivasan
# Contact: sasrinivasan@extremenetworks.com
#
#
####################################################

import json 
import subprocess
import  logging as logger




endpoint="ipaddress:portnumber"
authtoken='authorization: basic <<<key>>>'


#Accepts string respone of gRPC call, trims other strings and returns json
def getresponsedict(call_result="",callresultstartkey="{",callresultendkey="Response trailers received"):
        resp={}
        #Find begining and end of json resp
        startjson=call_result.find(callresultstartkey)
        endjson=call_result.find(callresultendkey)
        
          
        resp=call_result[startjson:endjson]

              
        return json.loads(resp)

#Get details of DT instance
def CreateDtInstance(params = {"owner_id": 0000, "mac_address": "00:A3:59:e8:40:00", "device_model": "5520-24T", "os_version": "31.5.0.324", "serial_number":"44956-12345"},servsock=endpoint,stub='extremecloudiq.dtis.v1.DtInstanceService/CreateDtInstance'):
    
    resp={}
    try:
        call_result = subprocess.check_output(['grpcurl', '-format-error', '-vv','--plaintext','-H', authtoken, '-d', json.dumps(params), servsock, stub])
        #Response is bytestrem- decode to str
        resp=getresponsedict(call_result.decode())
        
    except subprocess.CalledProcessError as e:
        logger.error(e.returncode)
        logger.error(e.output)
        resp["Error code"]=str(e.returncode)
        resp["Error"] = str(e.output)
        logger.error(resp)
    
    return resp

#Get details of DT instance
def GetDtInstance(params = {"owner_id": 0000, "instance_id":559},servsock=endpoint,stub='extremecloudiq.dtis.v1.DtInstanceService/GetDtInstance'):
    
    resp={}
    try:
        call_result = subprocess.check_output(['grpcurl', '-format-error', '-vv','--plaintext','-H', authtoken, '-d', json.dumps(params), servsock, stub])
        #Response is bytestrem- decode to str
        resp=getresponsedict(call_result.decode())
        
    except subprocess.CalledProcessError as e:
        logger.error(e.returncode)
        logger.error(e.output)
        resp["Error code"]=str(e.returncode)
        resp["Error"] = str(e.output)
        logger.error(resp)
    
    return resp

#List DT instances for owner
def ListDtInstances(params = {"owner_id": 0000, "page":0, "limit": 10},servsock=endpoint,stub='extremecloudiq.dtis.v1.DtInstanceService/ListDtInstances'):
    
    resp={}
    try:
        call_result = subprocess.check_output(['grpcurl', '-format-error', '-vv','--plaintext','-H', authtoken, '-d', json.dumps(params), servsock, stub])
        #Response is bytestrem- decode to str
        resp=getresponsedict(call_result.decode())
        
    except subprocess.CalledProcessError as e:
        logger.error(e.returncode)
        logger.error(e.output)
        resp["Error code"]=str(e.returncode)
        resp["Error"] = str(e.output)
        logger.error(resp)
    
    return resp
#Delete Dt instance
def DeleteDtInstance(params = {"owner_id": 0000, "instance_id":559},servsock=endpoint,stub='extremecloudiq.dtis.v1.DtInstanceService/DeleteDtInstance'):
    
    resp={}
    try:
        call_result = subprocess.check_output(['grpcurl', '-format-error', '-vv','--plaintext','-H', authtoken, '-d', json.dumps(params), servsock, stub])
        #print(call_result)
        #Response is bytestrem- decode to str
        resp=getresponsedict(call_result.decode())
        #Empty dict returns true
        if not resp:
            #Query the deleted instance status again
            gns_status=GetDtInstance(params=params)
            resp["owner_id"]=params["owner_id"]
            resp["instance_id"]=params["instance_id"]
            #gns3_status': 'GNS3_STATUS_DELETED
            resp["gns3_status"]=gns_status["instance"]["gns3_status"]
            
            
        
    except subprocess.CalledProcessError as e:
        logger.error(e.returncode)
        logger.error(e.output)
        resp["Error code"]=str(e.returncode)
        resp["Error"] = str(e.output)
        logger.error(resp)
    
    return resp
#Cleanup all running DT instances given a owner ID
def CleanupDtInstances(params = {}):
    
    dtinstancelist=ListDtInstances(params=params)
    #print(dtinstancelist)
    instances=dtinstancelist["dt_instances"]
    cleanedupList=[]
    for instance in instances:
        
        if instance["gns3_status"]=="GNS3_STATUS_RUNNING":
           
            deleteresp=DeleteDtInstance({"owner_id": params["owner_id"], "instance_id":instance["instance_id"]})
            cleanedupList.append(deleteresp)
    return cleanedupList
   



        



if __name__=="__main__":
    #listdtresp=ListDtInstances()
    #print(listdtresp)
    cleanlist=[]
    cleanlist=CleanupDtInstances(params={"owner_id": 0000, "page":0, "limit": 10})
    print(cleanlist)
    cleanlistg2=CleanupDtInstances(params={"owner_id": 0000, "page":0, "limit": 10})
    print(cleanlistg2)
    
    #createresp=CreateDtInstance()
    #print("Createresp->>>"+str(createresp))

    '''getdtresp=GetDtInstance(params = {"owner_id": 0000, "instance_id":createresp["dt_instance_id"]})
    print("Getresponse->>>"+str(getdtresp))
    deleteresp=DeleteDtInstance({"owner_id": 0000, "instance_id":createresp["dt_instance_id"]})
    print("Deleteresponse->>>"+str(deleteresp))'''

    

