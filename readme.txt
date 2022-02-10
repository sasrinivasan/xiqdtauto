1. Clone repo

2. Get environment in azure
Contact Junjie Ma <jma@extremenetworks.com> (Jackie) for environment/auth details
Change these variables in dtlib.py wit the information
endpoint="ipaddress:portnumber"
authtoken='authorization: basic <<<key>>>'

3. Create a public cloud account. Set the following variables in poc.py
ownerid=<<Your VIQ ID>>
xiquser="yourname@example.com"
xiqpass="yourpassword"

4. Change the macaddress and serial in poc.py- any mac/serial will work as long as they are in valid format

devmacaddress="00:48:78:68:90:00"
ser="38391-38601

5. Install grpcurl- preferred method of installing is compiling from source after installing go SDK.Refer

https://github.com/fullstorydev/grpcurl

6. Install requests lib with pip
