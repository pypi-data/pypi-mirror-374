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

from uuid import UUID
from majormode.perseus.model.date import ISO8601DateTime


class SchoolClass:
    def __init__(
            self,
            class_id: UUID,
            class_name: str,
            grade_level_min: int,
            grade_level_max: int,
            start_date: ISO8601DateTime,
            end_date: ISO8601DateTime
    ):
        self.__class_id = class_id
        self.__class_name = class_name
        self.__grade_level_min = grade_level_min
        self.__grade_level_max = grade_level_max
        self.__start_date = start_date
        self.__end_date = end_date

    @property
    def class_id(self) -> UUID:
        return self.__class_id

    @property
    def class_name(self) -> str:
        return self.__class_name

    @property
    def end_date(self) -> ISO8601DateTime:
        return self.__end_date

    @property
    def grade_level_max(self) -> int:
        return self.__grade_level_max

    @property
    def grade_level_min(self) -> int:
        return self.__grade_level_min

    @property
    def start_date(self) -> ISO8601DateTime:
        return self.__start_date

