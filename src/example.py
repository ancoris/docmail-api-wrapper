from docmail import client

USERNAME = ''   # a valid docmail username
PASSWORD = ''   # a valid docmail password
SOURCE = ''     # a string to describe your app

# create a client ...
docmail_client = client.Client(USERNAME, PASSWORD, SOURCE)

# create a new mailing ...
mailing = client.Mailing(name='api wrapper test')
mailing = docmail_client.create_mailing(mailing)

# to make a change to an existing mailing ...
mailing.name = 'api wrapper test edited'
docmail_client.update_mailing(mailing)

# to retrieve an existing mailing ...
mailing = docmail_client.get_mailing('enter-your-mailing-guid')

# add a template to a mailing ...
template_file = client.TemplateFile('sample.doc')
docmail_client.add_template_file(mailing.guid, template_file)

# add a mailing list ...
mailing_list_file = client.MailingListFile('AddressList.csv')
docmail_client.add_mailing_list_file(mailing.guid, mailing_list_file)

# get the users topup balance ...
balance = docmail_client.get_topup_balance()
# or invoice balance ...
balance = docmail_client.get_invoice_balance()

# delete a mailpack ...
docmail_client.delete_mail_pack(mailing.guid)

# delete a mailing_list ...
docmail_client.delete_mailing_list(mailing.guid)

# process a mailing ...
docmail_client.process_mailing(mailing.guid, False, True)

# approve a mailing ...
docmail_client.process_mailing(mailing.guid, True, False)

# cancel a mailing approval ...
docmail_client.cancel_mailing_approval(mailing.guid)
