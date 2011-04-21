#!/usr/bin/env python
#
# Docmail API Wrapper (Python)
#
#Copyright (c) 2011 Appogee (www.appogee.co.uk)
# 
#Permission is hereby granted, free of charge, to any person obtaining
#a copy of this software and associated documentation files (the
#"Software"), to deal in the Software without restriction, including
#without limitation the rights to use, copy, modify, merge, publish,
#distribute, sublicense, and/or sell copies of the Software, and to
#permit persons to whom the Software is furnished to do so, subject to
#the following conditions:
# 
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
# 
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
#LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
#OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Docmail API Wrapper (Python) is a Python wrapper for the docmail API V2.
For futher information and full documentation of Docmail API see http://www.cfhdocmail.com/downloads/WebServiceHelp2.pdf

Docmail is a web based service for sending snail-mail electronically.
For further information on Docmail see http://cfhdocmail.com/

This wrapper extends the suds library for making soap calls.
For further information on suds see https://fedorahosted.org/suds/

Project home: http://code.google.com/p/python-docmail/
"""

__author__ = 'gwyn.howell@appogee.co.uk (Gwyn Howell)'
__version__ = '1.0'
__license__ = 'Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)'

from xml.dom.minidom import parseString
import base64
import datetime
import os.path
import re
import suds.client

from docmail import enums, util

DOCMAIL_WSDL = 'https://www.cfhdocmail.com/BetaAPI2/DMWS.asmx?WSDL'

RE_DATETIME = '^(0[1-9]|[12][0-9]|3[01])[/](0[1-9]|1[012])[/](19|20)\d\d[ ]([0-1][0-9]|2[0-3])[:][0-5][0-9][:][0-5][0-9]$'
PTN_DATETIME = '%d/%m/%Y %H:%M:%S'

# some default values for processing a mailing
PROCESS_MAILING = { 'po_reference': '', 
                    'payment_method': 'Topup', 
                    'email_success_list': '',
                    'email_error_list': '',
                    'http_post_on_success': '', 
                    'http_post_on_error': '',
                    'max_price_ex_vat': 0,
                    'skip_preview_image_generation': False }

class DocmailException(Exception):
    def __init__(self, code, error, description):
        self.code = code
        self.error = error
        self.description = description
            
    def __str__(self):
        return '%s (%s): %s' % (self.error, self.code, self.description)

class DocmailObject(object):
    def _format_data(self):
        """ override this method to provide custom formatting for data returned from docmail """
        pass

class Mailing(DocmailObject):
    def __init__(self, name=None):
        # mailing_product and product_type seem to be the same thing?
        self.product_type = enums.ProductType.A4Letter
        self.name = name
        self.mailing_description = None
        self.is_colour = True
        self.is_duplex = False
        self.delivery_type = enums.DeliveryType.Standard
        self.courier_delivery_to_self = False
        self.despatch_asap = True
        self.despatch_date = datetime.datetime.now() + datetime.timedelta(days=2)
        self.address_name_prefix = None
        self.address_name_format = enums.AddressNameFormat.FullName
        self.discount_code = None
        self.min_envelope_size = enums.MinEnvelopeSize.C5

    @property
    def is_mono(self):
        raise Exception('property not supported - use is_colour instead')

    def _format_data(self):
        if self.mailing_list_guid == '00000000-0000-0000-0000-000000000000':
            self.mailing_list_guid = None
        
        if self.despatch_date == 'ASAP':
            self.despatch_asap = True
            self.despatch_date = None
        else:
            self.despatch_asap = False

class TemplateFile(object):
    def __init__(self, file, data=None):
        """ creates a template file object. can be created from:
            - file object - specify file=file object
            - file path - specify file=path to file
            - bytes - specify file=filename and data=bytes
        """
        
        if data:
            self.file_name = file
            self.file_data = data
        else:
            if isinstance(file, basestring):
                if os.path.isfile(file):
                    file = open(file, 'r')
            
            self.file_name = file.name
            self.file_data = file.read()
        
        ext = self.file_name[self.file_name.rfind('.')+1:].lower()
        if not ext in ('doc', 'docx', 'rtf'):
            raise ValueError('file_name incorrect format, must be .doc, .docx or .rtf')
        
        self.guid = None
        self.template_name = ''
        self.document_type = enums.DocumentType.A4Letter
        self.address_font_code = enums.AddressFont.Arial10
        self.template_type = 'Preformatted Stream' if ext == 'pdf' else 'Document'
        self.background_name = ''
        self.protected_area_password = ''
        self.encryption_password = ''
        self.instance_page_numbers = ''
        self.addressed_document = True
        self.can_begin_on_back = False
        self.next_template_can_begin_on_back = False
        self.bleed_supplied = True
        self.copies = 1
        self.instances = 1
        self.cycle_instances_on_copies = False

class MailingListFile(object):
    def __init__(self, file, data=None, sheet_name=None, data_format=None, mapping_delimiter=None, mapping_fixed_width_chars=None):
        """ creates a mailing list file object. can be created from:
            - file object - specify file=file object
            - file path - specify file=path to file
            - bytes - specify file=filename and data=bytes
        """

        if data:
            self.file_name = file
            self.file_data = data
        else:
            if isinstance(file, basestring):
                if os.path.isfile(file):
                    file = open(file, 'r')
            
            self.file_name = file.name
            self.file_data = file.read()

        ext = self.file_name[self.file_name.rfind('.')+1:].lower()
        if ext == 'csv':
            data_format = 'CSV'
        elif ext in ('xls', 'xlsx'):
            data_format = 'Excel'
            if not sheet_name:
                raise ValueError('sheet_name argument must be provided for .%s files' % ext)
        elif ext == 'txt':
            if not data_format in ('Tab separated', 'Delimited', 'Fixed width'):
                raise ValueError('data_format not supplied or not valid - must be "Tab separated", "Delimited", or "Fixed width" for txt files')
        else:
            raise ValueError('Unsupported file - %s. Please provide a .txt, .csv, .xls or .xlsx file' % ext)
        
        # some more validation ...
        if data_format == 'Delimited' and mapping_delimiter:
            raise ValueError('mapping_delimiter arg must be provided if data_format is Delimited')
        if data_format == 'Fixed width' and mapping_fixed_width_chars:
            raise ValueError('mapping_fixed_width_chars arg must be provided if data_format is Fixed Width')
        
        # some default values ...
        self.headers = True
        self.mapping_name = ''
        self.data_format = data_format or ''
        self.mapping_delimiter = mapping_delimiter or '    '
        self.sheet_name = sheet_name or ''
        self.mapping_fixed_width_chars = mapping_fixed_width_chars or ''

class Client(suds.client.Client):
    def __init__(self, username, password, source='', wsdl_url=None, **kwargs):
        if not wsdl_url:
            wsdl_url = DOCMAIL_WSDL
        self.source = source
        self.username = username
        self.password = password
        
        self.return_format = 'XML'           
        self.failure_return_format = 'XML'
        suds.client.Client.__init__(self, wsdl_url, **kwargs)
        
    def _parse(self, xml, return_class=DocmailObject):
        ob = return_class()
        dom = parseString(xml)
        for node in dom.firstChild.childNodes:
            key = node.childNodes[0].firstChild.wholeText
            value = node.childNodes[1].firstChild.wholeText
            
            key = self._format_key(key)
            value = self._format_value(value)
            
            if key == 'error_code':
                raise DocmailException(value,
                   self._format_value(node.childNodes[3].firstChild.wholeText),
                   self._format_value(node.childNodes[5].firstChild.wholeText))
            
            setattr(ob, key, value)
        if hasattr(ob, '_format_data'):
            ob._format_data()
        return ob
        
    def _format_key(self, key):
        if not ' ' in key:
            key = '_'.join(util.split_caps(key))
        key = key.strip('\/:*?"<>|').replace(' ', '_').lower()
        return key
    
    def _format_value(self, value):
        if re.match(RE_DATETIME, value):
            return datetime.datetime.strptime(value, PTN_DATETIME)
        if value.lower() == 'yes':
            return True
        if value.lower() == 'no':
            return False
        return value
    
    def get_mailing(self, guid):
        xml = self.service.GetMailingDetails(self.username, self.password, guid, self.return_format)
        mailing = self._parse(xml, Mailing)
        mailing.guid = guid
        return mailing
    
    def create_mailing(self, mailing):
        xml = self.service.CreateMailing(self.username, self.password, self.source,
                                         mailing.product_type, 
                                         mailing.name, 
                                         mailing.mailing_description,
                                         not mailing.is_colour, 
                                         mailing.is_duplex, 
                                         mailing.delivery_type, 
                                         mailing.courier_delivery_to_self, 
                                         mailing.despatch_asap, 
                                         mailing.despatch_date, 
                                         mailing.address_name_prefix, 
                                         mailing.address_name_format, 
                                         mailing.discount_code, 
                                         mailing.min_envelope_size, 
                                         self.return_format)
        ob = self._parse(xml)
        mailing.guid = ob.mailing_guid
        return mailing
    
    def update_mailing(self, mailing):
        xml = self.service.UpdateMailingOptions(self.username, self.password, 
                                                mailing.guid, 
                                                mailing.name, 
                                                mailing.mailing_description, 
                                                not mailing.is_colour, 
                                                mailing.is_duplex, 
                                                mailing.delivery_type, 
                                                mailing.despatch_asap, 
                                                mailing.despatch_date, 
                                                mailing.address_name_prefix, 
                                                mailing.address_name_format, 
                                                mailing.discount_code, 
                                                mailing.min_envelope_size, 
                                                self.return_format)
        ob = self._parse(xml)
        return ob.success
    
    def add_template_file(self, mailing_guid, template_file):
        xml = self.service.AddTemplateFile(self.username, self.password, mailing_guid, 
                                           template_file.template_name, 
                                           template_file.file_name, 
                                           base64.b64encode(template_file.file_data), 
                                           template_file.document_type, 
                                           template_file.addressed_document, 
                                           template_file.address_font_code, 
                                           template_file.template_type, 
                                           template_file.background_name, 
                                           template_file.can_begin_on_back, 
                                           template_file.next_template_can_begin_on_back, 
                                           template_file.protected_area_password, 
                                           template_file.encryption_password, 
                                           template_file.bleed_supplied, 
                                           template_file.copies, 
                                           template_file.instances, 
                                           template_file.instance_page_numbers, 
                                           template_file.cycle_instances_on_copies, 
                                           self.return_format)
        ob = self._parse(xml)
        template_file.guid = ob.template_guid
        return template_file
    
    def add_mailing_list_file(self, mailing_guid, mailing_list_file):
        xml = self.service.AddMailingListFile(self.username, self.password, mailing_guid, 
                                              mailing_list_file.file_name,
                                              base64.b64encode(mailing_list_file.file_data), 
                                              mailing_list_file.data_format,
                                              mailing_list_file.headers, 
                                              mailing_list_file.sheet_name, 
                                              mailing_list_file.mapping_delimiter, 
                                              mailing_list_file.mapping_fixed_width_chars, 
                                              mailing_list_file.mapping_name, 
                                              self.return_format)
        ob = self._parse(xml)
        mailing_list_file.guid = ob.mailing_list_guid
        return mailing_list_file
    
    def process_mailing(self, mailing_guid, submit=False, partial_process=True, **args):
        args['ReturnFormat'] = self.return_format
        for k, v in PROCESS_MAILING.items():
            if not args.has_key(k):
                args[k] = v
        xml = self.service.ProcessMailing(self.username, self.password,
                                          mailing_guid, self.source,
                                          submit, partial_process,
                                          args['max_price_ex_vat'], 
                                          args['po_reference'],
                                          args['payment_method'], 
                                          args['skip_preview_image_generation'], 
                                          args['email_success_list'],
                                          args['email_error_list'], 
                                          args['http_post_on_success'],
                                          args['http_post_on_error'], 
                                          self.return_format)
        return self._parse(xml).success
    
    def get_process_status(self, mailing_guid):
        xml = self.service.GetStatus(self.username, self.password,
                                      mailing_guid, self.return_format)
        return self._parse(xml).status
    
    def get_topup_balance(self):
        """ Returns a float representing current balance for a topup account """
        xml = self.service.GetBalance(self.username, self.password, 
                                      'Topup', self.return_format)
        return float(self._parse(xml).current_balance)
    
    def get_invoice_balance(self):
        """ Returns a float representing current balance for a topup account """
        xml = self.service.GetBalance(self.username, self.password, 
                                      'Invoice', self.return_format)
        return float(self._parse(xml).current_balance)
    
    def delete_mail_pack(self, mailing_guid):
        xml = self.service.DeleteMailPack(self.username, self.password, 
                                          mailing_guid, self.return_format)
        return self._parse(xml).success
    
    def delete_mailing_list(self, mailing_guid):
        xml = self.service.DeleteMailingList(self.username, self.password, 
                                             mailing_guid, self.return_format)
        return self._parse(xml).success
    
    def add_self(self, mailing_guid):
        xml = self.service.DeleteMailingList(self.username, self.password, 
                                             mailing_guid, self.return_format)
        return self._parse(xml).success
    
    def auto_correct_addresses(self, mailing_guid, correction_method='Cost'):
        xml = self.service.AutoCorrectAddresses(self.username, self.password, 
                                             mailing_guid, correction_method,
                                             self.return_format)
        return self._parse(xml).success
    
    def cancel_mailing_approval(self, mailing_guid):
        xml = self.service.CancelMailingApproval(self.username, self.password, 
                                                 mailing_guid, self.return_format)
        return self._parse(xml).success