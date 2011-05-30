Docmail API Python Wrapper
==========================

A python wrapper for the Docmail API (V2).

The CFH Docmail service offers customers the ability to generate their own mailings online and have them printed and distributed by Docmail.
Docmail have published a SOAP based API.
This library uses SUDS - a lightweight SOAP python client for consuming Web Services. 

This library was developed by Appogee in partnership with CFH Docmail, and is licensed under the MIT License

Setup
-----
There are Live, Test and Beta versions of the API. Each of which will require a different set of credentials: 
 - Live - links to the live site. This will actually send mail! Use this only in production environments.
 		- Create Account = https://www.cfhdocmail.com/live/signup.aspx
 		- WSDL = https://www.cfhdocmail.com/LiveAPI2/DMWS.asmx?WSDL
 - Test - Replica of Live. This does NOT send mail
 		- Create Account = https://www.cfhdocmail.com/test/signup.aspx
 		- WSDL = https://www.cfhdocmail.com/TestAPI2/DMWS.asmx?WSDL
 - Beta - Includes new and experimental features. This does NOT send mail
 		- Create Account = https://www.cfhdocmail.com/beta/signup.aspx
 		- WSDL = https://www.cfhdocmail.com/BetaAPI2/DMWS.asmx?WSDL
 		
Links
-----
[http://cfhdocmail.com](http://cfhdocmail.com)

[http://www.cfhdocmail.com/downloads/WebServiceHelp2.pdf](http://www.cfhdocmail.com/downloads/WebServiceHelp2.pdf)

[https://fedorahosted.org/suds](https://fedorahosted.org/suds)

[http://www.appogee.co.uk](http://www.appogee.co.uk)

[http://code.google.com/p/python-docmail](http://code.google.com/p/python-docmail)
