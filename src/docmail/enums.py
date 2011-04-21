class Enum(object):
    pass

class ProductType(Enum):
    A4Letter = 'A4Letter'
    BusinessCard = 'BusinessCard'
    GreetingCard = 'GreetingCard'
    Postcard = 'Postcard'

class DocumentType(Enum):
    A4Letter = 'A4Letter'
    BusinessCard = 'BusinessCard'
    GreetingCardA5 = 'GreetingCardA5'
    PostcardA5 = 'PostcardA5'
    PostcardA6 = 'PostcardA6'
    PostcardA5Right = 'PostcardA5Right'
    PostcardA6Right = 'PostcardA6Right'

class DeliveryType(Enum):
    First = 'First'
    Standard = 'Standard'
    Courier = 'Courier'

class AddressNameFormat(Enum):
    FullName = 'Full Name'
    FirstnameSurname = 'Firstname Surname'
    TitleInitialSurname = 'Title Initial Surname'
    TitleSurname = 'Title Surname'
    TitleFirstnameSurname = 'Title Firstname Surname'    

class MinEnvelopeSize(Enum):
    C4 = 'C4'
    C5 = 'C5'

class AddressFont(Enum):
    Arial10 = 'Arial10'
    Arial11 = 'Arial11'
    Arial12 = 'Arial12'
    Arial13 = 'Arial13'
    Arial14 = 'Arial14'
    Courier10 = 'Courier10'
    Courier11 = 'Courier11'
    Courier12  = 'Courier12'
    Courier13 = 'Courier13'
    Courier14 = 'Courier14'
    Gotham9 = 'Gotham9'
    Gotham10  = 'Gotham10'
    Gotham12 = 'Gotham12'
    Helvetica12 = 'Helvetica12'
    Helvetica13  = 'Helvetica13'
    Helvetica14 = 'Helvetica14'
    MetaOT10 = 'MetaOT10'
    MetaOT11 = 'MetaOT11'
    MetaOT12  = 'MetaOT12'
    Trebuchet10 = 'Trebuchet10'
    Trebuchet11 = 'Trebuchet11'
    Trebuchet12  = 'Trebuchet12'
    Verdana10 = 'Verdana10'
    Verdana11 = 'Verdana11'
    Verdana12 = 'Verdana12'