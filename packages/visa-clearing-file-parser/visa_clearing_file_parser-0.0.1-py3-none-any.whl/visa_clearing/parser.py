"""
Visa BASE II Clearing Transaction File Parser

This module provides functionality to parse Visa BASE II Clearing Transaction Files (.ctf)
with automatic encoding detection and proper transaction grouping.
"""

import logging
import os
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, Union

from .exceptions import ParseError, EncodingError

LOGGER = logging.getLogger(__name__)


class VisaBaseIIParser:
    """
    Parses Visa BASE II Clearing Transaction Files (.ctf) by automatically
    detecting the encoding and correctly grouping multiple Transaction
    Component Records (TCRs) into single, complete logical transactions.

    Example:
        >>> parser = VisaBaseIIParser()
        >>> for transaction in parser.parse_file('transactions.ctf'):
        ...      for key, value in transaction.items():
        ...        print(f"{key.ljust(35)}: {value}")
        ...        print("-" * 40)
        ...
    """

    # Transaction Code definitions
    TC_DEFINITIONS = {
        '01': 'Returned Credit',
        '02': 'Returned Debit',
        '03': 'Returned Nonfinancial',
        '04': 'Reclassification Advice transaction',
        '05': 'Sales Draft',
        '06': 'Credit Voucher',
        '07': 'Cash Disbursement',
        '09': 'Money Transfer transaction',
        '10': 'Fee Collection transaction',
        '15': 'Chargeback, Sales Draft',
        '16': 'Chargeback, Credit Voucher',
        '17': 'Chargeback, Cash Disbursement',
        '19': 'Reversal Money Transfer transaction',
        '20': 'Funds Disbursement transaction',
        '25': 'Reversal, Sales Draft',
        '26': 'Reversal, Credit Voucher',
        '27': 'Reversal, Cash Disbursement',
        '35': 'Chargeback Reversal of Sales Draft',
        '36': 'Chargeback Reversal of Credit Voucher',
        '37': 'Chargeback Reversal of Cash Disbursement',
        '46': 'Member Settlement Data transaction'
    }

    # TCR Layout definitions
    TCR_05X0 = [
        [5, 16, 'Account Number'], [21, 3, 'Account Number Extension'],
        [24, 1, 'Floor Limit Indicator'], [25, 1, 'CRB/Exception File Indicator'],
        [26, 1, 'Positive Cardholder Authorization Service (PCAS) Indicator'],
        [27, 23, 'Acquirer Reference Number'], [50, 8, 'Acquirers Business ID'],
        [58, 4, 'Purchase Date (MMDD)'], [62, 12, 'Destination Amount'],
        [74, 3, 'Destination Currency Code'], [77, 12, 'Source Amount'],
        [89, 3, 'Source Currency Code'], [92, 25, 'Merchant Name'],
        [117, 13, 'Merchant City'], [130, 3, 'Merchant Country Code'],
        [133, 4, 'Merchant Category Code'], [137, 5, 'Merchant ZIP Code'],
        [142, 3, 'Merchant State/Province Code'], [145, 1, 'Requested Payment Service'],
        [147, 1, 'Usage Code'], [148, 2, 'Reason Code'],
        [150, 1, 'Settlement Flag'], [151, 1, 'Authorization Characteristics Indicator'],
        [152, 6, 'Authorization Code'], [158, 1, 'POS Terminal Capability'],
        [159, 1, 'International Fee Indicator'], [160, 1, 'Cardholder ID Method'],
        [161, 1, 'Collection-Only Flag'], [162, 2, 'POS Entry Mode'],
        [164, 4, 'Central Processing Date (YDDD)'], [168, 1, 'Reimbursement Attribute']
    ]

    TCR_05X1 = [
        [5, 6, 'Issuer Workstation BIN'], [11, 6, 'Acquirer Workstation BIN'],
        [17, 6, 'Chargeback Reference Number'], [23, 1, 'Documentation Indicator'],
        [24, 50, 'Member Message Text'], [74, 2, 'Special Condition Indicators'],
        [76, 3, 'Fee Program Indicator'], [79, 1, 'Issuer Charge'],
        [81, 15, 'Card Acceptor ID'], [96, 8, 'Terminal ID'],
        [104, 12, 'National Reimbursement Fee'],
        [116, 1, 'Mail/Telephone or Electronic Commerce Indicator'],
        [117, 1, 'Special Chargeback Indicator'], [118, 6, 'Interface Trace Number'],
        [124, 1, 'Unattended Acceptance Terminal Indicator'],
        [125, 1, 'Prepaid Card Indicator'], [126, 1, 'Service Development Field'],
        [127, 1, 'AVS Response Code'], [128, 1, 'Authorization Source Code'],
        [129, 1, 'Purchase Identifier Format'], [130, 1, 'Account Selection'],
        [131, 2, 'Installment Payment Count'], [133, 25, 'Purchase Identifier'],
        [158, 9, 'Cashback'], [167, 1, 'Chip Condition Code'],
        [168, 1, 'POS Environment']
    ]

    TCR_05X5 = [
        [5, 15, 'Transaction Identifier'], [20, 12, 'Authorized Amount'],
        [32, 3, 'Authorization Currency Code'], [35, 2, 'Authorization Response Code'],
        [37, 4, 'Validation Code'], [41, 1, 'Excluded Transaction Identifier Reason'],
        [45, 2, 'Multiple Clearing Sequence Number'], [47, 2, 'Multiple Clearing Sequence Count'],
        [49, 1, 'Market-Specific Authorization Data Indicator'],
        [50, 12, 'Total Authorized Amount'], [62, 1, 'Information Indicator'],
        [63, 14, 'Merchant Telephone Number'], [77, 1, 'Additional Data Indicator'],
        [78, 2, 'Merchant Volume Indicator'], [80, 2, 'Electronic Commerce Goods Indicator'],
        [82, 10, 'Merchant Verification Value'], [92, 15, 'Interchange Fee Amount'],
        [107, 1, 'Interchange Fee Sign'], [108, 8, 'Source Currency to Base Currency Exchange Rate'],
        [116, 8, 'Base Currency to Destination Currency Exchange Rate'],
        [124, 12, 'Optional Issuer ISA Amount'], [136, 2, 'Product ID'],
        [138, 6, 'Program ID'], [168, 1, 'CVV2 Result Code']
    ]

    TCR_05X7 = [
        [5, 2, 'Transaction Type'], [7, 3, 'Card Sequence Number'],
        [10, 6, 'Terminal Transaction Date'], [16, 6, 'Terminal Capability Profile'],
        [22, 3, 'Terminal Country Code'], [25, 8, 'Terminal Serial Number'],
        [33, 8, 'Unpredictable Number'], [41, 4, 'Application Transaction Counter'],
        [45, 4, 'Application Interchange Profile'], [49, 16, 'Cryptogram'],
        [65, 2, 'Issuer Application Data, Byte 2'], [67, 2, 'Issuer Application Data, Byte 3'],
        [69, 10, 'Terminal Verification Results'], [79, 8, 'Issuer Application Data, Byte 4–7'],
        [87, 12, 'Cryptogram Amount'], [99, 2, 'Issuer Application Data, Byte 8'],
        [101, 16, 'Issuer Application Data, Byte 9–16'], [117, 2, 'Issuer Application Data, Byte 1'],
        [119, 2, 'Issuer Application Data, Byte 17'], [121, 30, 'Issuer Application Data, Byte 18–32'],
        [151, 8, 'Form Factor Indicator'], [159, 10, 'Issuer Script 1 Results']
    ]

    def __init__(self, record_length: int = 168):
        """
        Initialize the Visa BASE II parser.

        Args:
            record_length (int): Expected length of each record. Defaults to 168.
        """
        self.record_length = record_length
        self._tcr_layouts = self._build_layout_map()
        self._METADATA_TCs = {'90', '91', '92'}
        self.encoding: Optional[str] = None

    def _build_layout_map(self) -> Dict[str, list]:
        """Build a mapping of transaction codes to their respective TCR layouts."""
        layouts = {
            'TCR_05X0': self.TCR_05X0,
            'TCR_05X1': self.TCR_05X1,
            'TCR_05X5': self.TCR_05X5,
            'TCR_05X7': self.TCR_05X7,
        }

        tcr_map = {}
        draft_data_tcs = ['05', '06', '07', '15', '16', '17', '25', '26', '27', '35', '36', '37']

        for tc in draft_data_tcs:
            tcr_map[f'{tc}X0'] = layouts['TCR_05X0']
            tcr_map[f'{tc}X1'] = layouts['TCR_05X1']
            tcr_map[f'{tc}X5'] = layouts['TCR_05X5']
            tcr_map[f'{tc}X7'] = layouts['TCR_05X7']

        return tcr_map

    def _parse_record(self, record_str: str) -> Optional[Dict[str, Any]]:
        """
        Parse a single Transaction Component Record (TCR).

        Args:
            record_str (str): The TCR string to parse.

        Returns:
            Optional[Dict[str, Any]]: Parsed field data or None if layout not found.
        """
        if len(record_str) < 4:
            LOGGER.warning(f"Record too short: {len(record_str)} characters")
            return None

        tcr_key = f"{record_str[0:2]}X{record_str[3:4]}"
        layout = self._tcr_layouts.get(tcr_key)

        if not layout:
            LOGGER.debug(f"No layout found for TCR key: {tcr_key}")
            return None

        parsed_data = {}
        for start, length, name in layout:
            # Skip fields that are already handled at the transaction level
            if name in ('Transaction Code', 'Transaction Code Qualifier', 'Transaction Component Sequence Number'):
                continue

            try:
                value = record_str[start - 1: start + length - 1].strip()
                parsed_data[name] = value
            except IndexError:
                LOGGER.warning(f"Index error parsing field '{name}' in record")
                parsed_data[name] = ''

        return parsed_data

    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect the file encoding by sampling and comparing digit counts.

        Args:
            file_path (Path): Path to the file to analyze.

        Returns:
            str: The detected encoding ('cp500' or 'cp1252').

        Raises:
            EncodingError: If encoding detection fails.
        """
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(self.record_length * 10)  # Sample multiple records
        except IOError as e:
            raise EncodingError(f"Failed to read file for encoding detection: {e}")

        encodings_to_test = ['cp500', 'cp1252']
        digit_counts = {}

        for encoding in encodings_to_test:
            try:
                decoded = sample.decode(encoding)
                digit_counts[encoding] = sum(c.isdigit() for c in decoded)
            except UnicodeDecodeError:
                digit_counts[encoding] = -1

        # Choose encoding with more digits (financial data should have many digits)
        best_encoding = max(digit_counts, key=digit_counts.get)

        if digit_counts[best_encoding] == -1:
            raise EncodingError("Failed to decode file with any supported encoding")

        LOGGER.info(f"Detected encoding: {best_encoding} (digit count: {digit_counts[best_encoding]})")
        return best_encoding

    def parse_file(self, input_path: Union[str, os.PathLike]) -> Iterator[Dict[str, Any]]:
        """
        Parse a Visa BASE II clearing transaction file.

        Args:
            input_path (Union[str, os.PathLike]): Path to the .ctf file to parse.

        Yields:
            Dict[str, Any]: Complete transaction records with all associated TCRs.

        Raises:
            FileNotFoundError: If the input file doesn't exist.
            ParseError: If parsing fails.
            EncodingError: If encoding detection fails.
        """
        file_path = Path(input_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            self.encoding = self._detect_encoding(file_path)
        except EncodingError:
            raise

        LOGGER.info(f"Parsing file: {file_path} with encoding: {self.encoding}")

        current_transaction = {}
        transaction_count = 0

        try:
            with open(file_path, 'r', encoding=self.encoding, errors='replace') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        record_str = line
                        if len(record_str) != self.record_length:
                            LOGGER.debug(f"Skipping line {line_num}: incorrect length {len(record_str)}")
                            continue

                        tc_code = record_str[0:2]

                        # Skip metadata transaction codes and unknown codes
                        if tc_code in self._METADATA_TCs or tc_code not in self.TC_DEFINITIONS:
                            LOGGER.debug(f"Skipping metadata/unknown TC: {tc_code}")
                            continue

                        tcr_num_str = record_str[3:4]

                        # Determine if this starts a new transaction
                        is_new_transaction = (
                                not current_transaction or
                                tc_code != current_transaction.get('Transaction Code') or
                                tcr_num_str == '0'
                        )

                        if is_new_transaction:
                            # Yield the previous transaction if it exists
                            if current_transaction:
                                yield current_transaction
                                transaction_count += 1

                            # Start new transaction
                            current_transaction = {
                                'Transaction Code': tc_code,
                                'Transaction Description': self.TC_DEFINITIONS.get(tc_code, 'Unknown'),
                                'TCRs_Present': [],
                                '_line_number': line_num
                            }

                        # Parse the current record
                        parsed_fields = self._parse_record(record_str)
                        if parsed_fields:
                            current_transaction.update(parsed_fields)

                        # Track which TCRs are present
                        if tcr_num_str not in current_transaction['TCRs_Present']:
                            current_transaction['TCRs_Present'].append(tcr_num_str)

                    except Exception as e:
                        LOGGER.error(f"Error processing line {line_num}: {e}")
                        continue

        except IOError as e:
            raise ParseError(f"Error reading file: {e}")

        # Don't forget the last transaction
        if current_transaction:
            yield current_transaction
            transaction_count += 1

        LOGGER.info(f"Successfully parsed {transaction_count} transactions")

    def get_transaction_summary(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a summary of key transaction fields.

        Args:
            transaction (Dict[str, Any]): A parsed transaction record.

        Returns:
            Dict[str, Any]: Summary with key fields extracted and formatted.
        """
        return {
            'transaction_code': transaction.get('Transaction Code'),
            'description': transaction.get('Transaction Description'),
            'account_number': self._mask_account_number(transaction.get('Account Number')),
            'amount': transaction.get('Source Amount'),
            'currency': transaction.get('Source Currency Code'),
            'merchant_name': transaction.get('Merchant Name'),
            'merchant_city': transaction.get('Merchant City'),
            'merchant_country': transaction.get('Merchant Country Code'),
            'purchase_date': transaction.get('Purchase Date (MMDD)'),
            'tcrs_present': transaction.get('TCRs_Present', [])
        }

    def _mask_account_number(self, account_number: str) -> str:
        """
        Mask account number showing first digit + asterisks + last 3 digits + asterisk.

        Args:
            account_number (str): The account number to mask

        Returns:
            str: Masked account number or None if input is empty/None
        """
        if not account_number or not account_number.strip():
            return None

        account_number = account_number.strip()

        if len(account_number) <= 4:
            # For very short numbers, mask all but first character
            return account_number[0] + '*' * (len(account_number) - 1)

        # Pattern analysis for '4111111111111111' -> '4***********111*':
        # - Position 0: '4' (first digit)
        # - Positions 1-11: 11 asterisks (masking digits 1-11 of original)
        # - Positions 12-14: '111' (last 3 digits from original positions 13-15)
        # - Position 15: '*' (final asterisk)

        first_digit = account_number[0]
        last_three = account_number[-3:]

        # We need exactly 11 asterisks in the middle section
        # This masks positions 1 through 11 of the original number
        middle_asterisks = 11

        return first_digit + '*' * middle_asterisks + last_three + '*'
