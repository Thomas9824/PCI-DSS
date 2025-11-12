"""
PCI Requirements Comparison Module
Compares current PCI requirements export with stored reference
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class RequirementsComparator:
    """Compare PCI requirements between two CSV files"""

    def __init__(self, stored_references_dir='stored_references'):
        """
        Initialize the comparator

        Args:
            stored_references_dir: Directory where reference CSVs are stored
        """
        self.base_dir = Path(__file__).parent
        self.references_dir = self.base_dir / stored_references_dir
        self.references_dir.mkdir(exist_ok=True)

    def get_reference_path(self, language):
        """Get the path to the reference file for a given language"""
        return self.references_dir / f"reference_{language}.csv"

    def save_reference(self, csv_path, language):
        """
        Save a CSV file as the reference for comparison

        Args:
            csv_path: Path to the CSV file to save as reference
            language: Language code (EN, FR, etc.)

        Returns:
            dict: Result with success status and message
        """
        try:
            csv_path = Path(csv_path)
            if not csv_path.exists():
                return {
                    'success': False,
                    'error': f'Source file not found: {csv_path}'
                }

            # Read and validate CSV
            df = pd.read_csv(csv_path)

            # Check for required columns
            id_column = 'id' if 'id' in df.columns else 'req_num'
            if id_column not in df.columns:
                return {
                    'success': False,
                    'error': 'CSV must have an "id" or "req_num" column'
                }

            # Save as reference
            reference_path = self.get_reference_path(language)
            df.to_csv(reference_path, index=False)

            return {
                'success': True,
                'message': f'Reference saved for language {language}',
                'reference_path': str(reference_path),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error saving reference: {str(e)}'
            }

    def compare(self, current_csv_path, language):
        """
        Compare current CSV with stored reference

        Args:
            current_csv_path: Path to the current CSV file
            language: Language code (EN, FR, etc.)

        Returns:
            dict: Comparison results with added, removed, and unchanged IDs
        """
        try:
            current_path = Path(current_csv_path)
            reference_path = self.get_reference_path(language)

            # Check if files exist
            if not current_path.exists():
                return {
                    'success': False,
                    'error': f'Current file not found: {current_path}'
                }

            if not reference_path.exists():
                return {
                    'success': False,
                    'error': f'No reference found for language {language}',
                    'has_reference': False
                }

            # Read both CSVs
            df_current = pd.read_csv(current_path)
            df_reference = pd.read_csv(reference_path)

            # Identify ID column
            id_col_current = 'id' if 'id' in df_current.columns else 'req_num'
            id_col_reference = 'id' if 'id' in df_reference.columns else 'req_num'

            # Get sets of IDs
            current_ids = set(df_current[id_col_current].astype(str))
            reference_ids = set(df_reference[id_col_reference].astype(str))

            # Calculate differences
            added_ids = sorted(list(current_ids - reference_ids), key=self._natural_sort_key)
            removed_ids = sorted(list(reference_ids - current_ids), key=self._natural_sort_key)
            unchanged_ids = sorted(list(current_ids & reference_ids), key=self._natural_sort_key)

            # Calculate statistics
            total_current = len(current_ids)
            total_reference = len(reference_ids)

            return {
                'success': True,
                'has_reference': True,
                'comparison': {
                    'added': added_ids,
                    'removed': removed_ids,
                    'unchanged': unchanged_ids,
                    'added_count': len(added_ids),
                    'removed_count': len(removed_ids),
                    'unchanged_count': len(unchanged_ids),
                    'total_current': total_current,
                    'total_reference': total_reference
                },
                'language': language,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error comparing files: {str(e)}'
            }

    def _natural_sort_key(self, s):
        """
        Generate a key for natural sorting (e.g., 1.1, 1.2, 1.10, 2.1)
        """
        import re
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', str(s))]

    def has_reference(self, language):
        """
        Check if a reference exists for the given language

        Args:
            language: Language code (EN, FR, etc.)

        Returns:
            bool: True if reference exists, False otherwise
        """
        reference_path = self.get_reference_path(language)
        return reference_path.exists()

    def get_reference_info(self, language):
        """
        Get information about the stored reference

        Args:
            language: Language code (EN, FR, etc.)

        Returns:
            dict: Information about the reference file
        """
        reference_path = self.get_reference_path(language)

        if not reference_path.exists():
            return {
                'exists': False,
                'language': language
            }

        try:
            # Get file stats
            stats = reference_path.stat()

            # Read CSV to get count
            df = pd.read_csv(reference_path)
            id_column = 'id' if 'id' in df.columns else 'req_num'

            return {
                'exists': True,
                'language': language,
                'path': str(reference_path),
                'size': stats.st_size,
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'requirement_count': len(df),
                'columns': list(df.columns)
            }

        except Exception as e:
            return {
                'exists': True,
                'language': language,
                'error': f'Error reading reference: {str(e)}'
            }


if __name__ == '__main__':
    # Test the comparator
    comparator = RequirementsComparator()
    print("PCI Requirements Comparator initialized")
    print(f"References directory: {comparator.references_dir}")
