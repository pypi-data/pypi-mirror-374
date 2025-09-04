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


class SectionedSheetBaseException(Exception):
    pass


class EmptyFieldException(SectionedSheetBaseException):
    """
    Indicate that a field of a given section is empty.
    """
    def __init__(
            self,
            section_name: str,
            field: HeaderField,
            row_number: int
    ):
        super().__init__()
        self.__field = field
        self.__row_number = row_number
        self.__section_name = section_name

    def __str__(self):
        return (
            f'The field "{self.__field.name}" of the section "{self.__section_name}" is empty '
            f"at column {self.column_number} / row {self.row_number})"
        )

    @property
    def column_number(self) -> int:
        return self.__field.column_index + 1

    @property
    def field_name(self) -> str:
        return self.__field.name

    @property
    def row_number(self) -> int:
        return self.__row_number

    @property
    def section_name(self) -> str:
        return self.__section_name


class FieldNotFoundException(SectionedSheetBaseException):
    """
    Indicate that the name of a field of a given section does not exist in
    a sheet.
    """
    def __init__(self, section_name: str, field_name: str):
        super().__init__()
        self.__field_name = field_name
        self.__section_name = section_name

    def __str__(self) -> str:
        return (
            f'The requested field "{self.__field_name}" of the section "{self.__section_name}" '
            "does not exist in the sheet"
        )

    @property
    def field_name(self) -> str:
        return self.__field_name

    @property
    def section_name(self) -> str:
        return self.__section_name


class SectionNotFoundException(SectionedSheetBaseException):
    """
    Indicate that the name of a section does not exist in a sheet.
    """
    def __init__(self, section_name: str):
        super().__init__()
        self.__section_name = section_name

    def __str__(self) -> str:
        return f'The requested section "{self.__section_name}" does not exist in the sheet'

    @property
    def section_name(self) -> str:
        return self.__section_name


class HeaderField:
    """
    Represent a field of a section of a sheet.

    A field corresponds to a cell of a sheet header, located on the
    second row of this document.
    """
    def __init__(self, name: str, column_index: int):
        """
        Build a field of a section of a sheet.


        :param name: The name of the field.

        :param column_index: The column index of the field in the sheet.
            A column index starts with ``0``.
        """
        self.__name = name
        self.__column_index = column_index

    @property
    def name(self) -> str:
        """
        Return the name of the field.


        :return: The name of the field.
        """
        return self.__name

    @property
    def column_index(self) -> int:
        """
        Return the column index of the field in the sheet.


        :return: The column index of the field in the sheet.  A column
            index starts with ``0``.
        """
        return self.__column_index


class HeaderSection:
    """
    Represent a header section of a sheet.

    A section corresponds to one or more cells of a sheet header, located
    in the first row of this document.  A section groups as many
    subsections defined in the adjacent cells of the sheet located
    below in the second row of this document.
    """
    def __init__(self, name: str, column_index: int, fields: dict[str, HeaderField]):
        """
        Build a header section of a sheet.


        :param name: The name of the section.

        :param column_index: The index of column at which the section begins
            int the sheet.  A column index starts with ``0``.

        :param fields: The list of the fields that compose this section.
        """
        self.__name = name
        self.__column_index = column_index
        self.__fields = fields

    @property
    def name(self) -> str:
        """
        Return the name of the section.


        :return: The name of the section.
        """
        return self.__name

    @property
    def fields(self) -> dict[str, HeaderField]:
        """
        Return the values of the section's fields.


        :return: The values of the section's fields.
        """
        return self.__fields

    @property
    def column_index(self) -> int:
        """
        Return the index of the column at which the section begins in the CSV
        document.


        :return: The index of the column at which the section begins in the
            sheet.  A column index starts with ``0``.
        """
        return self.__column_index


