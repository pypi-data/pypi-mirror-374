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

import csv
import json
import logging
import os
import re
from pathlib import Path
from typing import Callable
from typing import Any

import requests
from majormode.perseus.model.country import Country
from majormode.perseus.model.country import InvalidCountryCode
from majormode.perseus.model.date import ISO8601DateTime
from majormode.perseus.model.locale import Locale
from majormode.perseus.utils import cast
from majormode.perseus.utils import module_utils
from majormode.xebus.constant.family import FamilyPropertyName
from majormode.xebus.model.family import FamilyData
from majormode.xebus.sis.connector.constant.vendor import SisVendor
from majormode.xebus.sis.connector.sis_connector import SisConnector
from majormode.xebus.utils import normalization_utils
from majormode.xebus.utils import csv_utils

# The Eduka character used to separate each CSV field.
EDUKA_CSV_DELIMITER_CHARACTER = ';'

# The Eduka character used to escape the delimiter character, in case
# quotes aren't used.
EDUKA_CSV_ESCAPE_CHARACTER = None

# The Eduka character used to surround fields that contain the delimiter
# character.
EDUKA_CSV_QUOTE_CHARACTER = '"'

EDUKA_COUNTRY_CODE_PATCHES = {
    'UK': 'GB',
}

# The French locale used to load the default languages names and
# nationalities names mappings.
FRENCH_LOCALE = Locale('fra')

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


# Regular expression to match an Eduka error returned either by the URL
# to request generating a specific list (`Erreur n°XXXYYY`), either by
# the URL to fetch the content of this list (`Error #XXXYYY`).
#
# Eduka doesn't raise an HTTP error using a proper HTTP status code, but
# instead returns a HTTP status code `200`, and returned a HTTP content
# that includes a message containing a HTTP status code `XXX` combined
# with another code `YYY` specific to Eduak.
REGEX_PATTERN_EDUKA_ERROR_CODE = r'Err(eu|o)r (#|n°)(?P<http_status_code>\d{3})(?P<eduka_error_code>\d*)'
REGEX_EDUKA_ERROR_CODE = re.compile(REGEX_PATTERN_EDUKA_ERROR_CODE)


class EdukaError(Exception):
    """
    Represent an error that a school's Eduka system raises.
    """
    def __init__(
            self,
            http_status_code: int,
            eduka_error_code: int
    ):
        """
        Build a new ``EdukaError`` exception.


        :param http_status_code: The HTTP status code that a school's Eduka
            system returns.

        :param eduka_error_code: The specific error code that a school's Eduka
            system raises.
        """
        self.__http_status_code = http_status_code
        self.__eduka_error_code = eduka_error_code

    @property
    def eduka_error_code(self) -> int:
        """
        Return the specific error code that a school's Eduka system raises.


        :return: The specific error code that a school's Eduka system raises.
        """
        return self.__eduka_error_code

    @property
    def http_status_code(self) -> int:
        """
        Return the HTTP status code that a school's Eduka system returns.


        :return: The HTTP status code that a school's Eduka system returns.
        """
        return self.__http_status_code


