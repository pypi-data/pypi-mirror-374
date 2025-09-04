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
import os
import string
from pathlib import Path
from typing import Any, Callable

from dateutil.parser import ParserError
from majormode.perseus.constant.contact import ContactName
from majormode.perseus.model.contact import Contact
from majormode.perseus.model.country import Country, InvalidCountryCode
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils import cast
from majormode.perseus.utils import module_utils

from majormode.xebus.constant.family_sheet import DEFAULT_FIELD_NAME_IS_CHILD_REMOVED
from majormode.xebus.constant.family_sheet import DEFAULT_SECTION_NAME_CHILD
from majormode.xebus.constant.family_sheet import DEFAULT_SHEET_FIELD_NAMES_FAMILY_PROPERTY_NAMES_MAPPING
from majormode.xebus.constant.family_sheet import FamilyPropertyName
from majormode.xebus.model.family import FamilyPropertyValueType
from majormode.xebus.model.sectioned_sheet import SectionedSheet
from majormode.xebus.utils import csv_utils
from majormode.xebus.utils import normalization_utils


# Define the absolute path to the data of this Python library.
#
# The data of this Python library are located in a folder ``data`` located
# at the root path of this Python library.
#
# We have organized our Python modules in a source folder ``src`` located
# at the root path of this Python library, therefore the source depth is
# ``1`` (not ``0``).
LIBRARY_DATA_PATH = os.path.join(
    module_utils.get_project_root_path(__file__, __name__, 1),
    'data'
)


