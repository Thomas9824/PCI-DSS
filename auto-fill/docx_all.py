#!/usr/bin/env python3
"""
Main orchestration script for the complete DOCX tagging workflow.
1. Downloads DOCX from PCI website based on language
2. Transforms requirement IDs from JSON
3. Replaces form fields with tags
"""

import subprocess
import sys
import os
import json
import tempfile
import shutil


def generate_docx_with_tags(requirement_ids, language_code, output_dir=None):
    """
    Complete workflow to generate a tagged DOCX file.

    Args:
        requirement_ids (list): List of requirement IDs extracted from PDF
        language_code (str): Language code (EN, FR, DE, etc.)
        output_dir (str): Output directory for final file (optional)

    Returns:
        tuple: (file_path, stats_dict) where:
            - file_path (str): Path to the generated tagged DOCX file, or None if failed
            - stats_dict (dict): Statistics about the tagging process
    """
    stats = {
        'total_requirements': len(requirement_ids),
        'tags_found': 0,
        'missing_tags': 0,
        'transformed_variants': 0
    }

    # Import required modules at the beginning
    import io

    print("="*70)
    print("DOCX WITH TAGS - COMPLETE WORKFLOW")
    print("="*70)
    print(f"Language: {language_code}")
    print(f"Number of requirement IDs: {len(requirement_ids)}")
    print()

    # Step 1: Save requirement IDs to JSON file
    print("Step 1: Saving requirement IDs to JSON...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ids_json_path = os.path.join(script_dir, "requirement_ids.json")

    with open(ids_json_path, 'w', encoding='utf-8') as f:
        json.dump(requirement_ids, f, indent=2, ensure_ascii=False)
    print(f"  Saved to: {ids_json_path}")

    # Step 2: Transform IDs (generate variants with suffixes)
    print("\nStep 2: Transforming requirement IDs...")
    transform_script = os.path.join(script_dir, "transform_ids.py")

    try:
        # Import transform_ids functions directly
        sys.path.insert(0, script_dir)
        import transform_ids

        transformed_json_path = os.path.join(script_dir, "requirement_ids_transformed.json")
        transform_ids.process_ids(ids_json_path, transformed_json_path)
        print(f"  Transformation complete: {transformed_json_path}")

        # Count transformed variants
        with open(transformed_json_path, 'r', encoding='utf-8') as f:
            transformed_data = json.load(f)
            stats['transformed_variants'] = len(transformed_data)
    except Exception as e:
        print(f"  Error during transformation: {e}")
        import traceback
        traceback.print_exc()
        stats['error_step'] = 'transformation'
        stats['error_message'] = str(e)
        return (None, stats)

    # Step 3: Download DOCX from PCI website
    print("\nStep 3: Downloading DOCX from PCI website...")
    docx_scraping_script = os.path.join(script_dir, "docx_scraping.py")

    try:
        # Import docx_scraping functions directly
        import docx_scraping

        # Use temporary directory for download
        temp_download_dir = tempfile.mkdtemp()
        print(f"  Temporary download directory: {temp_download_dir}")

        downloaded_file = docx_scraping.download_docx_from_pciwebsite(
            language_code,
            temp_download_dir
        )

        if not downloaded_file:
            print("  Error: Failed to download DOCX file")
            shutil.rmtree(temp_download_dir, ignore_errors=True)
            stats['error_step'] = 'download'
            stats['error_message'] = 'Failed to download DOCX file from PCI website'
            return (None, stats)

        print(f"  Downloaded: {downloaded_file}")

        # Copy to working directory
        docx_filename = os.path.basename(downloaded_file)
        working_docx_path = os.path.join(script_dir, docx_filename)

        if os.path.exists(working_docx_path):
            os.remove(working_docx_path)

        shutil.copy2(downloaded_file, working_docx_path)
        print(f"  Copied to working directory: {working_docx_path}")

        # Clean up temp directory
        shutil.rmtree(temp_download_dir, ignore_errors=True)

    except Exception as e:
        print(f"  Error during download: {e}")
        import traceback
        traceback.print_exc()
        stats['error_step'] = 'download'
        stats['error_message'] = f'Error downloading DOCX: {str(e)}'
        return (None, stats)

    # Step 4: Replace form fields with tags
    print("\nStep 4: Replacing form fields with tags...")
    replace_script = os.path.join(script_dir, "replace_form_fields.py")

    try:
        # Import replace_form_fields functions directly
        import replace_form_fields

        # Load transformed tags
        with open(transformed_json_path, 'r', encoding='utf-8') as f:
            tags_list = json.load(f)

        # Generate output filename
        output_filename = docx_filename.replace('.docx', '_tagged.docx')
        output_path = os.path.join(script_dir, output_filename)

        # Capture stdout to count warning messages
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        try:
            # Process the document - now returns tuple (replaced_count, total_fields_count)
            result = replace_form_fields.process_document(
                working_docx_path,
                output_path,
                tags_list
            )

            # Handle tuple return
            if isinstance(result, tuple):
                total_replaced, total_fields_in_tables = result
            else:
                # Backward compatibility
                total_replaced = result
                total_fields_in_tables = total_replaced
        finally:
            # Restore stdout and get captured output
            sys.stdout = old_stdout
            output_text = captured_output.getvalue()
            print(output_text, end='')  # Print it for debugging

        # Count warning messages for unreplaced fields
        unreplaced_count = output_text.count("⚠ ATTENTION: Plus de balises disponibles!")

        print(f"  Replaced {total_replaced} form fields")
        print(f"  Total fields in tables with IDs: {total_fields_in_tables}")
        print(f"  Output file: {output_path}")

        # Update statistics
        # tags_found = number of form fields successfully replaced
        # unreplaced_fields = counted from warning messages
        # Calculate missing IDs: each ID has 5 variants (a, b, c, d, e)
        missing_ids = unreplaced_count // 5 if unreplaced_count > 0 else 0

        stats['tags_found'] = total_replaced
        stats['unreplaced_fields'] = unreplaced_count
        stats['total_fields_in_document'] = total_fields_in_tables  # Only count fields in tables with IDs
        stats['missing_ids'] = missing_ids

        # Move to output directory if specified
        if output_dir and os.path.exists(output_dir):
            final_path = os.path.join(output_dir, output_filename)
            shutil.copy2(output_path, final_path)
            print(f"  Copied to output directory: {final_path}")
            return (final_path, stats)
        else:
            return (output_path, stats)

    except Exception as e:
        print(f"  Error during form field replacement: {e}")
        import traceback
        traceback.print_exc()
        stats['error_step'] = 'replacement'
        stats['error_message'] = f'Error replacing form fields: {str(e)}'
        return (None, stats)

    finally:
        # Clean up intermediate files
        print("\nStep 5: Cleaning up intermediate files...")
        if os.path.exists(working_docx_path):
            os.remove(working_docx_path)
            print(f"  Removed: {working_docx_path}")


def process_docx(file_path):
    """
    Legacy function for backward compatibility.
    Processes an existing DOCX file with transform + replace.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Exécution de transform_ids.py ===")
    transform_script = os.path.join(script_dir, "transform_ids.py")
    subprocess.run(["python", transform_script, file_path])

    print("\n=== Exécution de replace_form_fields.py ===")
    replace_script = os.path.join(script_dir, "replace_form_fields.py")
    subprocess.run(["python", replace_script, file_path])

    print("\n=== Traitement terminé ===")


if __name__ == "__main__":
    # Test mode: run with requirement IDs and language
    if len(sys.argv) >= 3:
        # Mode 1: generate_docx_with_tags <ids_json_file> <language>
        ids_file = sys.argv[1]
        language = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None

        if not os.path.exists(ids_file):
            print(f"Error: File '{ids_file}' not found")
            sys.exit(1)

        with open(ids_file, 'r', encoding='utf-8') as f:
            requirement_ids = json.load(f)

        result = generate_docx_with_tags(requirement_ids, language, output_dir)

        if result:
            print(f"\n✓ Success! Tagged DOCX generated: {result}")
        else:
            print(f"\n✗ Failed to generate tagged DOCX")
            sys.exit(1)

    elif len(sys.argv) >= 2:
        # Mode 2: Legacy mode - process existing DOCX file
        file_path = sys.argv[1]

        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found")
            sys.exit(1)

        if not file_path.endswith('.docx'):
            print("Error: File must be a .docx document")
            sys.exit(1)

        print(f"Processing file: {file_path}")
        process_docx(file_path)

    else:
        print("Usage:")
        print("  Mode 1 (new workflow): python docx_all.py <ids_json_file> <language> [output_dir]")
        print("  Mode 2 (legacy): python docx_all.py <docx_file>")
        sys.exit(1)

