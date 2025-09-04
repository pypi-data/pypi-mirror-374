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

from typing import Any

import unidecode


def normalize_names_codes_mapping(names_codes_mapping: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize the keys of a names codes mapping.

    Key normalization makes it possible to support minor differences
    (basically lowercase or uppercase letters, and accents) of names
    when searching for the corresponding code.


    :param names_codes_mapping: A mapping between names (the keys) and
        their respective codes (the values), such as, for example,
        language names and their ISO codes.


    :return: The names codes mapping where the names have been
        transliterated to ASCII lower cased strings.
    """
    normalized_names_codes_mapping = {
        normalize_key(key): value
        for key, value in names_codes_mapping.items()
    }

    return normalized_names_codes_mapping


def normalize_key(s: str) -> str:
    """
    Normalize the keys of a names codes mapping.


    :param s: A string to normalize.


    :return: The transliterated to ASCII lower cased string of the key
    """
    normalized_string = unidecode.unidecode(s.lower())
    return normalized_string