class SectionedSheetHeader:
    """
    Represent the header of a sectioned sheet.

    The header is composed of two rows:

    - The first row identified the name of the sections
    - The second row identified the name of each field of these sections.

    ```
    +===========+===========+===========+===========+===========+===...
    | Section 1 |           |           | Section 2 |           |
    +-----------+-----------+-----------+-----------+-----------+---...
    | Field 1.1 | Field 1.2 | Field 1.3 | Field 2.1 | Field 2.2 |
    +===========+===========+===========+===========+===========+===...
    |           |           |           |           |           |
    .           .           .           .           .           .
    ```
    """
    def __init__(self, sections: dict[str, HeaderSection]):
        """
        Build the header of a sectioned sheet.


        :param sections: A dictionary of sections where the key corresponds to
            the name of a section and the value represents the corresponding
            section.
        """
        self.__sections = sections

    @property
    def sections(self) -> dict[str, HeaderSection]:
        return self.__sections

    @staticmethod
    def from_rows(rows: list[list[str]]) -> SectionedSheetHeader:
        """
        Build the header of a sectioned sheet.


        :param rows: The rows of the sheet.


        :return: A sectioned sheet's header object.


        :raise Exception: If an unexpected condition occurs:

            - If no section is defined in the first column of the first row of the
              sheet.

            - If a field is not defined in the second row of the sheet.

            - If the name of a section is defined multiple times.

            - If the name of a field is defined multiple times for a same section.
        """
        # Read the primary row of the sheet.  Check that the first section
        # starts at the first column of the sheet.
        primary_header: list[str] = [section_name.strip() for section_name in rows[0]]
        if not primary_header[0]:
            raise ValueError("No section defined at column 1 / row 1 of the sheet")

        # Read the secondary row of the sheet.  Check that the first and the
        # second rows have the same number of columns.  Check that a field
        # name (row 2) is defined at the same column of its section (row 1).
        secondary_header: list[str] = [field_name.strip() for field_name in rows[1]]

        if len(primary_header) != len(secondary_header):
            raise ValueError("The first and second rows of the sheet have different length")

        for column_index in range(len(primary_header)):
            if primary_header[column_index] and not secondary_header[column_index]:
                raise ValueError(f"Missing field name at column {column_index + 1} / row 2 of the sheet")

        # Read the sections and their respective fields.
        sections: dict[str, HeaderSection] = {}
        previous_section_name: str | None = None
        section_field_names: dict[str, HeaderField] = {}

        for column_index, section_name in enumerate(primary_header):
            # If a new section is defined in the primary header, complete the
            # registration of the previous section.
            if section_name:
                # Check whether the name of this section is already in used.
                if section_name in sections:
                    raise Exception(f'The section "{section_name}" has been already defined')

                # Add the previous section in the list.
                if previous_section_name:
                    sections[previous_section_name] = HeaderSection(
                        previous_section_name,
                        column_index,
                        section_field_names  # This variable is not `None`
                    )

                # Start building the fields of this new section.
                previous_section_name = section_name
                section_field_names = dict[str, HeaderField]()

            # Add the field of the section.
            field_name: str = secondary_header[column_index]
            if not field_name:
                raise ValueError(f"The field at column {column_index + 1} / row 2 is not defined")

            if field_name in section_field_names:
                raise ValueError(
                    f'The field "{field_name}" located at column {column_index + 1} / row 2 '
                    f'has been already defined in the section "{section_name}"'
                )

            section_field_names[field_name] = HeaderField(field_name, column_index)

        # Add the last remaining section of the sheet.
        sections[previous_section_name] = HeaderSection(
            previous_section_name,
            column_index,
            section_field_names  # This variable is not `None`
        )

        return SectionedSheetHeader(sections)


class SectionedSheet:
    """
    Represent a sheet where the 2 first rows corresponds to the
    headers of this document.

    The first line of the header is composed of sections.  The second line
    of the header corresponds to the subsections:

    ```
    +===========+===========+===========+===========+===========+===...
    | Section 1 |           |           | Section 2 |           |
    +-----------+-----------+-----------+-----------+-----------+---...
    | Field 1.1 | Field 1.2 | Field 1.3 | Field 2.1 | Field 2.2 |
    +===========+===========+===========+===========+===========+===...
    |           |           |           |           |           |
    .           .           .           .           .           .
    """
    def __init__(self, rows: list[list[str]]):
        """
        Build a sectioned sheet from a reader object.


        :param rows: A reader object which will iterate over lines in a
            CSV file.
        """
        # Build the header of the sheet.
        self.__header = self._build_header(rows)

        # Read the data rows of the sheet.
        self.__data_rows: list[list[str]] = rows[2:]

    @classmethod
    def _build_header(cls, rows: list[list[str]]) -> SectionedSheetHeader:
        """
        Build the header of a sectioned sheet.


        :param rows: The rows of the sheet.


        :return: A sheet header object.
        """
        return SectionedSheetHeader.from_rows(rows)

    @staticmethod
    def __to_row_number(data_row_index: int) -> int:
        """
        Translate a data row number from the first row of the sheet,
        also known as the human-readable number of the row.

        Human-readable row number of a sheet starts with ``0``.  This
        number includes the 2 rows of the header (the sections of the CSV
        document and their respective fields).


        :param data_row_index: The index of the row starting at the first
            data row of the sheet.


        :return: The number of the row in the sheet.
        """
        return data_row_index + 1 + 2

    @property
    def data_row_count(self) -> int:
        """
        Return the number of rows of the sheet.


        :return: The total number of rows of the sheet, excluding the 2
            rows of the header.
        """
        return len(self.__data_rows)

    def get_field_value(
            self,
            data_row_index: int,
            section_name: str,
            field_name: str,
            is_required: bool = True
    ) -> str | None:
        """
        Return the value of a field (a cell) of the specified section of the
        sheet.


        :param data_row_index: The row index of the field to return its value.  A
            row index starts with ``0``.  The 2 rows of the sheet's
            header do not count.

        :param section_name: The name of the section that the field belongs to.

        :param field_name: The name of the field to return.

        :param is_required: Indicate whether this field MUST contain a value.


        :return: The value of the specified field.


        :raise EmptyFieldException: If the field is empty while a value is
            required.

        :raise FieldNotFoundException: if the field name does not exist for
            the specified section of the sheet.

        :raise IndexError: If the data row index is either negative or greater
            than or equal to the number of data rows of the sheet.

        :raise SectionNotFoundException: If the section name does not exist in
            the sheet.
        """
        if data_row_index < 0 or data_row_index >= len(self.__data_rows):
            raise IndexError(f"Row index {data_row_index} out of bound")

        section = self.__header.sections.get(section_name)
        if not section:
            raise SectionNotFoundException(section_name)

        field = section.fields.get(field_name)
        if not field:
            raise FieldNotFoundException(section_name, field_name)

        value = self.__data_rows[data_row_index][field.column_index].strip()

        if is_required and not value:
            raise EmptyFieldException(
                section_name,
                field,
                self.__to_row_number(data_row_index)
            )

        return value if value else None

    def get_row(self, data_row_number) -> list[any]:
        """
        Return the list of values of the specified row.


        :param data_row_number: The row number to return the list of values.


        :return: A list of values.
        """
        return self.__data_rows[data_row_number]
