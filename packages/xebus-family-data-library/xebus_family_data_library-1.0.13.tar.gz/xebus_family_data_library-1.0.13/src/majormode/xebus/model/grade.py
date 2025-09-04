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


class EducationGrade:
    """
    Represent an education grade of a school.

    Countries generally divide education stages into education grades for
    pupils in the same year.  Some schools may have used their own
    education grades.
    """
    def __init__(
            self,
            grade_level: int,
            grade_name: str,
            start_age: int,
            end_age: int,
            grade_short_name: str = None,
    ):
        """
        Build an object representing an education grade.


        :param grade_level: The number of the year that pupils have spent in
            the school’s education level to reach this grade level. Starts
            from ``0``.

        :param grade_name: The name given to this grade level. For instance,
            "Terminale".

        :param start_age: The age at which pupils usually start this grade
            level.

        :param end_age: The age at which pupils usually complete this grade
            level.

        :param grade_short_name: The short name given to this grade level. For
            instance, "Tle".
        """
        self.__grade_level = grade_level
        self.__grade_name = grade_name
        self.__grade_short_name = grade_short_name
        self.__start_age = start_age
        self.__end_age = end_age

    @property
    def end_age(self) -> int:
        """
        Return the age at which pupils usually complete this grade level.


        :return: The age at which pupils usually complete this grade level.
        """
        return self.__end_age

    @property
    def grade_level(self) -> int:
        """
        Return the number of the year that pupils have spent in the school’s
        education level to reach this grade level. Starts from ``0``.

        :return: The number of the year that pupils have spent in the school’s
            education level to reach this grade level.
        """
        return self.__grade_level

    @property
    def grade_name(self) -> str:
        """
        Return the name given to this grade level.


        :return: The name given to this grade level.
        """
        return self.__grade_name

    @property
    def grade_short_name(self) -> str | None:
        """
        Return the short name given to this grade level.


        :return" The short name given to this grade level.
        """
        return self.__grade_short_name

    @property
    def start_age(self) -> int:
        """
        Return he age at which pupils usually start this grade level.


        :return: The age at which pupils usually start this grade level.
        """
        return self.__start_age