class FamilyDataSectionedSheet(SectionedSheet):
    """
    A sectioned sheet containing family data of an organization.
    """
    def __convert_field_boolean_value(self, value: str) -> bool:
        """
        Return the boolean value corresponding to the specified string
        representation.


        :note: We cannot make this function static because it must respect a
            common interface with other data conversion functions, some of
            which need access to protected/private members of this class.


        :param value: A string representation of a boolean.


        :return: A boolean.
        """
        return cast.string_to_boolean(value)

    def __convert_field_date_value(self, value: str) -> datetime.datetime:
        """
        Return the date value of a property of the family list data.


        :note: We cannot make this function static because it must respect a
            common interface with other data conversion functions, some of
            which need access to protected/private members of this class.


        :param value: A string representation of a date complying with ISO
            8601.


        :return: A date.


        :raise ValueError: If the string representation of the date doesn't
            comply with ISO 8601.
        """
        try:
            date = cast.string_to_date(value)
        except (ParserError, OverflowError) as error:
            logging.error(f"Invalid string representation \"{value}\" of a date")
            raise ValueError(str(error))

        return date

    def __convert_field_email_address_value(self, value: str | None) -> Contact | None:
        """
        Return the contact information representing the specified email
        address.


        :note: We cannot make this function static because it must respect a
            common interface with other data conversion functions, some of
            which need access to protected/private members of this class.

        :param value: A string representation of an email address.

        :return: A contact information.
        """
        return value and Contact(
            ContactName.EMAIL,
            value.lower(),
            is_primary=True,
            strict=True
        )

    def __convert_field_phone_number_value(self, value: str | None) -> Contact | None:
        """
        Return the contact information representing the specified phone number.


        :note: We cannot make this function static because it must respect a
            common interface with other data conversion functions, some of
            which need access to protected/private members of this class.

        :param value: A string representation of an international phone number.


        :return: A contact information.
        """
        if not value:
            return None

        # Remove any character from the value that is not a number or the sign
        # ``+``.
        cleanse_value = ''.join([
            c
            for c in value
            if c in string.digits or c == '+'
        ])

        return value and Contact(
            ContactName.PHONE,
            cleanse_value,
            is_primary=True,
            strict=True
        )

    def __convert_field_grade_name_value(self, value: str) -> int | None:
        """
        Return the level of an educational grade.


        :param value: The name of an education grade.


        :return: The corresponding level for this education grade.  It
            generally corresponds to the number of the year a pupil has
            reached in this given educational stage for this grade.
        """
        if cast.is_undefined(value):
            return None

        key = normalization_utils.normalize_key(value)

        grade_level = self.__grades_names_mapping.get(key)
        if grade_level is None:
            message = f"Invalid string representation \"{value}\" of a grade name"
            logging.error(message)
            raise ValueError(message)

        return grade_level

    def __convert_field_language_value(self, value: str) -> Locale | None:
        """
        Return the locale corresponding to the string representation of a
        language.


        :param value: A string representation of a language.


        :return: A locale.


        :raise ValueError: If the value is not a valid string representation
            of a language.
        """
        if cast.is_undefined(value):
            return None

        key = normalization_utils.normalize_key(value)

        try:
            locale = cast.string_to_locale(key)
        except Locale.MalformedLocaleException as error:
            locale = self.__languages_names_mapping and self.__languages_names_mapping.get(key)
            if not locale:
                logging.error(f"Invalid string representation \"{value}\" of a language")
                raise ValueError(str(error))

        return locale

    def __convert_field_nationality_value(self, value: str) -> Country | None:
        """
        Return the country corresponding to the string representation of a
        nationality.


        :param value: A string representation of a nationality.


        :return: A country.


        :raise ValueError: If the value is not a valid string representation
            of a nationality.
        """
        if cast.is_undefined(value):
            return None

        key = normalization_utils.normalize_key(value)

        try:
            country = Country.from_string(key)
        except InvalidCountryCode as error:
            country = self.__nationalities_names_mapping and self.__nationalities_names_mapping.get(key)
            if not country:
                logging.error(f"Invalid string representation \"{value}\" of a nationality")
                raise ValueError(str(error))

        return country

    # Mapping between family properties and functions responsible for
    # converting their values from Google Sheet data.
    FIELD_VALUE_CONVERTERS: dict[FamilyPropertyName, Callable[[Any, str], Any]] = {
        FamilyPropertyName.child_date_of_birth: __convert_field_date_value,
        FamilyPropertyName.child_grade_level: __convert_field_grade_name_value,
        FamilyPropertyName.child_languages: __convert_field_language_value,
        FamilyPropertyName.child_nationalities: __convert_field_nationality_value,
        FamilyPropertyName.child_use_transport: __convert_field_boolean_value,
        FamilyPropertyName.primary_guardian_email_address: __convert_field_email_address_value,
        FamilyPropertyName.primary_guardian_languages: __convert_field_language_value,
        FamilyPropertyName.primary_guardian_nationalities: __convert_field_nationality_value,
        FamilyPropertyName.primary_guardian_phone_number: __convert_field_phone_number_value,
        FamilyPropertyName.secondary_guardian_email_address: __convert_field_email_address_value,
        FamilyPropertyName.secondary_guardian_languages: __convert_field_language_value,
        FamilyPropertyName.secondary_guardian_nationalities: __convert_field_nationality_value,
        FamilyPropertyName.secondary_guardian_phone_number: __convert_field_phone_number_value,
    }

    def __export_to_family_data_rows(self) -> list[dict[FamilyPropertyName, FamilyPropertyValueType]]:
        """
        Exports the rows from the sectioned sheet to a list of key/value rows
        with keys that have been normalized.

        The two-row header of sectioned sheet is not returned.

        :note: The value of fields is not converted to their respective
            appropriate Python type.


        :return: An array of where each entry corresponds to the information
            of a child and their guardianships.
        """
        rows: list[dict[FamilyPropertyName, FamilyPropertyValueType]] = []

        for row_index in range(self.data_row_count):
            # Check whether the current row is empty, meaning that we have reached
            # the end of the family data list.
            if self.__is_row_empty(row_index):
                break

            # Check whether the child has been marked as no longer with the school
            # and should be removed from the list.
            is_child_removed = cast.string_to_boolean(
                self.get_field_value(
                    row_index,
                    DEFAULT_SECTION_NAME_CHILD,
                    DEFAULT_FIELD_NAME_IS_CHILD_REMOVED,
                    is_required=True
                )
            )

            if is_child_removed:
                continue

            # Convert the sheet fields names and their values.
            fields = {}
            for sheet_section_name, sheet_fields_names in DEFAULT_SHEET_FIELD_NAMES_FAMILY_PROPERTY_NAMES_MAPPING.items():
                for sheet_field_name, field_name in sheet_fields_names.items():
                    sheet_field_value = self.get_field_value(
                        row_index,
                        sheet_section_name,
                        sheet_field_name,
                        is_required=False
                    )

                    field_value_converter_function = self.FIELD_VALUE_CONVERTERS.get(field_name)
                    field_value = sheet_field_value if field_value_converter_function is None \
                        else field_value_converter_function(self, sheet_field_value)

                    fields[field_name] = field_value

            rows.append(fields)

        return rows

    def __init__(
            self,
            rows: list[list[str]],
            grades_names_mapping: dict[str, int],
            languages_names_mapping: dict[str, Locale] | None = None,
            nationalities_names_mapping: dict[str, Country] | None = None
    ):
        """
        Build a family sheet from rows read from a sectioned sheet (e.g.,
        Google Sheets, CSV file).


        :param rows: The rows of the family data sheet of an organization,
            including a two-row header declaring the sections and subsections
            of the family data sheet.
        """
        super().__init__(rows)

        self.__family_data_rows: list[dict[FamilyPropertyName, Any]] | None = None

        self.__grades_names_mapping: dict[str, int] = normalization_utils.normalize_names_codes_mapping(grades_names_mapping)

        self.__languages_names_mapping: dict[str, Locale] = normalization_utils.normalize_names_codes_mapping(
            languages_names_mapping or self.__load_languages_names_mapping_from_default_csv_file()
        )

        self.__nationalities_names_mapping: dict[str, Country] = normalization_utils.normalize_names_codes_mapping(
            nationalities_names_mapping or self.__load_nationalities_names_mapping_from_default_csv_file()
        )

    def __is_row_empty(
            self,
            row_index: int
    ) -> bool:
        """
        Indicate if the specified row is empty.


        :param row_index: The index of the row in the sheet.


        :return: ``True`` if the row is empty; ``False`` otherwise.
        """
        # Check whether some fields contain a value.
        #
        # :note: The commented code below is a shorter version, but it requires
        #     checking each field, which is slower.
        #
        # ```python
        # non_empty_fields = [
        #     field_name
        #     for sheet_section_name, sheet_fields_names in self.DEFAULT_SHEET_FIELD_NAMES_FAMILY_PROPERTY_NAMES_MAPPING.items()
        #     for sheet_field_name, field_name in sheet_fields_names.items()
        #     if field_name != FamilyPropertyName.child_use_transport
        #        and self.get_field_value(
        #            row_index,
        #            sheet_section_name,
        #            sheet_field_name,
        #            is_required=False
        #        ) is not None
        # ]
        #
        # return not non_empty_fields
        # ```
        for sheet_section_name, sheet_fields_names in DEFAULT_SHEET_FIELD_NAMES_FAMILY_PROPERTY_NAMES_MAPPING.items():
            for sheet_field_name, field_name in sheet_fields_names.items():
                # The field `FamilyPropertyName.child_use_transport` is never empty
                # because it contains either the value `TRUE` or `FALSE`.
                if field_name != FamilyPropertyName.child_use_transport:
                    sheet_field_value = self.get_field_value(
                        row_index,
                        sheet_section_name,
                        sheet_field_name,
                        is_required=False
                    )

                    # Check the value of this field is defined.
                    #
                    # :note: ``False`` value is treated as ``None`` (cf. ``DEFAULT_FIELD_NAME_IS_CHILD_REMOVED``)
                    if sheet_field_value:
                        return False

        return True

    @staticmethod
    def __load_languages_names_mapping_from_default_csv_file() -> dict[str, Locale]:
        """
        Return the mapping between the names of languages and their respective
        ISO 639-3:2007 codes as identified in the default languages file.


        :note: This function is not used at the moment.  The language names
            mapping is dynamically loaded from the sheet ``(Languages)`` of
            the school organization's Google Sheets.  This sheet is actually
            imported from a common Google Sheets controlled by the Xebus team.
            It is easier for the Xebus team to update this Google Sheets
            rather to update the data of this Python library.  But, as result,
            the loading of the language names mapping is slower.


        :return: A dictionary representing a mapping between the names of
            languages (the keys), localized in the specified language, and
            their corresponding ISO 639-3:2007 codes (the values).
        """
        default_file_path_name = Path(LIBRARY_DATA_PATH, f'languages_names.csv')
        return csv_utils.load_languages_names_iso_codes_mapping_from_csv_file(default_file_path_name)

    @staticmethod
    def __load_nationalities_names_mapping_from_default_csv_file() -> dict[str, Country]:
        """
        Return the mapping between the names of nationalities and their
        respective ISO 3166-1 alpha-2 codes as identified in the default
        nationalities file.


        :note: This function is not used at the moment.  The country names
            mapping is dynamically loaded from the sheet ``(Countries)`` of
            the school organization's Google Sheets.  This sheet is actually
            imported from a common Google Sheets controlled by the Xebus team.
            It is easier for the Xebus team to update this Google Sheets
            rather to update the data of this Python library.  But, as result,
            the loading of the country names mapping is slower.


        :return: A dictionary representing a mapping between the names of
            nationalities (the keys), localized in the specified langauge, and
            their corresponding ISO 3166-1 alpha-2 codes (the values).
        """
        default_file_path_name = Path(LIBRARY_DATA_PATH, f'countries_names.csv')
        return csv_utils.load_nationalities_names_iso_codes_mapping_from_csv_file(default_file_path_name)

    @property
    def rows(self) -> list[dict[FamilyPropertyName, FamilyPropertyValueType]]:
        """
        Return the family data rows of this sheet.


        :note: The value of fields is not converted to their respective
            appropriate Python type.


        :return: A list of rows each corresponding to a dictionary whose key
            identifies the normalized name of the family data field.
        """
        if self.__family_data_rows is None:
            self.__family_data_rows = self.__export_to_family_data_rows()

        return self.__family_data_rows
