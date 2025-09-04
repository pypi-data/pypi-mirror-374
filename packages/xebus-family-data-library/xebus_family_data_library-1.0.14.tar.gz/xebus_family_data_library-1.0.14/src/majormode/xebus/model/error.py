# Copyright (C) 2021 Majormode.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Majormode or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Majormode.
#
# MAJORMODE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY
# OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT.  MAJORMODE SHALL NOT BE LIABLE FOR ANY
# LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING
# OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from majormode.xebus.model.person import Person


class CountryNameNotFoundException(Exception):
    """
    Indicate that a Family List CSV document refers to a country name that
    is not registered in the core data.
    """


class DuplicatedContactInformationException(Exception):
    """
    Indicate that a contact information is defined for two or more parents.
    """


class DuplicatedEmailAddressException(DuplicatedContactInformationException):
    """
    Indicate that an email address is used by two or more parents.
    """


class DuplicatedIdentifierException(Exception):
    """
    Indicate that a School Information System (SIS) identifier is used for
    multiple people (children and/or parents).
    """


class DuplicatedPhoneNumberException(DuplicatedContactInformationException):
    """
    Indicate that a phone number is defined for by two or more parents.
    """


class LanguageNameNotFoundException(Exception):
    """
    Indicate that a Family List CSV document refers to a language name
    that is not registered in the core data.
    """


class InvalidDateOfBirthException(Exception):
    """
    Indicate that a child's birth of date has an invalid format.
    """


class MismatchedParentContactInformationException(Exception):
    """
    Indicate that a parent has been declared two times with two different
    contact information.
    """


class MismatchedParentEmailAddressException(MismatchedParentContactInformationException):
    """
    Indicate that a parent has been declared two times with two different
    email addresses.
    """


class MismatchedParentPhoneNumberException(MismatchedParentContactInformationException):
    """
    Indicate that a parent has been declared two times with two different
    phone numbers.
    """


class MissingPersonDataException(Exception):
    """
    Indicates that a person's data is missing.
    """


class PersonNameIncorrectlyFormattedException(Exception):
    """
    Indicate the first name, the last name, and/or the full name of a
    person is incorrectly formatted.
    """
    def __init__(self, message: str, person: Person):
        super(message)
        self.__person = person

    @property
    def person(self) -> Person:
        return self.__person


class UndefinedClassNameException(Exception):
    """
    Indicate that the class name of a child has not been defined in the
    school's data.
    """


class UndefinedEducationGradeNameException(Exception):
    """
    Indicate that the name of the education grade of a child has not been
    defined in the school's data.
    """
