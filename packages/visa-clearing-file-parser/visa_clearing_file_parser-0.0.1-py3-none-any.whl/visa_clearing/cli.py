import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from .parser import VisaBaseIIParser
from .exceptions import VisaClearingError


def format_transaction(transaction: Dict[str, Any], format_type: str = 'summary') -> str:
    """Format transaction for display."""
    if format_type == 'json':
        return json.dumps(transaction, indent=2)

    elif format_type == 'summary':
        parser = VisaBaseIIParser()
        summary = parser.get_transaction_summary(transaction)
        lines = [
            f"Transaction: {summary['description']} ({summary['transaction_code']})",
            f"Amount: {summary['amount']} {summary['currency']}",
            f"Merchant: {summary['merchant_name']}",
            f"Location: {summary['merchant_city']}, {summary['merchant_country']}",
            f"Purchase Date: {summary['purchase_date']}",
            f"TCRs Present: {', '.join(summary['tcrs_present'])}",
        ]
        return '\n'.join(lines)

    else:  # table format
        lines = []
        for key, value in transaction.items():
            if key.startswith('_'):
                continue
            lines.append(f"{key:<35}: {value}")
        return '\n'.join(lines)


def parse_command(args):
    """Handle the parse command."""
    try:
        parser = VisaBaseIIParser()
        transactions = list(parser.parse_file(args.file))

        if not transactions:
            print("No transactions found in file.")
            return

        output_lines = []
        for i, transaction in enumerate(transactions, 1):
            if args.format == 'json':
                output_lines.append(format_transaction(transaction, 'json'))
            else:
                output_lines.append(f"=== Transaction {i} ===")
                output_lines.append(format_transaction(transaction, args.format))
                output_lines.append("")

        output_content = '\n'.join(output_lines)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"Output written to {args.output}")
        else:
            print(output_content)

        print(f"\n📊 Summary: Processed {len(transactions)} transactions")

    except VisaClearingError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def info_command(args):
    """Handle the info command."""
    try:
        parser = VisaBaseIIParser()

        print("📄 Visa BASE II Clearing Parser")
        print("=" * 40)
        print(f"Record Length: {parser.record_length}")
        print(f"Supported Transaction Types: {len(parser.TC_DEFINITIONS)}")
        print(f"Supported TCR Layouts: {len(parser._tcr_layouts)}")

        if args.verbose:
            print("\n📋 Supported Transaction Types:")
            for code, desc in parser.TC_DEFINITIONS.items():
                print(f"  {code}: {desc}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Visa BASE II Clearing Transaction File Parser',
        prog='visa-clearing'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse a clearing file')
    parse_parser.add_argument('file', type=Path, help='Path to the .ctf file')
    parse_parser.add_argument(
        '--format',
        choices=['table', 'summary', 'json'],
        default='summary',
        help='Output format (default: summary)'
    )
    parse_parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file (default: stdout)'
    )

    # Info command
    info_parser = subparsers.add_parser('info', help='Show parser information')
    info_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information'
    )

    args = parser.parse_args()

    if args.command == 'parse':
        parse_command(args)
    elif args.command == 'info':
        info_command(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