class EdukaConnector(SisConnector):
    def __convert_field_class_name_value(self, value: str | None) -> str | None:
        """
        Return the Xebus class name corresponding to the given Eduka class
        name.


        :param value: The name of a class as defined in the Eduka system.


        :return: The name of the class as defined in the Xebus system.
        """
        if self.__eduka_class_names_mapping is None or not value:  # is None or empty
            if not value:
                logging.debug("The class name passed to the converter is undefined")
            return value

        key = normalization_utils.normalize_key(value)

        class_name = self.__eduka_class_names_mapping.get(key)
        if class_name is None:
            message = f"Invalid Eduka string representation \"{value}\" of a class name"
            logging.error(message)
            raise ValueError(message)

        return class_name

    def __convert_field_grade_name_value(self, value: str) -> int | None:
        """
        Return the level of an educational grade.


        :param value: The name of an education grade.


        :return: The corresponding level for this education grade.  It
            generally corresponds to the number of the year a pupil has
            reached in this given educational stage for this grade.
        """
        key = normalization_utils.normalize_key(value)

        grade_level = self.__eduka_grades_names_mapping.get(key)
        if grade_level is None:
            message = f"Invalid Eduka string representation \"{value}\" of a grade name"
            logging.error(message)
            return 0
            # raise ValueError(message)

        return grade_level

    def __convert_field_languages_value(self, value: str) -> list[Locale] | None:
        """
        Return the locale corresponding to the string representation of a
        language.


        :param value: A string representation of a language.


        :return: A locale.


        :raise ValueError: If the value is not a valid string representation
            of a language.
        """
        if value:
            locales = [
                self.__convert_language_value(language.strip())
                for language in value.split(',')
            ]
            return locales

    def __convert_field_nationalities_value(self, value: str) -> list[Country] | None:
        """
        Return the country corresponding to the string representation of a
        nationality.


        :param value: A string representation of a nationality.


        :return: A country.


        :raise ValueError: If the value is not a valid string representation
            of a nationality.
        """
        if value:
            countries = [
                self.__convert_nationality_value(nationality.strip())
                for nationality in value.split(',')
            ]
            return countries

    # Mapping between family properties and functions responsible for
    # converting their values from Eduka data.
    #
    # :note: The keys are not the Eduka property names (that can change
    #     from a school organization to another), but the Xebus property
    #     names (that never change).
    #
    # :note: The flag following the converter indicates whether any value
    #    format error should simply be ignored, and the value replaced with
    #    a null value, or whether an exception should be raised.
    #
    #    THIS DOES NOT INDICATE THAT THE VALUE MUST NOT BE NULL.  A
    #    converter is only responsible for converting text data into an
    #    appropriate format.
    EDUKA_PROPERTY_VALUE_CONVERTERS: dict[FamilyPropertyName, tuple[Callable[[Any, str], Any], bool]] = {
        FamilyPropertyName.child_class_name: (__convert_field_class_name_value, True),
        FamilyPropertyName.child_date_of_birth: (SisConnector._convert_field_date_value, True),
        FamilyPropertyName.child_grade_level: (__convert_field_grade_name_value, True),
        FamilyPropertyName.child_languages: (__convert_field_languages_value, False),
        FamilyPropertyName.child_nationalities: (__convert_field_nationalities_value, False),
        FamilyPropertyName.child_use_transport: (SisConnector._convert_field_boolean_value, True),
        FamilyPropertyName.primary_guardian_email_address: (SisConnector._convert_field_email_address_value, True),
        FamilyPropertyName.primary_guardian_languages: (__convert_field_languages_value, True),
        FamilyPropertyName.primary_guardian_nationalities: (__convert_field_nationalities_value, True),
        FamilyPropertyName.primary_guardian_phone_number: (SisConnector._convert_field_phone_number_value, False),
        FamilyPropertyName.secondary_guardian_email_address: (SisConnector._convert_field_email_address_value, True),
        FamilyPropertyName.secondary_guardian_languages: (__convert_field_languages_value, True),
        FamilyPropertyName.secondary_guardian_nationalities: (__convert_field_nationalities_value, True),
        FamilyPropertyName.secondary_guardian_phone_number: (SisConnector._convert_field_phone_number_value, False),
    }

    def __convert_eduka_rows(
            self,
            rows: list[str]
    ) -> list[dict[FamilyPropertyName, Any]]:
        """
        Convert rows of information about children and their parents extracted
        from a school's Eduka system to their standard representation in Xebus.


        :param rows: The rows of information about children and their parents
            extracted from a school's Eduka system.


        :return: A list of Python dictionaries.  Each dictionary represents
            the information about a child and their parents.  Each key of the
            dictionary corresponds to the name of a Family property, while the
            value corresponds to the information about a child or their parent
            represented with a Python datum.
        """
        csv_reader = csv.DictReader(
            rows,
            delimiter=EDUKA_CSV_DELIMITER_CHARACTER,
            escapechar=EDUKA_CSV_ESCAPE_CHARACTER,
            quotechar=EDUKA_CSV_QUOTE_CHARACTER
        )

        # The Eduka list may contain more properties that those required.  We
        # ignore them.
        ignored_eduka_property_names = []
        for eduka_property_name in csv_reader.fieldnames:
            key = normalization_utils.normalize_key(eduka_property_name)
            if key not in self.__eduka_properties_mapping:
                logging.debug(f'"Ignoring the Eduka property name "{eduka_property_name}"')
                ignored_eduka_property_names.append(key)

        # Check that all the required Eduka property names are not missing.
        normalized_eduka_property_names = [
            normalization_utils.normalize_key(field_name)
            for field_name in csv_reader.fieldnames
        ]

        for eduka_property_name in self.__eduka_properties_mapping:
            if eduka_property_name not in normalized_eduka_property_names:
                raise ValueError(f'The Eduka property name "{eduka_property_name}" is missing')

        # Translate the Eduka fields names and values in their corresponding
        # Xebus fields names and values.

        # :note: Type annotation to avoid the linter to complain that
        #     "Unresolved attribute reference 'items' for class 'str'" for the
        #     expression "eduka_row.items()".
        eduka_row: dict[str, Any]

        rows = []
        for eduka_row in csv_reader:
            xebus_properties = {}
            for eduka_property_name, eduka_property_value in eduka_row.items():
                key = normalization_utils.normalize_key(eduka_property_name)
                if key not in ignored_eduka_property_names:
                    xebus_property_name = self.__eduka_properties_mapping[key]
                    eduka_property_value_converter = self.EDUKA_PROPERTY_VALUE_CONVERTERS.get(xebus_property_name)

                    if eduka_property_value_converter is not None:
                        eduka_property_value_converter_function, is_eduka_property_required = eduka_property_value_converter
                        try:
                            eduka_property_value = eduka_property_value_converter_function(self, eduka_property_value)
                        except ValueError as error:
                            # If the Eduka property's value is of the wrong format, while this
                            # property is not required, we ignore its value, replacing it with a
                            # null value.
                            if is_eduka_property_required:
                                raise error

                            logging.error(error)
                            eduka_property_value = None

                    xebus_properties[xebus_property_name] = eduka_property_value

            rows.append(xebus_properties)

        return rows

    def __convert_language_value(self, value: str) -> Locale:
        """
        Return the locale corresponding to the string representation of a
        language.


        :param value: A string representation of a language.


        :return: A locale.


        :raise ValueError: If the Eduka value is not a valid string
            representation of a language.
        """
        key = normalization_utils.normalize_key(value)

        try:
            locale = cast.string_to_locale(key)
        except Locale.MalformedLocaleException as error:
            locale = (
                self.__eduka_languages_names_mapping
                and cast.string_to_locale(self.__eduka_languages_names_mapping.get(key))
            )
            if not locale:
                logging.error(f"Invalid Eduka string representation \"{value}\" of a language")
                raise ValueError(str(error))

        return locale

    def __convert_nationality_value(self, value: str) -> Country:
        """
        Return the country corresponding to the string representation of a
        nationality.


        :param value: A string representation of a nationality.


        :return: A country.


        :raise ValueError: If the Eduka value is not a valid string
            representation of a nationality.
        """
        key = normalization_utils.normalize_key(value)

        try:
            country_code = self.__patch_eduka_country_code(key)  # Some Eduka country codes are invalid (cf. `UK`)
            country = Country.from_string(country_code)
        except InvalidCountryCode as error:
            country = (
                self.__eduka_nationalities_names_mapping
                and Country.from_string(self.__eduka_nationalities_names_mapping.get(key))
            )
            if not country:
                logging.error(f"Invalid Eduka string representation \"{value}\" of a nationality")
                raise ValueError(str(error))

        return country

    @staticmethod
    def __fetch_eduka_list_data(
            list_url: str
    ) -> list[str]:
        """
        Fetch and return the school's family data.


        :param list_url: The school's Eduka list containing the family data to
            synchronize.


        :return: A list of CSV rows corresponding to information about
            children and their guardianships.


        :raise ValueError: If the HTTP request to fetch the family data from
            the school's Eduka information system failed, or if some Eduka
            fields are missing.
        """
        response = requests.get(list_url)
        if response.status_code != 200:
            error_message = f'The HTTP request "{list_url}" failed with status code {response.status_code}'
            logging.error(error_message)
            raise ValueError(error_message)

        data = response.text
        match = REGEX_EDUKA_ERROR_CODE.search(data)
        if match:
            http_status_code = match.group('http_status_code')
            eduka_error_code = match.group('eduka_error_code')
            raise EdukaError(int(http_status_code), int(eduka_error_code))

        rows = data.splitlines()

        return rows

    @staticmethod
    def __fetch_eduka_list_url(
            eduka_school_hostname: str,
            api_key: str,
            list_id: int,
    ) -> str:
        """
        Request the generation of a predefined list, generated by the school
        organization, corresponding to the family data and return the URL of
        the generated list.

        The school organization is responsible for creating a predefined list
        corresponding to the family data with all the required fields for the
        children and the primary and secondary parents of these children.

        The function requests the Eduka school information system to generate
        the data in CSV (Comma-Separated Values) format, with the semicolon
        character as a delimiter.

        The generated list is only valid for a limited period of time, after
        which the list is no longer available for download.


        :param eduka_school_hostname: The hostname of the school's Eduka.

        :param api_key: The API key that allows to access the predefined list
            corresponding to the school's family data.

        :param list_id: The identifier of the predefined list corresponding to
             the school's family data.


        :return: The Uniform Resource Locator (URL) of the generated list
            corresponding to the school's family data.  This URL is only valid
            for a limited period of time.


        :raise UnauthorizedAccess: If the access to the predefined list is not
            authorized.  This could happen when the IP address of the machine
            that requests the predefined list has not been authorized to
            access the school's Eduka platform.
        """
        response = requests.get(
            f'https://{eduka_school_hostname}/api.php',
            params={
                'A': 'GENLIST',
                'FORMAT': 'csvs',
                'K': api_key,
                'LIST': list_id
            }
        )

        if response.status_code == 200:
            data = response.text
            # data = '{"confirm":"OK","url":"https:\/\/lpehcm.eduka.school\/download\/ticket\/265\/8ybdx3pummon0yx7ngsulta84ymciq"}'

            try:
                payload = json.loads(data)
                return payload['url']

            except json.decoder.JSONDecodeError:
                match = REGEX_EDUKA_ERROR_CODE.search(data)
                if match:
                    http_status_code = match.group('http_status_code')
                    eduka_error_code = match.group('eduka_error_code')
                    raise EdukaError(int(http_status_code), int(eduka_error_code))

                else:
                    print(data)
        else:
            print("Request failed with status code:", response.status_code)

    def __init__(
            self,
            eduka_hostname: str,
            eduka_api_key: str,
            eduka_list_id: int,
            eduka_properties_mapping: dict[str, FamilyPropertyName],
            eduka_grades_names_mapping: dict[str, int],
            eduka_class_names_mapping: dict[str, str] = None,
            eduka_languages_names_mapping: dict[str, Locale] = None,
            eduka_nationalities_names_mapping: dict[str, Country] = None
    ):
        """
        Build an ``EdukaConnector`` object.


        :param eduka_hostname: The hostname of the Eduka server of a school.

        :param eduka_api_key: The Eduka API key to use to access the families
            list.

        :param eduka_list_id: The list ID that the school has created and
            shared.

        :param eduka_properties_mapping: The mapping between the Eduka
            property names (the keys) and the Xebus property names (the
            values), containing information about children and their guardians.

        :param eduka_grades_names_mapping: The mapping between the names of
            the educational grade name (the keys) declared in Eduka and their
            corresponding grade levels (the values).

        :param eduka_class_names_mapping: The mapping between names of classes
            as defined in the Eduka system and their corresponding names as
            defined in the Xebus systems.  (THIS IS A PATCH TO BE REMOVED).

        :param eduka_languages_names_mapping: The mapping between names of
            languages (the keys) used in Eduka and their corresponding
            ISO 639-3:2007 codes (the values).

            If this argument is not passed, the function loads the default French
            languages names mapping defined in the library.

        :param eduka_nationalities_names_mapping: The mapping between names of
            nationalities names (the keys) used in Eduka and their
            corresponding ISO 3166-1 alpha-2 codes (the values).

            If this argument is not passed, the function loads the default French
            nationalities names mapping defined in the library.
        """
        super().__init__(SisVendor.eduka)

        self.__eduka_hostname = eduka_hostname
        self.__eduka_api_key = eduka_api_key
        self.__eduka_list_id = eduka_list_id

        # Check that the Xebus property names are items of the enumeration
        # ``FamilyPropertyName`` (and not the type ``str``).
        assert not any([
            v
            for k, v in eduka_properties_mapping.items()
            if v not in FamilyPropertyName
        ]), "Eduka properties mapping has Xebus properties defined with wrong type"

        # Normalize the Eduka properties names. The mapping between Eduka
        # property names and Xebus property names is manually defined by the
        # school organization, and therefore the writing of accents, capital
        # letters, special characters, can be prone to errors.
        self.__eduka_properties_mapping = normalization_utils.normalize_names_codes_mapping(eduka_properties_mapping)

        self.__eduka_grades_names_mapping = normalization_utils.normalize_names_codes_mapping(eduka_grades_names_mapping)
        logging.debug("Eduka Grade Names Mapping:")
        logging.debug(self.__eduka_grades_names_mapping)

        self.__eduka_class_names_mapping = (
            eduka_class_names_mapping
            and normalization_utils.normalize_names_codes_mapping(eduka_class_names_mapping)
        )

        self.__eduka_languages_names_mapping = normalization_utils.normalize_names_codes_mapping(
            eduka_languages_names_mapping
            or self.__load_eduka_languages_names_mapping_from_default_csv_file(FRENCH_LOCALE)
        )

        self.__eduka_nationalities_names_mapping = normalization_utils.normalize_names_codes_mapping(
            eduka_nationalities_names_mapping
            or self.__load_eduka_nationalities_names_mapping_from_default_csv_file(FRENCH_LOCALE)
        )

    @staticmethod
    def __load_eduka_languages_names_mapping_from_default_csv_file(locale: Locale = None) -> dict[str, Locale]:
        """
        Return the mapping between the names of languages and their respective
        ISO 639-3:2007 codes as identified in the default Eduka languages
        file.


        :note: We assume that the list of language names is the same for all
            instances of the Eduka platform used by school organizations.
            Therefore, we put its definition and loading in this library.  We
            may be wrong.


        :param locale: The language to return the names of the languages in.


        :return: A dictionary representing a mapping between the names of
            languages (the keys), localized in the specified language, and
            their corresponding ISO 639-3:2007 codes (the values).
        """
        default_file_path_name = Path(LIBRARY_DATA_PATH, f'languages_names.{locale}.csv')
        return csv_utils.load_languages_names_iso_codes_mapping_from_csv_file(default_file_path_name)

    @staticmethod
    def __load_eduka_nationalities_names_mapping_from_default_csv_file(locale: Locale = None) -> dict[str, Country]:
        """
        Return the mapping between the names of nationalities and their
        respective ISO 3166-1 alpha-2 codes as identified in the default Eduka
        nationalities file.


        :note: We assume that the list of nationality names is the same for
            all instances of the Eduka platform used by school organizations.
            Therefore, we put its definition and loading in this library.  We
            may be wrong.


        :param locale: The language to return the names of the nationalities
            in.


        :return: A dictionary representing a mapping between the names of
            nationalities (the keys), localized in the specified langauge, and
            their corresponding ISO 3166-1 alpha-2 codes (the values).
        """
        default_file_path_name = Path(LIBRARY_DATA_PATH, f'nationalities_names.{locale}.csv')
        return csv_utils.load_nationalities_names_iso_codes_mapping_from_csv_file(default_file_path_name)

    @staticmethod
    def __patch_eduka_country_code(code: str) -> str:
        uppercase_code = code.upper()
        return EDUKA_COUNTRY_CODE_PATCHES.get(uppercase_code) or uppercase_code

    def fetch_family_data(self) -> FamilyData:
        """
        Returns the data of the families to synchronize.


        :return: The data of the families to synchronize.
        """
        logging.debug(
            f"Fetching families data from the Eduka platform \"{self.__eduka_hostname}\"..."
        )

        # Fetch the URL of the Eduka list containing the families data to
        # synchronize.
        eduka_list_url = self.__fetch_eduka_list_url(
            self.__eduka_hostname,
            self.__eduka_api_key,
            self.__eduka_list_id
        )

        # Fetch the families data from the list URL.
        eduka_rows = self.__fetch_eduka_list_data(eduka_list_url)

        # Convert the Eduka CSV families list into a Xebus data structure.
        xebus_rows = self.__convert_eduka_rows(eduka_rows)

        # Remove guardians who are not declared with an email address.
        xebus_rows = self._cleanse_rows(xebus_rows)

        # Build the families entities.
        family_list = FamilyData(xebus_rows)

        # for child in family_list.children:
        #     logging.debug(f"- {child.full_name}: {child.grade_level}")

        return family_list

    def fetch_update_time(self) -> ISO8601DateTime | None:
        """
        Return the time of the most recent update of the family list.

        :note: The Eduka platform doesn't support this feature.


        :return: ``None``.
        """
        return None
