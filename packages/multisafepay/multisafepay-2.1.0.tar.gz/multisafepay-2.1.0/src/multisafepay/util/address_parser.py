# Copyright (c) MultiSafepay, Inc. All rights reserved.

# This file is licensed under the Open Software License (OSL) version 3.0.
# For a copy of the license, see the LICENSE.txt file in the project root.

# See the DISCLAIMER.md file for disclaimer details.

import re
from typing import List


class AddressParser:
    """
    Class AddressParser.

    Parses and splits up an address in street and house number
    """

    def parse(
        self: "AddressParser",
        address1: str,
        address2: str = "",
    ) -> List[str]:
        """
        Parses and splits up an address in street and house number.

        Args:
        ----
            address1 (str): Primary address line
            address2 (str): Secondary address line (optional)

        Returns:
        -------
            List[str]: [street, house_number] where street is the street name
                      and house_number is the house number with any extensions

        """
        # Remove whitespaces from the beginning and end
        full_address = f"{address1} {address2}".strip()

        # Turn multiple whitespaces into one single whitespace
        full_address = re.sub(r"\s+", " ", full_address)

        # Split the address into 3 groups: street, apartment and extension
        pattern = r"(.+?)\s?([\d]+[\S]*)((\s?[A-z])*?)$"
        matches = re.match(pattern, full_address)

        if not matches:
            return [full_address, ""]

        return self.extract_street_and_apartment(
            matches.group(1) or "",
            matches.group(2) or "",
            matches.group(3) or "",
        )

    def extract_street_and_apartment(
        self: "AddressParser",
        group1: str,
        group2: str,
        group3: str,
    ) -> List[str]:
        """
        Extract the street and apartment from the matched RegEx results.

        When the address starts with a number, it is most likely that group1 and group2 are the house number and
        extension. We therefore check if group1 and group2 are numeric, if so, we can assume that group3
        will be the street and return group1 and group2 together as the apartment.
        If group1 or group2 contains more than just numbers, we can assume group1 is the street and group2 and
        group3 are the house number and extension. We therefore return group1 as the street and return group2 and
        group3 together as the apartment.

        Args:
        ----
            group1 (str): First captured group from regex
            group2 (str): Second captured group from regex
            group3 (str): Third captured group from regex

        Returns:
        -------
            List[str]: [street, apartment] where street is the street name
                      and apartment is the house number with extensions

        """
        if group1.isdigit() and group2.isdigit():
            return [group3.strip(), f"{group1}{group2}".strip()]

        return [group1.strip(), f"{group2}{group3}".strip()]
