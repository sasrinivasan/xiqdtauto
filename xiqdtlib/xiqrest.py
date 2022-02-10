###################################################
# Author:Sathish Kumar Srinivasan
# Contact: sasrinivasan@extremenetworks.com
#
#
####################################################
import time
import logging
import requests
import inspect
import datetime
import  logging as logger
import os


okRespCodeList=[200,202]
snsList=[]

apiurl="apiurl"
xiquser="xiquser"
xiqpass="xiqpass"
authurl="authurl"


polname=""

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

def CheckRestError(status_code=500,response=""):
    respOK=True
    callerfunction=str(inspect.stack()[1].function)


    if status_code not in okRespCodeList:
        logging.error("Unexpected response from REST server- Response  is %s",response)
        
        logging.error("Calling Function is %s",callerfunction)
        respOK=False
    return respOK

def CreateLogReport(logname='Logs_'):
    filename= logname +"_"+ datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+'.log'
    if not os.path.exists("Testlog"):
        os.makedirs("Testlog")
        
    
    logging.basicConfig(
    filename='./Testlog/'+filename,
    level=logging.INFO, 
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
     )


# Login to XIQ with user/pass and get  a bearer/auth token. This is needed for further REST requests
def xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass):
    accessToken=None
    auth_token_header_value = None

    data = { "username": xiquser, "password": xiqpass }
    auth_response = requests.post(authurl, json=data,headers=headers)
    statusCode=auth_response.status_code
    responseOK=CheckRestError(status_code=statusCode,response=auth_response.text)
  
    if responseOK!=False:
        #print(auth_response.text)
        logger.debug("Authentication  successfull. Access token is:")
        logger.debug(auth_response.text)

        #authToken=json.dumps(auth_response.text)["access_token"]
        auth_token=auth_response.json()
        accessToken=auth_token["access_token"]
        auth_token_header_value = "Bearer %s" % accessToken
    
    
    return  accessToken,auth_token_header_value

