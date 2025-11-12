import PyPDF2
import re
import os
import sys
import csv
from typing import List, Tuple, Dict

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pages_text = []

    def extract_all_pages(self) -> List[str]:
        """Extracts text from all PDF pages"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pages_text = []

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    pages_text.append(text)

                return pages_text
        except Exception as e:
            print(f"Error during PDF extraction: {e}")
            return []

    def find_id_range(self, pages_text: List[str]) -> Tuple[int, int]:
        """Finds pages containing IDs from 1.1.1 to the highest ID (including A IDs)"""
        start_page = None
        end_page = None
        highest_id = 0
        highest_a_id = 0

        # Pattern to detect numeric IDs (e.g.: 1.1.1, 12.10, 10.2.6.1, etc.)
        id_pattern = r'\b(\d+)\.(\d+)(?:\.(\d+)(?:\.(\d+))?)?\b'
        # Pattern to detect IDs with A prefix (e.g.: A1.1.1, A2.2.3, etc.)
        a_id_pattern = r'\bA(\d+)\.(\d+)(?:\.(\d+)(?:\.(\d+))?)?\b'

        for page_num, text in enumerate(pages_text):
            # Search for ID 1.1.1 as the start page
            if re.search(r'\b1\.1\.1\b', text) and start_page is None:
                start_page = page_num

            # Search all numeric IDs to find the highest
            matches = re.findall(id_pattern, text)
            for match in matches:
                # Convert ID to number for comparison (support 2, 3 or 4 levels)
                major = int(match[0])
                minor = int(match[1])
                patch = int(match[2]) if match[2] else 0
                sub_patch = int(match[3]) if match[3] else 0

                current_id = major * 10000 + minor * 100 + patch * 10 + sub_patch
                if current_id > highest_id:
                    highest_id = current_id
                    end_page = page_num

            # Search all IDs with A prefix to find the highest
            a_matches = re.findall(a_id_pattern, text)
            for match in a_matches:
                # Convert A ID to number for comparison (support 2, 3 or 4 levels)
                major = int(match[0])
                minor = int(match[1])
                patch = int(match[2]) if match[2] else 0
                sub_patch = int(match[3]) if match[3] else 0

                current_a_id = major * 10000 + minor * 100 + patch * 10 + sub_patch
                if current_a_id > highest_a_id:
                    highest_a_id = current_a_id
                    end_page = page_num

        return start_page, end_page

    def clean_text(self, text: str) -> str:
        """Cleans text from unwanted elements"""
        # Remove page markers
        text = re.sub(r'=== PAGE \d+ ===\s*', '', text)

        # Remove copyright lines and legal notices
        text = re.sub(r'SAQ D de PCI DSS v\d+\.\d+.*?Octobre \d+\s*', '', text, flags=re.DOTALL)
        text = re.sub(r'© \d+-?\s*\d+ PCI Security Standards Council.*?Tous Droits Réservés\.\s*Page \d+\s*', '', text, flags=re.DOTALL)

        # Remove specific header elements line by line
        text = re.sub(r'Section 2 :.*?Questionnaire d\'Auto.*?Commerçants.*?\n', '', text, flags=re.DOTALL)
        text = re.sub(r'Remarque :.*?Standard PCI DSS\..*?\n', '', text, flags=re.DOTALL)
        text = re.sub(r'Date d\'achèvement de l\'auto.*?JJ-MM.*?AAAA.*?\n', '', text, flags=re.DOTALL)

        # Remove generic section titles
        text = re.sub(r'Créer et Maintenir un Réseau et des Systèmes Sécurisés\s*', '', text)
        text = re.sub(r'Exigence \d+ : [^\n]+\n', '', text)

        # Remove answer option blocks
        text = re.sub(r'Exigence de PCI DSS\s*Tests Prévus.*?en Place\s*', '', text, flags=re.DOTALL)
        text = re.sub(r'\(Cocher une réponse pour chaque exigence\)\s*En Place\s*En Place\s*avec CCW\s*Non\s*Applicable\s*Non\s*Testé\s*Pas\s*en Place\s*', '', text, flags=re.DOTALL)

        # Remove lines containing the ♦ symbol
        text = re.sub(r'.*♦.*\n?', '', text, flags=re.MULTILINE)

        # Remove multiple empty lines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        # Clean leading and trailing spaces
        text = text.strip()

        return text

    def merge_suite_sections(self, text: str) -> str:
        """Merges ID (suite) sections with their main sections"""
        lines = text.split('\n')
        processed_lines = []

        # Pattern to detect ID (suite)
        suite_pattern = r'^((?:A)?\d+\.\d+(?:\.\d+(?:\.\d+)?)?)\s*\(suite\)\s*(.*)'

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if it's an ID (suite) line
            suite_match = re.match(suite_pattern, line)
            if suite_match:
                suite_id = suite_match.group(1)
                suite_content = suite_match.group(2).strip()

                # Search for the corresponding main section by going backwards
                main_section_found = False
                for j in range(len(processed_lines) - 1, -1, -1):
                    main_line = processed_lines[j].strip()
                    if main_line.startswith(suite_id + ' ') or main_line.startswith(suite_id + '\t'):
                        main_section_found = True
                        break

                # If we found the main section, add the suite content directly
                if suite_content:
                    processed_lines.append(suite_content)

                # Continue adding following lines until the next ID
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line:
                        processed_lines.append('')
                        i += 1
                        continue

                    # Check if it's a new ID (not suite)
                    id_pattern = r'^((?:A)?\d+\.\d+(?:\.\d+(?:\.\d+)?)?)\s+'
                    if re.match(id_pattern, next_line) and '(suite)' not in next_line:
                        # New ID found, stop merging
                        break

                    processed_lines.append(next_line)
                    i += 1

                # Go back one step as the main loop will increment
                i -= 1
            else:
                # Normal line, add it as is
                processed_lines.append(line)

            i += 1

        return '\n'.join(processed_lines)

    def parse_requirements_data(self, text: str) -> List[Dict]:
        """Parses text to extract structured data by ID chronologically"""
        requirements = []
        processed_ids = set()  # To avoid duplicates

        # Split text into lines for sequential processing
        lines = text.split('\n')

        current_id = None
        current_content = []

        # Pattern to detect IDs at line start (avoid references in text)
        # Support for IDs with 2, 3 or 4 levels (e.g.: 1.1, 1.1.1, 10.2.6.1)
        id_pattern = r'^((?:A)?\d+\.\d+(?:\.\d+(?:\.\d+)?)?)\s*'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Search for an ID at line start
            id_match = re.match(id_pattern, line)

            if id_match:
                # Save previous section if it exists AND hasn't been processed yet
                if current_id and current_content and current_id not in processed_ids:
                    content_text = '\n'.join(current_content).strip()
                    parsed_data_list = self.parse_section_content(current_id, content_text)
                    if parsed_data_list:
                        requirements.extend(parsed_data_list)
                        processed_ids.add(current_id)  # Mark ID as processed

                # Start a new section
                potential_id = id_match.group(1)
                remaining_content = line[len(id_match.group(0)):].strip()

                # Check if it's a real ID or just a reference in text
                if self.is_valid_requirement_id(potential_id, remaining_content, current_id):
                    current_id = potential_id
                    current_content = [remaining_content] if remaining_content else []
                else:
                    # Treat this line as content of current section
                    if current_id:
                        current_content.append(line)
            else:
                # Add line to current section content
                if current_id:
                    current_content.append(line)

        # Don't forget the last section
        if current_id and current_content and current_id not in processed_ids:
            content_text = '\n'.join(current_content).strip()
            parsed_data_list = self.parse_section_content(current_id, content_text)
            if parsed_data_list:
                requirements.extend(parsed_data_list)

        return requirements

    def is_valid_requirement_id(self, potential_id: str, remaining_content: str, current_id: str) -> bool:
        """Checks if a detected ID is really a new requirement ID or just a reference"""

        # If the ID is alone on the line (no content after), it's probably valid
        if len(remaining_content) == 0:
            return True

        # If the content following the ID is too short, it's probably a reference
        if len(remaining_content) < 10:
            return False

        # Typical patterns of a real requirement
        requirement_indicators = [
            r'est\s+stocké',
            r'ne\s+sont?\s+pas\s+stocké',
            r'sont?\s+crypté',
            r'doit\s+',
            r'doivent\s+',
            r'est\s+',
            r'ne\s+peut\s+pas',
            r'ne\s+peuvent\s+pas',
            r'Les\s+\w+\s+qui',
            r'Le\s+\w+\s+qui',
        ]

        # If the content looks like a real requirement
        for pattern in requirement_indicators:
            if re.search(pattern, remaining_content, re.IGNORECASE):
                return True

        # If the content starts with "à" (like "à 3.3.1.3"), it's a reference
        if remaining_content.startswith('à '):
            return False

        # If it's just an ID number without context, it's a reference
        if re.match(r'^\d+\.\d+(?:\.\d+)*\.?\s*$', remaining_content):
            return False

        # If we have substantial content (more than 20 characters), it's probably valid
        if len(remaining_content) > 20:
            return True

        return False

    def parse_section_content(self, requirement_id: str, content: str) -> List[Dict]:
        """Parses section content to extract text, tests and guidance"""
        content = content.strip()

        # STEP 1: First detect the bullet → tests → bullet pattern on full text
        text_parts = self.split_text_by_bullets(content)

        results = []

        if len(text_parts) > 1:
            # Multiple sub-parts detected with bullet → tests → bullet pattern
            # First extract tests and guidance from full content once
            full_parsed_data = self.extract_tests_and_guidance(content)

            for i, text_part in enumerate(text_parts):
                sub_id = f"{requirement_id}.{chr(97 + i)}"  # 97 = 'a' in ASCII

                # For each sub-part, extract only text,
                # but use common tests and guidance
                text_only = self.extract_text_only(text_part)

                results.append({
                    'id': sub_id,
                    'text': text_only,
                    'tests': full_parsed_data['tests'],  # Shared tests
                    'guidance': full_parsed_data['guidance']  # Shared guidance
                })
        else:
            # Single part - normal processing
            parsed_data = self.extract_tests_and_guidance(content)

            results.append({
                'id': requirement_id,
                'text': parsed_data['text'],
                'tests': parsed_data['tests'],
                'guidance': parsed_data['guidance']
            })

        return results

    def extract_text_only(self, content: str) -> str:
        """Extracts only main text by removing tests and guidance"""
        content = content.strip()

        # Remove guidance (Notes d'Applicabilité)
        content = re.sub(r'Notes d\'Applicabilité\s*.*', '', content, flags=re.DOTALL | re.IGNORECASE).strip()

        # Remove tests (lists with • and specific verbs)
        test_verbs = ['Examiner', 'Observer', 'Interroger', 'Vérifier', 'Inspecter', 'Comparer']
        test_pattern = r'(•\s*(?:' + '|'.join(test_verbs) + r').*?)(?=•\s*(?:' + '|'.join(test_verbs) + r')|Notes d\'Applicabilité|$)'

        test_matches = re.findall(test_pattern, content, re.DOTALL | re.IGNORECASE)
        for match in test_matches:
            content = content.replace(match, '').strip()

        # Clean and return main text
        return self.clean_section_text(content)

    def extract_tests_and_guidance(self, content: str) -> Dict:
        """Extracts tests and guidance from content"""
        content = content.strip()

        # Separate content into parts
        tests_part = ""
        guidance_part = ""

        # Extract guidance (Applicability Notes)
        guidance_match = re.search(r'Notes d\'Applicabilité\s*(.*)', content, re.DOTALL | re.IGNORECASE)
        if guidance_match:
            guidance_part = guidance_match.group(1).strip()
            # Remove guidance part from main content
            content = re.sub(r'Notes d\'Applicabilité\s*.*', '', content, flags=re.DOTALL | re.IGNORECASE).strip()

        # Extract tests (lists with • and specific verbs)
        test_verbs = ['Examiner', 'Observer', 'Interroger', 'Vérifier', 'Inspecter', 'Comparer']
        test_pattern = r'(•\s*(?:' + '|'.join(test_verbs) + r').*?)(?=•\s*(?:' + '|'.join(test_verbs) + r')|Notes d\'Applicabilité|$)'

        test_matches = re.findall(test_pattern, content, re.DOTALL | re.IGNORECASE)
        if test_matches:
            tests_part = '\n'.join([match.strip() for match in test_matches])

            # Remove tests from main content
            for match in test_matches:
                content = content.replace(match, '').strip()

        # The rest is considered main text
        text_part = re.sub(r'\s+', ' ', content).strip()

        # Clean parts
        return {
            'text': self.clean_section_text(text_part),
            'tests': self.clean_section_text(tests_part),
            'guidance': self.clean_section_text(guidance_part)
        }

    def split_text_by_bullets(self, text: str) -> List[str]:
        """Splits text into sub-parts based on pattern: content bullets -> test block -> content bullets"""
        if not text:
            return []

        # Exclude Applicability Notes section from processing
        guidance_match = re.search(r'Notes d\'Applicabilité', text, re.IGNORECASE)
        if guidance_match:
            # Only process the part before Applicability Notes
            text_to_analyze = text[:guidance_match.start()].strip()
            guidance_section = text[guidance_match.start():].strip()
        else:
            text_to_analyze = text
            guidance_section = ""

        test_verbs = ['Examiner', 'Observer', 'Interroger', 'Vérifier', 'Inspecter', 'Comparer']
        test_verbs_pattern = '|'.join(test_verbs)

        # Split text (without Applicability Notes) into tokens
        tokens = re.split(r'(•[^•]+)', text_to_analyze)
        tokens = [token.strip() for token in tokens if token.strip()]

        # Identify test blocks (consecutive sequences of test bullets)
        token_types = []
        for token in tokens:
            if token.startswith('•'):
                bullet_content = token[1:].strip()
                is_test_bullet = re.match(r'^(' + test_verbs_pattern + r')', bullet_content, re.IGNORECASE)
                token_types.append('test' if is_test_bullet else 'content')
            else:
                token_types.append('text')

        # Search for pattern: content -> test block -> content
        test_block_start = -1
        test_block_end = -1

        # Analyze global structure to detect interspersed patterns
        total_content = sum(1 for t in token_types if t == 'content')
        total_tests = sum(1 for t in token_types if t == 'test')

        # Conditions for valid segmentation:
        # 1. At least 2 tests total
        # 2. At least 2 contents total
        # 3. There must be content before the first test
        # 4. There must be content after the last test

        if total_tests >= 2 and total_content >= 3:
            # Find position of first and last test
            first_test_pos = -1
            last_test_pos = -1

            for i, token_type in enumerate(token_types):
                if token_type == 'test':
                    if first_test_pos == -1:
                        first_test_pos = i
                    last_test_pos = i

            if first_test_pos != -1 and last_test_pos != -1:
                # Check that there is content before the first test
                has_content_before = any(token_types[j] == 'content' for j in range(0, first_test_pos))

                # Check that there is valid content after the last test (not disguised tests)
                has_content_after = False
                content_after_tokens = []

                for j in range(last_test_pos + 1, len(token_types)):
                    if token_types[j] == 'content':
                        # Check that it's not a misclassified test
                        token_text = tokens[j]
                        if token_text.startswith('•'):
                            bullet_content = token_text[1:].strip()
                            # Double check: ensure it's not a test verb
                            is_really_test = re.match(r'^(' + test_verbs_pattern + r')', bullet_content, re.IGNORECASE)
                            if not is_really_test:
                                content_after_tokens.append(j)
                        else:
                            content_after_tokens.append(j)

                has_content_after = len(content_after_tokens) >= 1

                if has_content_before and has_content_after:
                    test_block_start = first_test_pos
                    test_block_end = last_test_pos

        # If we found a valid test block, split content
        if test_block_start != -1:
            content_parts = []

            # Part before tests
            before_tokens = tokens[:test_block_start]
            before_content = ' '.join(before_tokens).strip()

            # Part after tests (but before Applicability Notes)
            after_tokens = tokens[test_block_end + 1:]
            after_content = ' '.join(after_tokens).strip()

            # NEW LOGIC: Separate content bullets individually
            # Identify content bullets in "before" part
            before_content_bullets = []
            if before_content:
                before_bullet_tokens = re.split(r'(•[^•]+)', before_content)
                before_bullet_tokens = [token.strip() for token in before_bullet_tokens if token.strip()]

                for token in before_bullet_tokens:
                    if token.startswith('•'):
                        bullet_content = token[1:].strip()
                        is_test_bullet = re.match(r'^(' + test_verbs_pattern + r')', bullet_content, re.IGNORECASE)
                        if not is_test_bullet:
                            before_content_bullets.append(token)

            # Identify content bullets in ALL tokens (before, during, after tests)
            # To avoid missing content bullets that end up after tests
            all_content_bullets = []

            for i, token in enumerate(tokens):
                if token.startswith('•'):
                    bullet_content = token[1:].strip()
                    is_test_bullet = re.match(r'^(' + test_verbs_pattern + r')', bullet_content, re.IGNORECASE)

                    # If it's not a test, it's content
                    if not is_test_bullet:
                        all_content_bullets.append(token)

            # Keep part logic for compatibility
            after_content_bullets = []
            if after_content:
                after_bullet_tokens = re.split(r'(•[^•]+)', after_content)
                after_bullet_tokens = [token.strip() for token in after_bullet_tokens if token.strip()]

                for token in after_bullet_tokens:
                    if token.startswith('•'):
                        bullet_content = token[1:].strip()
                        is_test_bullet = re.match(r'^(' + test_verbs_pattern + r')', bullet_content, re.IGNORECASE)
                        if not is_test_bullet:
                            after_content_bullets.append(token)

            # Main text (without bullets)
            main_text_parts = []
            if before_content:
                # Extract main text (before bullets)
                before_main = re.split(r'•[^•]+', before_content)[0].strip()
                if before_main:
                    main_text_parts.append(before_main)

            main_text = ' '.join(main_text_parts).strip()

            # Extract tests found between contents
            test_tokens = tokens[test_block_start:test_block_end + 1]
            test_bullets = []
            for token in test_tokens:
                if token.startswith('•'):
                    bullet_content = token[1:].strip()
                    is_test_bullet = re.match(r'^(' + test_verbs_pattern + r')', bullet_content, re.IGNORECASE)
                    if is_test_bullet:
                        test_bullets.append(token)

            tests_content = ' '.join(test_bullets).strip()

            # Use ALL found content bullets (not just before/after)
            if len(all_content_bullets) >= 2:
                # Create a section for each bullet
                for bullet in all_content_bullets:
                    section_content = main_text + " " + bullet if main_text else bullet

                    # Add Applicability Notes to each section
                    if guidance_section:
                        section_content += "\n" + guidance_section

                    content_parts.append(section_content.strip())
            else:
                # Original logic if less than 2 content bullets
                if before_content:
                    content_parts.append(before_content)

                if after_content:
                    # Add Applicability Notes to last part if they exist
                    if guidance_section:
                        after_content += "\n" + guidance_section
                    content_parts.append(after_content)

            return content_parts if len(content_parts) > 1 else [text]

        return [text]

    def clean_section_text(self, text: str) -> str:
        """Cleans text from a specific section"""
        if not text:
            return ""

        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove residual formatting characters
        text = re.sub(r'[•\-]\s*$', '', text)

        return text.strip()

    def process_pdf(self) -> List[Dict]:
        """Processes complete PDF and returns structured data"""
        print(f"Extracting PDF: {self.pdf_path}")

        # Extract all pages
        pages_text = self.extract_all_pages()
        if not pages_text:
            return []

        # Find page range to process
        start_page, end_page = self.find_id_range(pages_text)

        if start_page is None:
            print("Start page (1.1.1) not found, processing entire document")
            start_page = 0
        if end_page is None:
            print("End page not found, processing until the end")
            end_page = len(pages_text) - 1

        print(f"Processing pages {start_page + 1} to {end_page + 1}")

        # Combine text from selected pages
        combined_text = ""
        for page_num in range(start_page, end_page + 1):
            combined_text += f"\n=== PAGE {page_num + 1} ===\n" + pages_text[page_num]

        # Clean text
        cleaned_text = self.clean_text(combined_text)

        # Preprocessing: Merge sections with (suite)
        preprocessed_text = self.merge_suite_sections(cleaned_text)

        # Parse structured data
        requirements_data = self.parse_requirements_data(preprocessed_text)

        return requirements_data

    def export_to_csv(self, requirements_data: List[Dict], output_file: str):
        """Exports structured data to CSV file"""
        if not requirements_data:
            print("No data to export")
            return

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'text', 'tests', 'guidance']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write header
                writer.writeheader()

                # Write data
                for requirement in requirements_data:
                    writer.writerow({
                        'id': requirement['id'],
                        'text': requirement['text'],
                        'tests': requirement['tests'],
                        'guidance': requirement['guidance']
                    })

            print(f"Data exported to: {output_file}")

        except Exception as e:
            print(f"Error during CSV export: {e}")

def main():
    # Check if a PDF file path was provided as argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found: {pdf_path}")
            return
        pdf_files = [os.path.basename(pdf_path)]
        pdf_folder = os.path.dirname(pdf_path) if os.path.dirname(pdf_path) else "."
    else:
        # Default behavior: use current folder
        pdf_folder = "."
        pdf_files = ['PCI-DSS-v4-0-1-SAQ-D-Merchant-FR.pdf']

    if not pdf_files:
        print("No PDF files found in specified folder")
        return

    print(f"PDF files found: {pdf_files}")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        # Write CSV to the same directory as the input PDF
        output_csv = os.path.join(pdf_folder, pdf_file.replace('.pdf', '_structured.csv'))

        print(f"\nProcessing: {pdf_file}")

        extractor = PDFExtractor(pdf_path)
        requirements_data = extractor.process_pdf()

        if requirements_data:
            extractor.export_to_csv(requirements_data, output_csv)
            print(f"[OK] {len(requirements_data)} requirements extracted and saved in {output_csv}")
        else:
            print("[ERROR] No data extracted")

    sys.exit(0)  # Explicitly exit with success code

if __name__ == "__main__":
    main()