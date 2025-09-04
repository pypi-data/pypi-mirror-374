# Copyright (C) 2024 Majormode.  All rights reserved.
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

import datetime
import logging
from typing import Union

from majormode.perseus.constant.contact import ContactName
from majormode.perseus.model.contact import Contact
from majormode.perseus.model.country import Country
from majormode.perseus.model.locale import DEFAULT_LOCALE, Locale
from majormode.perseus.utils import cast
from majormode.xebus.constant.guardian import GuardianRole

from majormode.xebus.constant.family import FAMILY_PROPERTY_TYPES_VALIDATORS
from majormode.xebus.constant.family_sheet import FamilyPropertyName
from majormode.xebus.model.child import Child
from majormode.xebus.model.error import MissingPersonDataException
from majormode.xebus.model.guardian import Guardian
from majormode.xebus.model.guardian import Guardianship


# Declare the possible Python types of the value of a family property.
FamilyPropertyValueType = Union[
    Locale,
    Country,
    bool,
    datetime.datetime,
    int,
    str,
]


class FamilyData:
    """
    Represent the information of children and their respective guardians.
    """
    @staticmethod
    def __assert_data_values_types(rows: list[dict[FamilyPropertyName, FamilyPropertyValueType]]) -> None:
        """
        Check that the value of each family data property is of the correct
        data type.


        :param rows: The row of the family data of an organization.


        :raise ValueError: if the value of a property is of the wrong data
            type.
        """
        for row_index, row in enumerate(rows):
            for property_name, property_value in row.items():
                property_value_type_validator = FAMILY_PROPERTY_TYPES_VALIDATORS[property_name]
                if property_value and not property_value_type_validator(property_value):
                    raise ValueError(
                        f"The value of the property \"{property_name}\" at row {row_index} has "
                        f"the wrong type \"{type(property_value)}\")"
                    )

    def __build_child(
            self,
            row_index: int,
            strict_prosoponym: bool = False
    ) -> Child:
        """
        Build an object representing a child defined in the specified row of
        the family data list.


        :note: The function doesn't check, nor format, the child's first name,
            last name, and full name.


        :param row_index: The index of the row to read the child's information.


        :return: An object representing a child.


        :raise CountryNameNotFoundException: If the English name of the
            child's nationality is not defined in the core data.  Either this
            name is misspelled, either the core data are missing this name.

        :raise InvalidDateOfBirthException: If the child's birthdate is not
            formatted according the ISO 8601 specifications.

        :raise LanguageNameNotFoundException: If the English name of the
            child's language is not defined in the core data.  Either this
            name is misspelled, either the core data are missing this name.
        """
        # Read the child's information.
        sis_account_id = self.__get_property_value(row_index, FamilyPropertyName.child_sis_id, is_required=True)
        first_name = self.__get_property_value(row_index, FamilyPropertyName.child_first_name, is_required=True)
        last_name = self.__get_property_value(row_index, FamilyPropertyName.child_last_name, is_required=True)
        full_name = self.__get_property_value(row_index, FamilyPropertyName.child_full_name, is_required=True)
        dob = self.__get_property_value(row_index, FamilyPropertyName.child_date_of_birth, is_required=True)
        grade_level = self.__get_property_value(row_index, FamilyPropertyName.child_grade_level, is_required=True)
        class_name = self.__get_property_value(row_index, FamilyPropertyName.child_class_name, is_required=False)

        languages = self.__get_property_value(row_index, FamilyPropertyName.child_languages, is_required=False)
        if cast.is_undefined(languages):
            logging.warning(
                f"The child \"{sis_account_id}\" is declared with no spoken language; "
                f"we are using the default language \"{DEFAULT_LOCALE}\" as their spoken "
                f"language..."
            )
            languages = [DEFAULT_LOCALE]

        nationalities = self.__get_property_value(row_index, FamilyPropertyName.child_nationalities, is_required=False)
        use_transport = self.__get_property_value(row_index, FamilyPropertyName.child_use_transport, is_required=False)

        # Build the object representing the child.
        child = Child(
            sis_account_id,
            first_name,
            last_name,
            full_name,
            dob,
            grade_level,
            class_name=class_name,
            languages=languages,
            nationalities=nationalities,
            use_transport=use_transport
        )

        child = self.__index_child_in_cache(child)
        return child

    def __build_children_and_their_guardianships(
            self,
            row_index: int,
            strict_prosoponym: bool = False
    ) -> None:
        """
        Build and index the child and parents' information contained in the
        specified row of the family list data.


        :param row_index: The index of the data row to read.

        :param strict_prosoponym: Indicate whether full names MUST be
            formatted according to the lexical name related to the culture of
            each person.


        :raise ValueError: If the child or one of their parent has been
            defined multiple times but with different information.
        """
        child = self.__build_child(row_index)

        # Collect the information of the child's primary parent, and build the
        # guardianship between this primary parent and the child.
        primary_parent_guardianship = self.__build_primary_parent_guardianship(
            row_index,
            strict_prosoponym=strict_prosoponym
        )

        if primary_parent_guardianship:
            child.add_guardianship(primary_parent_guardianship)

        # Collect the information of the child's secondary parent, if any
        # defined, and build the guardianship between the secondary parent and
        # the child.
        secondary_parent_guardianship = self.__build_secondary_parent_guardianship(
            row_index,
            strict_prosoponym=strict_prosoponym
        )

        if secondary_parent_guardianship:
            child.add_guardianship(secondary_parent_guardianship)

        # Check that the child is declared with guardians.
        if not child.guardianships:
            raise ValueError(
                f"The child with SIS ID \"{child.sis_account_id}\" has no guardian"
            )

    def __build_families(self, strict_prosoponym: bool = False) -> None:
        """
        Build objects representing the children and their guardians from the
        family list data.

        The function reads each row of the family list data representing a
        child and the primary and possible the secondary guardians who are
        legally responsible for this child.


        :param strict_prosoponym: Indicate whether full names MUST be
            formatted according to the lexical name related to the culture of
            each person.


        :raise ValueError: If a child or one of their parent has been defined
            multiple times but with different information.
        """
        for row_index in range(len(self.__rows)):
            self.__build_children_and_their_guardianships(row_index, strict_prosoponym=strict_prosoponym)

    def __build_primary_parent_guardianship(
            self,
            row_index: int,
            strict_prosoponym: bool = False
    ) -> Guardianship | None:
        """
        Build the guardianship of the child with the primary parent.


        :param row_index: The index of the data row to read.

        :param strict_prosoponym: Indicate whether full name of the primary
            guardian MUST be formatted according to the lexical name related
            to the culture of the guardian.


        :return: The guardianship of the child with the primary parent, or
            ``None`` if the primary parent is ignored because their
            information is missing some required identifiers (such as a unique
            email address).
        """
        # Collect the primary parent's information.
        sis_account_id = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_sis_id)
        first_name = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_first_name)
        last_name = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_last_name)
        full_name = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_full_name)

        languages = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_languages, is_required=False)
        if cast.is_undefined(languages):
            logging.warning(
                f"The guardian \"{sis_account_id}\" is declared with no spoken language; "
                f"we are using the default language \"{DEFAULT_LOCALE}\" as their spoken "
                f"language..."
            )
            languages = [DEFAULT_LOCALE]

        nationalities = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_nationalities, is_required=False)
        email_address = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_email_address)
        phone_number = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_phone_number, is_required=False)

        contacts: list[Contact] = [email_address]
        if phone_number:
            contacts.append(phone_number)

        # Collect the postal address where the primary parent puts their child
        # in.
        home_address = self.__get_property_value(row_index, FamilyPropertyName.primary_guardian_home_address, is_required=False)

        # Build the objects representing the primary parent and their
        # guardianship towards the child.
        primary_parent = Guardian(
            sis_account_id,
            first_name,
            last_name,
            full_name,
            contacts=contacts,
            languages=languages,
            nationalities=nationalities
        )

        primary_parent = self.__index_parent_in_cache(primary_parent)

        # If the parent is defined with the same email address than another
        # parent, we ignore this parent from the family list.
        if primary_parent is None:
            return None

        primary_parent_guardianship = Guardianship(
            primary_parent,
            GuardianRole.legal,
            home_address
        )

        return primary_parent_guardianship

    def __build_secondary_parent_guardianship(
            self,
            row_index: int,
            strict_prosoponym: bool = False
    ) -> Guardianship | None:
        """
        Build the guardianship of the child with the secondary parent.


        :param row_index: The index of the data row to read.

        :param strict_prosoponym: Indicate whether full name of the secondary
            guardian MUST be formatted according to the lexical name related
            to the culture of the guardian.


        :return: The guardianship of the child with the secondary parent, or
            ``None`` if no secondary parent is defined for the child or the
            secondary parent is ignored because their information is missing
            some required identifiers (such as a unique email address).
        """
        # Collect the secondary parent's nominative information.
        sis_account_id = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_sis_id, is_required=False)
        first_name = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_first_name, is_required=False)
        last_name = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_last_name, is_required=False)
        full_name = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_full_name, is_required=False)
        languages = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_languages, is_required=False)
        nationalities = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_nationalities, is_required=False)
        email_address = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_email_address, is_required=False)
        phone_number = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_phone_number, is_required=False)

        contacts: list[Contact] = []
        if email_address:
            contacts.append(email_address)
        if phone_number:
            contacts.append(phone_number)

        # Collect the postal address where the secondary parent puts their child
        # in.
        home_address = self.__get_property_value(row_index, FamilyPropertyName.secondary_guardian_home_address, is_required=False)

        # Check that all the required information about a secondary parent are
        # provided defined, or none of them.
        required_values = [sis_account_id, first_name, last_name, full_name, languages, email_address]
        optional_values = [phone_number, home_address]
        all_values = required_values + optional_values

        if not any(all_values):
            return None  # No secondary parent is defined for the child.

        if cast.is_undefined(languages):
            logging.warning(
                f"The guardian \"{sis_account_id}\" is declared with no spoken language; "
                f"we are using the default language \"{DEFAULT_LOCALE}\" as their spoken "
                f"language..."
            )
            languages = [DEFAULT_LOCALE]

        if not all(required_values):
            if sis_account_id and full_name:
                message = f"The information required from the secondary guardian \"{full_name}\" " \
                          f"({sis_account_id}) is missing"
            else:
                stringified_defined_values = [
                    f"\"{required_value}\""
                    for required_value in required_values
                    if required_value
                ]
                defined_values_stringified_list = ', '.join(stringified_defined_values)
                message = f"The information of the secondary guardian is partially defined with" \
                          f"{defined_values_stringified_list}"

            logging.error(message)
            return None
            # raise MissingPersonDataException(message)

        # Build the objects representing the primary parent and their
        # guardianship towards the child.
        secondary_parent = Guardian(
            sis_account_id,
            first_name,
            last_name,
            full_name,
            contacts=contacts,
            languages=languages,
            nationalities=nationalities
        )

        secondary_parent = self.__index_parent_in_cache(secondary_parent)

        # If the parent is defined with the same email address than another
        # parent, we ignore this parent from the family list.
        if secondary_parent is None:
            return None

        secondary_parent_guardianship = Guardianship(
            secondary_parent,
            GuardianRole.legal,
            home_address=home_address
        )

        return secondary_parent_guardianship

    def __get_property_value(
            self,
            row_index: int,
            property_name: FamilyPropertyName,
            is_required: bool = True
    ) -> FamilyPropertyValueType | None:
        """
        Return the value of a property of the family list data.


        :param row_index: The row index of the property to return the value.  A
            row index starts with ``0``.

        :param property_name: The name of the properties to return the value.

        :param is_required: Indicate whether this property MUST contain a
            value.


        :return: The property value.
        """
        if row_index < 0 or row_index >= len(self.__rows):
            raise IndexError(f"Row index {row_index} out of bound")

        value = self.__rows[row_index][property_name]

        if is_required and cast.is_undefined(value):
            error_message = f'The required field "{property_name}" is empty at row {row_index}'
            logging.error(error_message)
            raise ValueError(error_message)

        return value if value else None

    def __init__(
            self,
            rows: list[dict[FamilyPropertyName, FamilyPropertyValueType]],
            strict_prosoponym: bool = False
    ):
        """
        Build a family list from an array of children and their parents.


        :param rows: A list of row of children and their parents.


        :param strict_prosoponym: Indicate whether full names MUST be
            formatted according to the lexical name related to the culture of
            each person.
        """
        self.__assert_data_values_types(rows)

        self.__rows = rows

        # The cache of children indexed with their SIS identifier.
        self.__children_cache: dict[str, Child] = {}

        # The cache of parents indexed with SIS identifier, their email
        # address, and their possible phone number.
        self.__parents_cache: dict[str, Guardian] = {}

        self.__build_families(strict_prosoponym=strict_prosoponym)

    def __index_child_in_cache(self, child: Child) -> Child:
        """
        Index a child in the app's cache for further access.


        :param child: A child.


        :return: The child instance passed to the function if this instance
            was not already cached, otherwise the instance that is already in
            the cache.


        :raise ValueError: If the child has already been defined but with
            different information.
        """
        cached_child = self.__children_cache.get(child.sis_account_id)

        if cached_child:
            # Check the child has not been cached with different information.
            if cached_child != child:
                raise ValueError(
                    f"The child {child.sis_account_id} has already been defined but with "
                    "different information"
                )
        else:
            # Cache the child with their SIS identifier.
            self.__children_cache[child.sis_account_id] = child

        return cached_child or child

    def __index_parent_in_cache(self, parent: Guardian) -> Guardian | None:
        """
        Index a parent in the app's cache for further access.


        :param parent: A parent.


        :return: The parent instance passed to the function if this instance
            was not already cached, otherwise the instance that is already in
            the cache.

            If the parent is defined with the same email address than another
            parent, the function returns ``None`` to ignore this parent from the
            family list.


        :raise ValueError: If the parent has already been defined but with
            different information.
        """
        cached_parents = [
            cached_parent
            for cached_parent in [
                self.__parents_cache.get(parent.sis_account_id),
                self.__parents_cache.get(parent.email_address),
                self.__parents_cache.get(parent.phone_number)
            ]
            if cached_parent
        ]

        if cached_parents:
            # It may happen that this parent is in fact another parent declared with
            # the same identifier (e.g., telephone number) as the parent in the
            # cache.  In such a case, we will remove the declaration of this
            # duplicate identifier (if this case is allowed) and we will add this
            # parent to the cache.
            is_parent_cached = True

            # Check that the parent has not been cached with different information,
            # or another parent has similar identifier (email address, phone number).
            for cached_parent in cached_parents:
                if cached_parent and cached_parent != parent:
                    if parent.sis_account_id == cached_parent.sis_account_id:
                        # The parent has been declared multiple times but with different
                        # information.
                        raise ValueError(
                            f"The guardian \"{parent.sis_account_id}\" has already been defined but "
                            "with different information"
                        )

                    else:
                        # Another parent has been declared with the same email address or phone
                        # number.
                        if parent.email_address == cached_parent.email_address:
                            # Two parents MUST NOT be declared with the same email address.  We are
                            # ignoring this parent.
                            logging.warning(
                                f"The guardian \"{parent.sis_account_id}\" has been declared with the same "
                                f"email address \"{parent.email_address}\" than the other guardian "
                                f"\"{cached_parent.sis_account_id}\"; we are ignoring this guardian "
                                f"\"{parent.sis_account_id}\"..."
                            )
                            return None

                        elif parent.phone_number == cached_parent.phone_number:
                            # Some school organizations allow two parents to be declared with the
                            # same telephone number. We remove the telephone number from the second
                            # parent's declaration.
                            logging.warning(
                                f"The guardian \"{parent.sis_account_id}\" has been declared with the "
                                f"same phone number \"{parent.phone_number}\" than the other guardian "
                                f"\"{cached_parent.sis_account_id}\"; we are removing this phone number "
                                f"from the guardian \"{parent.sis_account_id} information..."
                            )
                            parent.remove_contact(
                                Contact(ContactName.PHONE, parent.phone_number)
                            )
                            is_parent_cached = False

                        else:
                            # :note: Folks! Is there another identifier that we are not aware of?!
                            raise ValueError(
                                f"The guardian \"{parent.sis_account_id}\" has been declared with a same "
                                f"identifier than the other guardian \"{cached_parent.sis_account_id}\". "
                                "The problem is that the developers of this library did not handle this "
                                "case."
                            )

            if is_parent_cached:
                return cached_parent

        # Cache the parent with their SIS identifier, email address, and phone
        # number if any defined.
        self.__parents_cache[parent.sis_account_id] = parent
        self.__parents_cache[parent.email_address] = parent
        if parent.phone_number:
            self.__parents_cache[parent.phone_number] = parent

        return parent

    @property
    def children(self) -> list[Child]:
        """
        Return the list of the children enrolled to the school organization.


        :return: The list of the children enrolled to the school organization.
        """
        return list(set(self.__children_cache.values()))

    @property
    def parents(self) -> list[Guardian]:
        """
        Return the list of parents whose children enrolled to the school
        organization.


        :return: The list of parents.
        """
        return list(set(self.__parents_cache.values()))
