####################################################
# Author:Sathish Kumar Srinivasan
# Contact: sasrinivasan@extremenetworks.com
#
#
####################################################

'''
  
    -Create a DT instance in Azure dynamically. User the generated ser and mac- DTIS gRPC
   - Onboard DT to XIQ- OA3 XAPI
   - Assign policy to device- OA3 XAPI
   - Run a CLI to create VLAN- OA3-XAPI CLI
   - Run a CLI to show VLAN- OA3-XAPI CLI
   - Delete DT from XIQ- OA3 API
   - Destroy DT instance- DTIS gRPC

'''
import time
import sys
sys.path.append("..")
from xiqdtlib.dtlib import *
from xiqdtlib.xiqrest import *
import logging as logger
import random


#Env Variables
endpoint="ipaddress:portnumber"
authtoken='authorization: basic <<<key>>>'


ownerid=0000

apiurl="https://api.extremecloudiq.com/"
xiquser="yourname@example.com"
xiqpass="yourpassword"
authurl="https://api.extremecloudiq.com/login"

devmacaddress="00:48:78:68:90:00"
ser="38391-38601"
snsList=["ESIM"+ser]
clilist_vlancreate=["create vlan test"]
clilist_vlanshow=["show vlan"]


CreateLogReport(logname="DT Automation POC")
logger.info ("Creating DT Instance- ")
createresp=CreateDtInstance(params = {"owner_id": ownerid, "mac_address": devmacaddress, "device_model": "5520-24T", "os_version": "31.5.0.324", "serial_number":ser},servsock=endpoint,stub='extremecloudiq.dtis.v1.DtInstanceService/CreateDtInstance')
#Sleeping for instance to be active

time.sleep(10)
logger.info(createresp)
getdtresp=GetDtInstance(params = {"owner_id": ownerid, "instance_id":createresp["dt_instance_id"]})
logger.info(getdtresp)

listdtresp=ListDtInstances(params = {"owner_id": ownerid, "page":0, "limit": 10})
logger.info(listdtresp)

#Check if DT instance is running and attempt onboard
if (getdtresp["instance"]["gns3_status"]== "GNS3_STATUS_RUNNING") and (getdtresp["instance"]["node_status"]== "started"):
    logger.info("DT instances status>>GNS3_STATUS_RUNNING and node_status>>Started")
    logger.info("Attempting onboarding")
    #Get JWT token
    accessToken,auth_token_header_value=xiqlogin(authurl=authurl,xiquser=xiquser,xiqpass=xiqpass)

    #Onboard device
    onboarded=post_xiqOnboardDevices(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,snsList=snsList,auth_token=auth_token_header_value)
    CheckDeviceStatusPeriodic(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,sn="ESIM"+ser,auth_token="None",starttime=10,incrementtime=5,endtime=300)
    put_xiqpoldevice(apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,snsList=snsList,polname="ST_Policy",auth_token=auth_token_header_value)
    
    #<<<FIX ME- Selenium to update pol or check for API>>>>
    choice=input("Device onboarded. Continue test ?")
    print("Choice is: " + choice)
    
    if onboarded:
        logger.info(f"Onboarded:\t {snsList} successfully")

        #Send CLI with XAPI calls
        cliresp={}
        cliExecTIme={}
        cliresp,cliExecTIme=xiqSwitchingApi(apiurl=apiurl,authurl=authurl,cliList=["show iqagent"],snsList=snsList,auth_token=auth_token_header_value)    
        logger.info("Show iqagent>>>>>")
        logger.info(cliresp)
        logger.info(f"Execution time for CLI is>> {cliExecTIme}")

        #Send CLI with XAPI calls
        cliresp={}
        cliExecTIme={}
        cliresp,cliExecTIme=xiqSwitchingApi(apiurl=apiurl,authurl=authurl,cliList=clilist_vlancreate,snsList=snsList,auth_token=auth_token_header_value)    
        logger.info("Creating VLAN>>>>>")
        logger.info(cliresp)
        logger.info(f"Execution time for CLI is>> {cliExecTIme}")

        cliresp={}
        cliExecTIme={}
        cliresp,cliExecTIme=xiqSwitchingApi(apiurl=apiurl,authurl=authurl,cliList=clilist_vlanshow,snsList=snsList,auth_token=auth_token_header_value)    
        logger.info("show VLAN>>>>>")
        logger.info(cliresp)
        logger.info(f"Execution time for CLI is>> {cliExecTIme}")

        #Delete Onboarded device
        logger.info(f"Deleting DT Instance:{snsList} from XIQ")
        deleted=post_xiqDelOnboardDevices (apiurl=apiurl,authurl=authurl,xiquser=xiquser,xiqpass=xiqpass,path="devices/:delete",snsList=snsList)
        logger.info(f"Device with serial {ser} delete status from xiq"+str(deleted))

    #Delete DTI from azure
    deleteresp=DeleteDtInstance({"owner_id": ownerid, "instance_id":createresp["dt_instance_id"]})
    logger.info(f"Dtinstance with serial {ser} delete Status>>>"+str(deleteresp))
    