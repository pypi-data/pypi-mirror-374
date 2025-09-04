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

from majormode.xebus.constant.family import FamilyPropertyName


# The default name of the sheet in a school organization's Google
# Sheets containing the list of children and their guardian.
DEFAULT_FAMILIES_SHEET_NAME = 'Families'

# The default name of the sheet in a organization's Google Sheets
# containing the list of the country names and their respective
# ISO 3166-1 alpha-2 codes.
DEFAULT_COUNTRIES_NAMES_MAPPING_SHEET_NAME = '(Countries)'

# The default name of the sheet in a organization's Google Sheets
# containing the list of the educational grade names and their
# respective levels.
DEFAULT_GRADES_NAMES_MAPPING_SHEET_NAME = '(Education Grades)'

# The default name of the sheet in an organization's Google Sheets
# containing the list of the language names and their respective
# 639-3:2007 codes.
DEFAULT_LANGUAGES_NAMES_MAPPING_SHEET_NAME = '(Languages)'

# The default column names of the primary header (sections) of the sheet
# containing family data.
DEFAULT_SECTION_NAME_CHILD = 'Child'
DEFAULT_SECTION_NAME_PRIMARY_PARENT = 'Parent 1'
DEFAULT_SECTION_NAME_SECONDARY_PARENT = 'Parent 2'

# The default column names of the secondary header (fields) of the sheet
# containing family data.
DEFAULT_FIELD_NAME_IS_CHILD_REMOVED = '🗑'
DEFAULT_FIELD_NAME_ACCOUNT_SIS_ID = 'SIS ID'
DEFAULT_FIELD_NAME_DOB = "Date of Birth"
DEFAULT_FIELD_NAME_EMAIL_ADDRESS = 'Email Address'
DEFAULT_FIELD_NAME_FIRST_NAME = 'First Name'
DEFAULT_FIELD_NAME_FULL_NAME = 'Full Name'
DEFAULT_FIELD_NAME_GRADE_NAME = 'Grade Name'
DEFAULT_FIELD_NAME_CLASS_NAME = 'Class Name'
DEFAULT_FIELD_NAME_HOME_ADDRESS = 'Home Address'
DEFAULT_FIELD_NAME_LANGUAGE = 'Language'
DEFAULT_FIELD_NAME_LAST_NAME = 'Last Name'
DEFAULT_FIELD_NAME_NATIONALITY = 'Nationality'
DEFAULT_FIELD_NAME_PHONE_NUMBER = 'Phone Number'
DEFAULT_FIELD_NAME_USE_TRANSPORT = 'Transport?'

# The mapping between the default field names of a sectioned sheet
# (e.g., Google Sheet, CSV file) containing family data and Xebus
# property names.
DEFAULT_SHEET_FIELD_NAMES_FAMILY_PROPERTY_NAMES_MAPPING = {
    DEFAULT_SECTION_NAME_CHILD: {
        DEFAULT_FIELD_NAME_ACCOUNT_SIS_ID: FamilyPropertyName.child_sis_id,
        DEFAULT_FIELD_NAME_CLASS_NAME: FamilyPropertyName.child_class_name,
        DEFAULT_FIELD_NAME_DOB: FamilyPropertyName.child_date_of_birth,
        DEFAULT_FIELD_NAME_FIRST_NAME: FamilyPropertyName.child_first_name,
        DEFAULT_FIELD_NAME_FULL_NAME: FamilyPropertyName.child_full_name,
        DEFAULT_FIELD_NAME_GRADE_NAME: FamilyPropertyName.child_grade_level,
        DEFAULT_FIELD_NAME_LANGUAGE: FamilyPropertyName.child_languages,
        DEFAULT_FIELD_NAME_LAST_NAME: FamilyPropertyName.child_last_name,
        DEFAULT_FIELD_NAME_NATIONALITY: FamilyPropertyName.child_nationalities,
        DEFAULT_FIELD_NAME_USE_TRANSPORT: FamilyPropertyName.child_use_transport
    },
    DEFAULT_SECTION_NAME_PRIMARY_PARENT: {
        DEFAULT_FIELD_NAME_ACCOUNT_SIS_ID: FamilyPropertyName.primary_guardian_sis_id,
        DEFAULT_FIELD_NAME_EMAIL_ADDRESS: FamilyPropertyName.primary_guardian_email_address,
        DEFAULT_FIELD_NAME_FIRST_NAME: FamilyPropertyName.primary_guardian_first_name,
        DEFAULT_FIELD_NAME_FULL_NAME: FamilyPropertyName.primary_guardian_full_name,
        DEFAULT_FIELD_NAME_HOME_ADDRESS: FamilyPropertyName.primary_guardian_home_address,
        DEFAULT_FIELD_NAME_LANGUAGE: FamilyPropertyName.primary_guardian_languages,
        DEFAULT_FIELD_NAME_LAST_NAME: FamilyPropertyName.primary_guardian_last_name,
        DEFAULT_FIELD_NAME_NATIONALITY: FamilyPropertyName.primary_guardian_nationalities,
        DEFAULT_FIELD_NAME_PHONE_NUMBER: FamilyPropertyName.primary_guardian_phone_number,
    },
    DEFAULT_SECTION_NAME_SECONDARY_PARENT: {
        DEFAULT_FIELD_NAME_ACCOUNT_SIS_ID: FamilyPropertyName.secondary_guardian_sis_id,
        DEFAULT_FIELD_NAME_EMAIL_ADDRESS: FamilyPropertyName.secondary_guardian_email_address,
        DEFAULT_FIELD_NAME_FIRST_NAME: FamilyPropertyName.secondary_guardian_first_name,
        DEFAULT_FIELD_NAME_FULL_NAME: FamilyPropertyName.secondary_guardian_full_name,
        DEFAULT_FIELD_NAME_HOME_ADDRESS: FamilyPropertyName.secondary_guardian_home_address,
        DEFAULT_FIELD_NAME_LANGUAGE: FamilyPropertyName.secondary_guardian_languages,
        DEFAULT_FIELD_NAME_LAST_NAME: FamilyPropertyName.secondary_guardian_last_name,
        DEFAULT_FIELD_NAME_NATIONALITY: FamilyPropertyName.secondary_guardian_nationalities,
        DEFAULT_FIELD_NAME_PHONE_NUMBER: FamilyPropertyName.secondary_guardian_phone_number,
    }
}
