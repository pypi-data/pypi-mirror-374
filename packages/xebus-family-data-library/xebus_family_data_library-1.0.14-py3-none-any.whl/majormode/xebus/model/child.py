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

import datetime
from uuid import UUID

from majormode.perseus.model.country import Country
from majormode.perseus.model.locale import Locale

from majormode.xebus.model.guardian import Guardian, Guardianship
from majormode.xebus.model.person import Person


class DuplicatedGuardianshipException(Exception):
    """
    Indicate that a guardian has been referenced twice for a child.
    """
    def __init__(self, child: Child, guardian: Guardian):
        """
        Build a new instance of the exception ``DuplicatedGuardianshipException``.


        :param child: a child.

        :param guardian: The guardian who has been referenced twice for this
            child.
        """
        super().__init__(
            f"The parent \"{guardian.sis_account_id}\" is already a guardian of the "
            f"child \"{child.sis_account_id}\""
        )
        self.__child = child
        self.__guardian = guardian

    @property
    def child(self) -> Child:
        """
        Return the child whose guardian was referenced twice.


        :return: The child whose guardian was referenced twice.
        """
        return self.__child

    @property
    def guardian(self) -> Guardian:
        """
        Return the guardian who has been referenced twice for the child.


        :return: The guardian who has been referenced twice for the child.
        """
        return self.__guardian


class Child(Person):
    """
    Represent a child enrolled to a school.
    """
    def __init__(
            self,
            sis_account_id: str,
            first_name: str,
            last_name: str,
            full_name: str,
            dob: datetime.datetime,
            grade_level: int,
            account_id: UUID = None,
            class_name: str = None,
            languages: list[Locale] = None,
            nationalities: list[Country] = None,
            use_transport: bool = False
    ):
        """
        Build a new object representing a child.


        :param sis_account_id: The identifier of the child registered in the
            school information system (SIS) of the organization.

        :param first_name: The forename of the child.

        :param last_name: The surname of the child.

        :param full_name: The complete personal name by which child is known,
            including their surname, forename and middle name(s), in the
            correct lexical name order depending on the culture of the child.

        :param dob: The date of birth of the child.

        :param grade_level: The education grade level that the child has
            reached for the current or the coming school year.  It generally
            corresponds to the number of the year a pupil has reached in this
            given educational stage for this grade.

        :param class_name: The name of the child's class.

        :param account_id: The identifier of the child's account registered in
            the service database.

        :param languages: The spoken languages of the child.

        :param nationalities: The countries the child's citizenship belong to.

        :param use_transport: Indicate whether the child uses a transport
            service to go to their school.
        """
        super().__init__(
            sis_account_id,
            first_name,
            last_name,
            full_name,
            account_id=account_id,
            languages=languages,
            nationalities=nationalities
        )

        self._dob = dob
        self._grade_level = grade_level
        self._class_name = class_name
        self._use_transport = use_transport

        self._guardianships: list[Guardianship] = []

    def add_guardianship(self, guardianship: Guardianship) -> None:
        """
        Add a parent of the child.


        :param guardianship: The relationship between a guardian and the child.


        :raise DuplicatedGuardianException:
        """
        for existing_guardianship in self._guardianships:
            if guardianship.guardian.account_id is not None \
               and existing_guardianship.guardian.account_id is not None:
                # If the cloud identifiers of the two people are defined, check that
                # they refer to two different people.
                if guardianship.guardian.account_id == existing_guardianship.guardian.account_id:
                    raise DuplicatedGuardianshipException(self, guardianship.guardian)

            elif guardianship.guardian.sis_account_id == existing_guardianship.guardian.sis_account_id:
                # If the cloud identifiers of the two people are not defined (meaning
                # that the families information has been read from a School Information
                # System only), check that their SIS IDs refer to two different people.
                raise DuplicatedGuardianshipException(self, guardianship.guardian)

        self._guardianships.append(guardianship)

    @property
    def class_name(self) -> str:
        """
        Return the name of the child's class.


        :return: The child's class name.
        """
        return self._class_name

    @property
    def dob(self) -> datetime.datetime:
        """
        Return the child's date of birth.


        :return: The child's date of birth.
        """
        return self._dob

    @property
    def grade_level(self) -> int | None:
        """
        Return the level of the education grade that the child has reached for
        the current or the coming school year.


        :return: The level of the child's education grade.
        """
        return self._grade_level

    @property
    def guardianships(self) -> list[Guardianship]:
        """
        Return the list of the child's parents.


        :return: The list of the child's parents.
        """
        return self._guardianships

    @property
    def use_transport(self) -> bool:
        """
        Indicate whether the child uses a transport service to go to the school.


        :return: ``True`` if the child uses a transport service to go to the
            school; ``False`` if they don't.
        """
        return self._use_transport
