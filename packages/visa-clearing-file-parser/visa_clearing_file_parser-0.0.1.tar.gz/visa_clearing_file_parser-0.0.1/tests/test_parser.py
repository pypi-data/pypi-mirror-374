"""
Comprehensive test suite for visa-clearing-file-parser library.
"""

import pytest
from unittest.mock import mock_open, patch, MagicMock
from pathlib import Path
import tempfile
import time
from visa_clearing import VisaBaseIIParser
from visa_clearing.exceptions import VisaClearingError, ParseError, EncodingError


class TestVisaBaseIIParser:

    def test_parser_initialization_default(self):
        """Test parser initialization with default parameters."""
        parser = VisaBaseIIParser()
        assert parser.record_length == 168
        assert parser.encoding is None
        assert isinstance(parser._tcr_layouts, dict)
        assert len(parser.TC_DEFINITIONS) > 0

    def test_parser_initialization_custom_length(self):
        """Test parser initialization with custom record length."""
        parser = VisaBaseIIParser(record_length=200)
        assert parser.record_length == 200

    def test_transaction_code_definitions_coverage(self):
        """Test that all expected transaction codes are defined."""
        parser = VisaBaseIIParser()

        expected_codes = {
            '05': 'Sales Draft',
            '06': 'Credit Voucher',
            '07': 'Cash Disbursement',
            '15': 'Chargeback, Sales Draft',
            '16': 'Chargeback, Credit Voucher',
            '25': 'Reversal, Sales Draft',
            '35': 'Chargeback Reversal of Sales Draft'
        }

        for code, description in expected_codes.items():
            assert parser.TC_DEFINITIONS[code] == description

    def test_tcr_layout_mapping_completeness(self):
        """Test that TCR layouts are properly mapped for all draft data transaction codes."""
        parser = VisaBaseIIParser()

        draft_data_tcs = ['05', '06', '07', '15', '16', '17', '25', '26', '27', '35', '36', '37']
        tcr_numbers = ['0', '1', '5', '7']

        for tc in draft_data_tcs:
            for tcr in tcr_numbers:
                layout_key = f'{tc}X{tcr}'
                assert layout_key in parser._tcr_layouts, f"Missing layout for {layout_key}"

    def test_build_layout_map_structure(self):
        """Test the internal layout map structure."""
        parser = VisaBaseIIParser()

        # Test that layouts contain expected field definitions
        layout_05x0 = parser._tcr_layouts['05X0']
        assert len(layout_05x0) > 0

        # Each layout entry should be [start, length, name]
        for entry in layout_05x0:
            assert isinstance(entry, list)
            assert len(entry) == 3
            assert isinstance(entry[0], int)  # start position
            assert isinstance(entry[1], int)  # length
            assert isinstance(entry[2], str)  # field name

    def test_parse_record_valid_sales_draft(self):
        """Test parsing a valid Sales Draft TCR 0 record."""
        parser = VisaBaseIIParser()

        # Create a mock Sales Draft record (TC=05, TCR=0)
        record = (
            '05'  # Transaction Code
            + '0'  # Transaction Code Qualifier
            + '0'  # Transaction Component Sequence Number
            + '4123456789012345'  # Account Number (positions 5-20)
            + '001'  # Account Number Extension (positions 21-23)
            + ' ' * 142  # Pad remaining fields
        )
        record = record[:168]  # Ensure exactly 168 characters

        result = parser._parse_record(record)

        assert result is not None
        assert isinstance(result, dict)
        assert 'Account Number' in result
        assert result['Account Number'] == '4123456789012345'
        assert 'Account Number Extension' in result
        assert result['Account Number Extension'] == '001'

    def test_parse_record_unknown_layout(self):
        """Test parsing record with unknown transaction code/layout."""
        parser = VisaBaseIIParser()
        record = '99' + '0' + '9' + ' ' * 165  # Unknown TC=99, TCR=9

        result = parser._parse_record(record)
        assert result is None

    def test_parse_record_too_short(self):
        """Test parsing record that's too short."""
        parser = VisaBaseIIParser()
        record = '05'  # Only 2 characters, need at least 4

        result = parser._parse_record(record)
        assert result is None

    def test_parse_record_field_extraction(self):
        """Test that fields are correctly extracted from their positions."""
        parser = VisaBaseIIParser()

        # Create record with known values in specific positions
        record = (
            '05'  # TC
            + '0'  # TCQ
            + '0'  # TCSN
            + '4111111111111111'  # Account Number (pos 5-20, 16 chars)
            + '123'  # Account Number Extension (pos 21-23, 3 chars)
            + '1'    # Floor Limit Indicator (pos 24, 1 char)
            + ' ' * 140  # Pad rest
        )
        record = record[:168]

        result = parser._parse_record(record)

        assert result['Account Number'] == '4111111111111111'
        assert result['Account Number Extension'] == '123'
        assert result['Floor Limit Indicator'] == '1'

    @patch('builtins.open', new_callable=mock_open)
    def test_detect_encoding_cp500_preferred(self, mock_file):
        """Test encoding detection preferring CP500 when it has more digits."""
        parser = VisaBaseIIParser()

        # Mock file content that decodes better with CP500
        mock_cp500_content = "123456789ABCD"  # More digits when decoded as CP500
        mock_cp1252_content = "ABCDEFGHIJKLM"  # Fewer digits when decoded as CP1252

        test_data = b'\xF1\xF2\xF3\xF4\xF5\xC1\xC2\xC3'
        mock_file.return_value.read.return_value = test_data

        with patch('builtins.open', mock_open()) as mock_open_func:

            mock_file_obj = MagicMock()

            # Create a custom bytes-like object that can be decoded
            class MockBytes:
                def decode(self, encoding, errors='strict'):
                    if encoding == 'cp500':
                        return mock_cp500_content
                    elif encoding == 'cp1252':
                        return mock_cp1252_content
                    else:
                        raise UnicodeDecodeError(encoding, b'', 0, 1, 'test error')

            mock_file_obj.read.return_value = MockBytes()
            mock_open_func.return_value.__enter__.return_value = mock_file_obj

            result = parser._detect_encoding(Path('test.ctf'))

            # Should choose cp500 because it has more digits (9 vs 0)
            assert result == 'cp500'

    def test_detect_encoding_file_not_found(self):
        """Test encoding detection with non-existent file."""
        parser = VisaBaseIIParser()

        with pytest.raises(EncodingError):
            parser._detect_encoding(Path('nonexistent.ctf'))

    def test_parse_file_nonexistent(self):
        """Test parsing non-existent file raises FileNotFoundError."""
        parser = VisaBaseIIParser()

        with pytest.raises(FileNotFoundError):
            list(parser.parse_file('nonexistent.ctf'))

    @patch('visa_clearing.parser.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_parse_file_empty_file(self, mock_file, mock_exists):
        """Test parsing empty file."""
        parser = VisaBaseIIParser()
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = b''

        with patch.object(parser, '_detect_encoding', return_value='cp1252'):
            mock_file.return_value.__iter__.return_value = iter([])

            transactions = list(parser.parse_file('empty.ctf'))
            assert len(transactions) == 0

    def test_get_transaction_summary_complete(self):
        """Test transaction summary generation with all fields."""
        parser = VisaBaseIIParser()

        transaction = {
            'Transaction Code': '05',
            'Transaction Description': 'Sales Draft',
            'Account Number': '4111111111111111',
            'Source Amount': '000000100050',
            'Source Currency Code': '840',
            'Merchant Name': 'TEST MERCHANT',
            'Merchant City': 'NEW YORK',
            'Merchant Country Code': 'USA',
            'Purchase Date (MMDD)': '1215',
            'TCRs_Present': ['0', '1', '5']
        }

        summary = parser.get_transaction_summary(transaction)

        assert summary['transaction_code'] == '05'
        assert summary['description'] == 'Sales Draft'
        assert summary['account_number'] == '4***********111*'  # Masked
        assert summary['amount'] == '000000100050'
        assert summary['currency'] == '840'
        assert summary['merchant_name'] == 'TEST MERCHANT'
        assert summary['merchant_city'] == 'NEW YORK'
        assert summary['merchant_country'] == 'USA'
        assert summary['purchase_date'] == '1215'
        assert summary['tcrs_present'] == ['0', '1', '5']

    def test_get_transaction_summary_minimal(self):
        """Test transaction summary with minimal transaction data."""
        parser = VisaBaseIIParser()

        transaction = {
            'Transaction Code': '06',
            'Transaction Description': 'Credit Voucher',
            'TCRs_Present': ['0']
        }

        summary = parser.get_transaction_summary(transaction)

        assert summary['transaction_code'] == '06'
        assert summary['description'] == 'Credit Voucher'
        assert summary['account_number'] is None
        assert summary['amount'] is None
        assert summary['currency'] is None
        assert summary['merchant_name'] is None
        assert summary['tcrs_present'] == ['0']

    def test_metadata_transaction_codes(self):
        """Test that metadata transaction codes are properly defined."""
        parser = VisaBaseIIParser()

        # These should be in the metadata set
        assert '90' in parser._METADATA_TCs
        assert '91' in parser._METADATA_TCs
        assert '92' in parser._METADATA_TCs

    @patch('visa_clearing.parser.Path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    def test_parse_file_with_metadata_transactions(self, mock_file, mock_exists):
        """Test that metadata transactions are skipped during parsing."""
        parser = VisaBaseIIParser()

        # Based on your actual file format - each line appears to be exactly 168 characters
        mock_lines = [
            # Metadata transaction (90) - should be skipped
            "90" + "48369625231" + " " * 155,  # 168 chars total

            # Regular Sales Draft transaction (05) - should be processed
            "05" + "004462214292764664000   24836965210800066650469000000000811000000000000   000000000995826onenergys.com            Liverpool    GB 7399L76PD     1009N0113549 4 010000",

            # Another metadata transaction (91) - should be skipped
            "91" + "0000000000000000000000000000000000000001000001000000000004      00000001000000002                  000000000000995" + " " * 71,

            # Another metadata transaction (92) - should be skipped
            "92" + "0000000000000000000000000000000000000001000001000000000005              000000003                  000000000000995" + " " * 71,
        ]

        # Verify all lines are exactly 168 characters (standard for Visa Base II)
        for i, line in enumerate(mock_lines):
            if len(line) != 168:
                # Adjust line length to exactly 168
                if len(line) < 168:
                    mock_lines[i] = line + " " * (168 - len(line))
                else:
                    mock_lines[i] = line[:168]

        # Verify line lengths after adjustment
        for i, line in enumerate(mock_lines):
            assert len(line) == 168, f"Line {i} has length {len(line)}, expected 168"

            # Create the mock content that will be returned by read()
        mock_content = '\n'.join(mock_lines)

        mock_file = mock_open(read_data=mock_content)
        mock_file.return_value.__iter__ = lambda self: iter(mock_content.splitlines())

        with patch.object(parser, '_detect_encoding', return_value='cp1252'):
            # Mock the file content as both bytes (for encoding detection) and lines (for iteration)
            with patch('builtins.open', mock_file):

                transactions = list(parser.parse_file('test.ctf'))

                # Debug output
                print(f"Found {len(transactions)} transactions")
                for i, t in enumerate(transactions):
                    print(f"Transaction {i}: code='{t.get('Transaction Code', 'MISSING')}'")

                # Should only have 1 transaction (the Sales Draft with code '05')
                assert len(transactions) == 1, f"Expected 1 transaction, got {len(transactions)}"
                assert transactions[0]['Transaction Code'] == '05'

    def test_account_number_masking_in_summary(self):
        """Test that account numbers are properly masked in summaries."""
        parser = VisaBaseIIParser()

        test_cases = [
            ('4111111111111111', '4***********111*'),
            ('5555444433332222', '5***********222*'),
            ('', None),
            (None, None),
        ]

        for account_number, expected_masked in test_cases:
            transaction = {
                'Transaction Code': '05',
                'Transaction Description': 'Sales Draft',
                'Account Number': account_number,
                'TCRs_Present': ['0']
            }

            summary = parser.get_transaction_summary(transaction)
            assert summary['account_number'] == expected_masked


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_encoding_error_propagation(self):
        """Test that encoding errors are properly propagated."""
        parser = VisaBaseIIParser()

        with patch('visa_clearing.parser.Path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("File read error")):
                with pytest.raises(EncodingError):
                    parser._detect_encoding(Path('test.ctf'))

    def test_parse_error_on_file_read_failure(self):
        """Test that file read errors during parsing raise ParseError."""
        parser = VisaBaseIIParser()

        with patch('visa_clearing.parser.Path.exists', return_value=True):
            with patch.object(parser, '_detect_encoding', return_value='cp1252'):
                with patch('builtins.open', side_effect=IOError("Read error")):
                    with pytest.raises(ParseError):
                        list(parser.parse_file('test.ctf'))

    def test_malformed_record_handling(self):
        """Test handling of malformed records."""
        parser = VisaBaseIIParser()

        # Test with record that causes IndexError during field extraction
        malformed_record = '05' + '0'   # Too short for field extraction

        result = parser._parse_record(malformed_record)

        # Should return None for malformed records that are too short
        assert result is None


class TestIntegration:
    """Integration tests with realistic data."""

    def test_complete_transaction_parsing_workflow(self):
        """Test complete workflow with multiple transaction types."""
        parser = VisaBaseIIParser()

        # Create realistic test data
        mock_transactions = [
            # Header record
            '90' + '48369625231' + ' ' * 155,
            # Sales Draft with multiple TCRs
            '05' + '0' + '0' + '4111111111111111' + '001' + '0' * 142,
            '05' + '0' + '1' + '1' * 165,  # Additional TCR for same transaction
            # Credit Voucher
            '06' + '0' + '0' + '5555444433332222' + '002' + '1' * 142,
            # Chargeback
            '15' + '0' + '0' + '4000000000000002' + '003' + '2' * 142,
            # Footer records
            '91' + '0' * 36 + '001000001000000000004' + ' ' * 6 + '00000001000000002' + ' ' * 18 + '000000000000995' + ' ' * 71,
            '92' + '0' * 36 + '001000001000000000005' + ' ' * 14 + '000000003' + ' ' * 18 + '000000000000995' + ' ' * 71
        ]

        # Pad all records to exactly 168 characters
        mock_transactions = [txn[:168].ljust(168) for txn in mock_transactions]

        # Create the mock content that will be returned by read()
        mock_content = '\n'.join(mock_transactions)

        mock_file = mock_open(read_data=mock_content)
        mock_file.return_value.__iter__ = lambda self: iter(mock_content.splitlines())

        with patch('visa_clearing.parser.Path.exists', return_value=True):
            with patch.object(parser, '_detect_encoding', return_value='cp1252'):
                with patch('builtins.open', mock_file):
                    #mock_file.return_value.__iter__.return_value = iter(mock_transactions)
                    #mock_file.return_value.read.return_value = mock_content

                    transactions = list(parser.parse_file('test.ctf'))

                    # Should have 3 transactions (Sales Draft groups TCRs 0 and 1)
                    assert len(transactions) == 3

                    # Check transaction types
                    assert transactions[0]['Transaction Code'] == '05'
                    assert transactions[1]['Transaction Code'] == '06'
                    assert transactions[2]['Transaction Code'] == '15'

                    # Check that Sales Draft has both TCRs
                    assert '0' in transactions[0]['TCRs_Present']
                    assert '1' in transactions[0]['TCRs_Present']

                    # Check that each transaction has the expected fields
                    for txn in transactions:
                        assert 'Transaction Description' in txn
                        assert 'TCRs_Present' in txn
                        assert txn['Transaction Description'] in parser.TC_DEFINITIONS.values()


class TestCLI:
    """Test CLI functionality if implemented."""

    def test_cli_module_imports(self):
        """Test that CLI module can be imported."""
        try:
            from visa_clearing.cli import main
            assert callable(main)
        except ImportError:
            pytest.skip("CLI module not yet implemented")


# Performance tests
class TestPerformance:
    """Performance and scalability tests."""

    def test_large_file_handling(self):
        """Test parser performance with large number of transactions."""
        parser = VisaBaseIIParser()

        # Create mock data for 1000 transactions
        num_transactions = 1000
        mock_transactions = []

        for i in range(num_transactions):
            tc = '05' if i % 2 == 0 else '06'  # Alternate between Sales Draft and Credit Voucher
            tcq = '0'  # Transaction Code Qualifier
            tcr_seq = '0'  # TCR sequence number (0 for first/main TCR)

            # Create a properly formatted record
            # Format: TC(2) + TCQ(1) + TCR_SEQ(1) + data fields + padding
            record_data = f'{i:016d}' + '1' * 148  # 16-digit transaction ID + padding
            record = tc + tcq + tcr_seq + record_data

            # Ensure exactly 168 characters
            record = record[:168].ljust(168)
            mock_transactions.append(record)

        mock_content = '\n'.join(mock_transactions)

        # Create a properly configured mock file
        mock_file_instance = mock_open(read_data=mock_content.encode('cp1252'))

        # Mock the file iteration to return individual lines
        mock_file_instance.return_value.__iter__ = lambda self: iter(mock_content.splitlines())

        with patch('visa_clearing.parser.Path.exists', return_value=True):
            with patch.object(parser, '_detect_encoding', return_value='cp1252'):
                with patch('builtins.open',  mock_file_instance):
                    #mock_file.return_value.__iter__.return_value = iter(mock_transactions)
                    #mock_file.return_value.read.return_value = b'test'

                    start_time = time.time()

                    transactions = list(parser.parse_file('test.ctf'))

                    end_time = time.time()
                    processing_time = end_time - start_time

                    # Should complete in reasonable time (less than 2 seconds for 1000 transactions)
                    assert processing_time < 2.0, f"Processing took {processing_time:.2f}s, expected < 2.0s"
                    assert len(transactions) == num_transactions

                    # Verify some transactions were parsed correctly
                    assert transactions[0]['Transaction Code'] == '05'
                    assert transactions[1]['Transaction Code'] == '06'


if __name__ == '__main__':
    pytest.main([__file__])