def post_xiqOnboardDevices (apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,path="devices/:onboard",deviceType="exos",field="sns",snsList=[],auth_token="None"):
    url=apiurl+path
    onboardeddeviceList=None
    
    OnBoarded=False
    
    onboardDeviceDict={deviceType:{ "sns": []}}
    
    if auth_token=="None":
        logger.info("post_xiqOnboardDevices-Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)
    else:
        auth_token_header_value=auth_token
        
     
    for serialno in snsList:
        onboardDeviceDict[deviceType][field].append(serialno)
    
    data=onboardDeviceDict
    #print (data)
    headers={'accept': 'application/json',"Authorization": auth_token_header_value,}
    response = requests.post(url, json=data,headers=headers)

    statusCode=response.status_code
    responseOK=CheckRestError(status_code=statusCode,response=response.text)
    
    if responseOK!=False:
        #print(auth_response.text)
        logger.info("Devices added to XIQ")

        OnBoarded=True



    return  OnBoarded



#Returns a dictionary list of  onboarded  devices
def get_xiqdeviceListDict(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,path="devices?page=1&limit=100",auth_token="None"):
    url=apiurl+path
    DeviceInfo={}
    if auth_token=="None":
        logger.info("get_xiqdeviceListDict-Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)
    auth_token_header_value=auth_token
    headers={'accept': 'application/json',"Authorization": auth_token_header_value,}
    response=requests.get(url, headers=headers)
    statusCode=response.status_code
    responseOK=CheckRestError(status_code=statusCode,response=response.text)
    
    if responseOK!=False:
        #print(auth_response.text)
        logger.debug("get_xiqdeviceList-XIQ added list of devices:")
        logger.debug(response.json())
        DeviceInfo=response.json()
    
    return DeviceInfo

#Returns a dictionary list of  clients connected to  onboarded devices
def get_xiqclientListDict(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,path="clients/active?page=1&limit=10000", auth_token="None"):
    url=apiurl+path
    ClientInfo={}
    if auth_token=="None":
        logger.info("get_xiqclientListDict-Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)
    
    headers={'accept': 'application/json',"Authorization": auth_token_header_value,}
    response=requests.get(url, headers=headers)
    statusCode=response.status_code
    responseOK=CheckRestError(status_code=statusCode,response=response.text)
    
    if responseOK!=False:
        #print(auth_response.text)
        logger.debug("get_xiqclientListDict-List of connected clients")
        logger.debug(response.json())
        ClientInfo=response.json()
    #print(UserInfo)
    return ClientInfo

# Given a device serial  number, fetch onboarded device ID
def get_xiqDeviceId(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,sn="2008G-01292",auth_token="None"):
    DeviceId=None
    
    if auth_token=="None":
        logger.info("get_xiqDeviceId-Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)
        auth_token=auth_token_header_value
   
    
   
    
    deviceInfoDict=get_xiqdeviceListDict(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,auth_token=auth_token)

    logger.info("get_xiqDeviceId:List of devices\t" +str(deviceInfoDict))
    deviceList=deviceInfoDict['data']
    for device in deviceList:
        if device['serial_number']== sn:
            DeviceId=device['id']
    return DeviceId

# Poll device status periodically till it reaches a state Managed in given time
#Start time- Inital sleep, increment time- periodic poll time, endtime- final time before returning failure

def CheckDeviceStatusPeriodic(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,sn="",auth_token="None",starttime=10,incrementtime=5,endtime=300):
    deviceStatus="NOT_PRESENT"
    connecttime=starttime
    poll=True
    if auth_token=="None":
        logger.info("get_xiqDeviceId-Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)
        auth_token=auth_token_header_value
    
    
    logger.info(f"Sleeping for {starttime} before checking device status")
    time.sleep(starttime)

    while poll==True:
        
        deviceInfoDict=get_xiqdeviceListDict(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,auth_token=auth_token)

        #logger.info("get_xiqDeviceId:List of devices\t" +str(deviceInfoDict))
        deviceList=deviceInfoDict['data']

        for device in deviceList:
 
            if (device['serial_number']== sn) and (device["device_admin_state"]=="MANAGED"):
                
                
                logger.info(f"Device status is Managed- Time taken {connecttime} seconds")
                poll=False
                deviceStatus="Managed"
                logger.info(device)

                break
                
            else:
                if (connecttime == endtime):
                    logger.error(f"Device state did not change to managed in {endtime} seconds.")
                    logger.info(device)
                    poll=False
                    break
                else:
                    devicestate=device["device_admin_state"]
                    logger.info(f"Current state of device with serial number {sn} is {devicestate} ")
                    logger.info(f"Time elapsed {connecttime} sec.Sleeping for {incrementtime} seconds before next poll")
                    connecttime=connecttime+incrementtime
                    time.sleep(incrementtime)



                

                
    return deviceStatus

# Delete Devices from XIQ
def post_xiqDelOnboardDevices (apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,path="devices/:delete",snsList=[]):
    url=apiurl+path
    data = {"ids":[]}
    Deleted=False
    accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)

    
    

    for serialno in snsList:
        devid=""
        devid=get_xiqDeviceId(apiurl=apiurl,authurl=authurl,sn=serialno,auth_token=auth_token_header_value)
        if devid !="None":
            data["ids"].append(devid)
    
    #print(data)

    logger.info("From post_xiqDelOnboardDevices- Devices ID list:\t",data)

  
    headers={'accept': 'application/json',"Authorization": auth_token_header_value,}
    response = requests.post(url, json=data,headers=headers)
    #print(response)
    statusCode=response.status_code
    responseOK=CheckRestError(status_code=statusCode,response=response.text)

    if responseOK!=False: 
        #print(auth_response.text)
        logger.debug("Devices deleted from XIQ")

        Deleted=True



    return  Deleted



def xiqSwitchingApi(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,path="devices/:cli",deviceType="exos",cliList=[],snsList=[],auth_token="None"):


    cliResp={}
    url=apiurl+path
    cliRespJson={}
   
    #accessToken=None
    #auth_token_header_value = None
    #OnBoarded=False
    
    cliDict = {"devices":{"ids":[]},"clis":[]}
    
    cliExecTImeDict={"devices":{"ids":[]},"clis":[],"execTime":[]}

    if auth_token=="None":
        logger.info("Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)

    
    
    auth_token_header_value=auth_token
    for serialno in snsList:
        id=get_xiqDeviceId(apiurl=apiurl,authurl=authurl,sn=serialno,auth_token=auth_token_header_value)
        cliDict["devices"]["ids"].append(id)
        cliExecTImeDict["devices"]["ids"].append(id)
        
    for cli in cliList:
        cliDict["clis"].append(cli)
        cliExecTImeDict["clis"].append(cli)
        #Dict for CLIresp time
        
    
    #print(cliDict)
    headers={'accept': 'application/json',"Authorization": auth_token_header_value,}
    #Start clock tick
    cli_begin_time = datetime.datetime.now()
    logger.debug(f"CLI dictionary is {cliDict}")
    response = requests.post(url, json=cliDict,headers=headers)
    #End it after getting resp from XIQ
    cli_endtime=datetime.datetime.now()-cli_begin_time
    cliExecTImeDict["execTime"].append(cli_endtime)

  


    statusCode=response.status_code
    responseOK=CheckRestError(status_code=statusCode,response=response.text)

    
    if responseOK!=False:
        
        logger.debug(f"CLI executed for devices")
        cliRespJson=response.json()
        
    return cliRespJson,cliExecTImeDict

#Returns a dictionary list of  policies
def get_xiqpolicyListDict(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,path="network-policies?page=1&limit=10",auth_token="None"):
    url=apiurl+path
    #print(url)
    PolicyInfo={}

    if auth_token=="None":
        logger.info("Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)
    auth_token_header_value=auth_token

    headers={'accept': 'application/json',"Authorization": auth_token_header_value,}
    response=requests.get(url, headers=headers)
    statusCode=response.status_code
    responseOK=CheckRestError(status_code=statusCode,response=response.text)
    
    if responseOK!=False:
        #print(auth_response.text)
        logger.debug("get_xiqpolicyListDic-List of policies")
        logger.debug(response.json())
        PolicyInfo=response.json()
    #print(UserInfo)
    return PolicyInfo

def get_xiqpolicyId(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,polname="Wired",auth_token="None"):
    PolicyId=None
    
    if auth_token=="None":
        logger.info("Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)
    auth_token_header_value=auth_token

    policyInfoDict=get_xiqpolicyListDict(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,auth_token=auth_token)
    
    logger.debug("get_xiqDeviceId:List of policy\t" +str(policyInfoDict))
    policyList=policyInfoDict['data']
    for pol in policyList:
        if pol['name']== polname:
            PolicyId=pol['id']

    return PolicyId
#assign a policy to device
def put_xiqpoldevice(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,snsList=[],polname="ST_Policy",auth_token="None"):
    
    if auth_token=="None":
        logger.info("Auth token not passed- Generating new token")
        accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)
    auth_token_header_value=auth_token


    headers={'accept': 'application/json',"Authorization": auth_token_header_value,}
    
    polstatusdict={}
    
    for serialno in snsList:
        deviceid=get_xiqDeviceId(apiurl=apiurl,authurl=authurl,sn=serialno,auth_token=auth_token_header_value)
        policyid=get_xiqpolicyId(apiurl=apiurl,polname=polname,authurl=authurl,auth_token=auth_token_header_value)
        
        url=apiurl+"devices/"+str(deviceid)+"/network-policy?networkPolicyId="+str(policyid)
       
        response=requests.put(url,headers=headers)
        polstatusdict["serial_no"]=serialno
        polstatusdict["device_id"]=deviceid
        polstatusdict["policy_id"]=policyid
        polstatusdict["put_url"]=url
        polstatusdict["policy assignment status"]=response
    
    
    
    statusCode=response.status_code
    responseOK=CheckRestError(status_code=statusCode,response=response.text)
   
    if responseOK!=False:
        
        logger.debug(f"{polname} assigned to devices in {snsList}" )
        logger.info(polstatusdict)
        
   
    return polstatusdict


        
        

    

if __name__=="__main__":

  
    print("<<<<<In XIQ REST main>>>>>>>>>")
 