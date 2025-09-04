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

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from majormode.perseus.constant.contact import ContactName
from majormode.perseus.model.contact import Contact
from majormode.perseus.model.country import Country
# from majormode.perseus.model.country import Country
from majormode.perseus.model.locale import DEFAULT_LOCALE
from majormode.perseus.model.locale import Locale


class Person:
    # List of the attributes to compare in order to determine if two
    # `Guardian` objects are identical
    COMPARISON_ATTRIBUTE_NAMES = [
        'email_address',
        'first_name',
        'full_name',
        'languages',
        'last_name',
        'nationalities',
        'phone_number',
        'sis_account_id',
    ]

    def __eq__(self, other: Person) -> bool:
        """
        Indicate if this person and the other person correspond to this person.

        The two people correspond to the same person when they have the same
        School Information System (SIS) identifier and when their information
        are identical.


        :param other: Another person.


        :return: ``True`` if the other person corresponds to this person;
            ``False`` otherwise.
        """
        if other is None:
            return False

        if not isinstance(other, Person):
            raise TypeError(
                f"The argument 'other' MUST be an instance of {self.__class__.__name__}; "
                f"{other.__class__.__name__} provided"
            )

        for attribute_name in self.COMPARISON_ATTRIBUTE_NAMES:
            this_attribute_value = getattr(self, attribute_name)
            other_attribute_value = getattr(other, attribute_name)
            if this_attribute_value != other_attribute_value:
                # logging.debug(
                #     f"The value \"{this_attribute_value}\" of the attribute \"{attribute_name}\" "
                #     f"of this instance \"{self.__class__.__name__}\" differs from the value "
                #     f"\"{other_attribute_value}\" of the same attribute of the other instance "
                #     f"\"{other.__class__.__name__}\""
                # )
                return False

        return True

    def __get_contact_value(self, property_name: ContactName) -> str | None:
        """
        Return the contact information of the person corresponding to a
        contact type.

        :param property_name: The type of contact to return.


        :return: The contact information corresponding to the specified
            contact type.
        """
        if not self._contacts:
            return None

        property_values = [
            contact.property_value
            for contact in self._contacts
            if contact.property_name == property_name
        ]

        return None if len(property_values) == 0 else property_values[0]

    def __hash__(self) -> int:
        return hash(self._sis_account_id)

    def __init__(
            self,
            sis_account_id: str,
            first_name: str,
            last_name: str,
            full_name: str,
            account_id: UUID = None,
            contacts: Contact | list[Contact] = None,
            languages: Locale | list[Locale] = None,
            nationalities: Country | list[Country] = None
    ):
        """
        Build a new object representing a family member such as a child or a
        parent.


        :param sis_account_id: The School Information System (SIS) identifier
            of the person.

        :param first_name: The forename (also known as *given name*) of the
            person.

        :param last_name: The surname (also known as *family name*) of the
            person.

        :param full_name: The complete personal name by which the user is
            known, including their surname, forename and middle name(s), in
            the correct lexical name order depending on the culture of this
            person.

        :param account_id: The identifier of the person's user account
            registered in the service database.

        :param contacts: The contact information of the person.

        :param languages: The spoken languages of the person.

        :param nationalities: The countries the person's citizenship belongs
            to.


        :raise ValueError: If the argument ``sis_account_id`` is ``None``.
        """
        if not sis_account_id:
            raise ValueError(f'The SIS identifier of "{full_name}" is undefined ({account_id})')

        self._sis_account_id = sis_account_id
        self._first_name = first_name
        self._last_name = last_name
        self._full_name = full_name

        self._account_id = account_id
        self._contacts = [contacts] if isinstance(contacts, Contact) else contacts

        self._languages = [languages] if isinstance(languages, Locale) else languages or [DEFAULT_LOCALE]
        self._nationalities = [nationalities] if isinstance(nationalities, Country) else nationalities

        self.__password = None

    @property
    def account_id(self) -> UUID | None:
        return self._account_id

    @account_id.setter
    def account_id(self, account_id: UUID) -> None:
        if not account_id:
            raise AttributeError("Can't set a null ID")

        if self._account_id == account_id:
            return

        if self._account_id:
            raise AttributeError("Can't set ID when already defined")

        self._account_id = account_id

    @property
    def contacts(self) -> list[Contact]:
        return self._contacts

    @property
    def email_address(self) -> str:
        return self.__get_contact_value(ContactName.EMAIL)

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def languages(self) -> list[Locale]:
        return self._languages

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def nationalities(self) -> list[Country]:
        return self._nationalities

    @property
    def password(self) -> str:
        return self.__password

    @password.setter
    def password(self, password: str) -> None:
        self.__password = password

    @property
    def phone_number(self) -> str:
        return self.__get_contact_value(ContactName.PHONE)

    def remove_contact(self, contact: Contact) -> None:
        """
        Remove the specified contact from the person's information.


        :param contact: The contact to remove.
        """
        for i, existing_contact in enumerate(self._contacts):
            if existing_contact.property_name == contact.property_name \
               and existing_contact.property_value == contact.property_value:
                del self._contacts[i]
                break

    @property
    def sis_account_id(self) -> str:
        """
        Returns the School Information System (SIS) identifier of the person.


        :return: The person's SIS identifier.
        """
        return self._sis_account_id
