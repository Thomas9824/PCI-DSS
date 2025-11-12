from flask import Flask, render_template, request, jsonify, send_from_directory
import webbrowser
import threading
import time
import os
import sys

# Configuration Flask pour PyInstaller
if getattr(sys, 'frozen', False):
    # Application packagée avec PyInstaller
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    # Mode développement
    template_folder = 'templates'
    static_folder = 'templates'
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

@app.route('/test')
def test():
    return "Flask works!"

# Routes pour servir les fichiers statiques
@app.route('/<path:filename>')
def serve_static(filename):
    """Sert les fichiers CSS, JS et autres fichiers statiques"""
    # Exclure les routes spéciales
    if filename in ['test', 'info', 'api']:
        return "Route not found", 404
    
    if getattr(sys, 'frozen', False):
        static_dir = os.path.join(sys._MEIPASS, 'templates')
    else:
        static_dir = 'templates'
    
    # Vérifier si le fichier existe
    file_path = os.path.join(static_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(static_dir, filename)
    else:
        return "File not found", 404

@app.route('/converter/<path:filename>')
def serve_converter_static(filename):
    """Sert les fichiers du dossier converter"""
    if getattr(sys, 'frozen', False):
        static_dir = os.path.join(sys._MEIPASS, 'templates', 'converter')
    else:
        static_dir = os.path.join('templates', 'converter')
    
    file_path = os.path.join(static_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(static_dir, filename)
    else:
        return "File not found", 404

@app.route('/converter2/<path:filename>')
def serve_converter2_static(filename):
    """Sert les fichiers du dossier converter2"""
    if getattr(sys, 'frozen', False):
        static_dir = os.path.join(sys._MEIPASS, 'templates', 'converter2')
    else:
        static_dir = os.path.join('templates', 'converter2')
    
    file_path = os.path.join(static_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(static_dir, filename)
    else:
        return "File not found", 404

@app.route('/change/<path:filename>')
def serve_change_static(filename):
    """Sert les fichiers du dossier change"""
    if getattr(sys, 'frozen', False):
        static_dir = os.path.join(sys._MEIPASS, 'templates', 'change')
    else:
        static_dir = os.path.join('templates', 'change')
    
    file_path = os.path.join(static_dir, filename)
    if os.path.exists(file_path):
        return send_from_directory(static_dir, filename)
    else:
        return "File not found", 404

@app.route('/info')
def info():
    return f"""
    Current directory: {os.getcwd()}<br>
    Templates folder: {app.template_folder}<br>
    Templates exist: {os.path.exists('templates')}<br>
    Files in templates: {os.listdir('templates') if os.path.exists('templates') else 'No templates folder'}<br>
    Frozen: {getattr(sys, 'frozen', False)}<br>
    """

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Template Error: {str(e)}<br>Template folder: {app.template_folder}<br>Frozen: {getattr(sys, 'frozen', False)}"

@app.route('/change')
def change_page():
    try:
        return render_template('change/index.html')
    except Exception as e:
        return f"Template Error: {str(e)}<br>Template folder: {app.template_folder}<br>Frozen: {getattr(sys, 'frozen', False)}"

@app.route('/historic')
def historic_page():
    try:
        return render_template('change/historic.html')
    except Exception as e:
        return f"Template Error: {str(e)}<br>Template folder: {app.template_folder}<br>Frozen: {getattr(sys, 'frozen', False)}"

@app.route('/converter2')
def converter2_page():
    try:
        return render_template('converter2/index.html')
    except Exception as e:
        return f"Template Error: {str(e)}<br>Template folder: {app.template_folder}<br>Frozen: {getattr(sys, 'frozen', False)}"

@app.route('/api/process', methods=['POST'])
def process_data():
    data = request.json
    # Votre code Python ici
    result = f"Traité: {data.get('input', '')}"
    return jsonify({'result': result})

def check_and_install_dependencies():
    """Check if scraper dependencies are installed and install if missing"""
    import subprocess
    from pathlib import Path
    
    required_packages = ['selenium', 'webdriver-manager', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {missing_packages}")
        print("Installing missing dependencies...")
        
        # Install missing packages
        for package in missing_packages:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print(f"✅ Successfully installed {package}")
                else:
                    print(f"❌ Failed to install {package}: {result.stderr}")
                    return False, f"Failed to install {package}: {result.stderr}"
            except Exception as e:
                print(f"❌ Error installing {package}: {e}")
                return False, f"Error installing {package}: {e}"
    
    return True, "All dependencies are installed"

# Global variable to track scraper status
scraper_status = {
    'running': False,
    'progress': '',
    'completed': False,
    'error': None
}

# Global variable to store PDF extraction results paths
pdf_extraction_results = {}

def cleanup_old_temp_files():
    """Clean up temporary CSV files older than 1 hour"""
    import tempfile
    import time
    from pathlib import Path
    
    temp_dir = Path(tempfile.gettempdir())
    current_time = time.time()
    
    # Find and delete old CSV files
    for csv_file in temp_dir.glob('pci_upload_*_structured.csv'):
        try:
            # Check if file is older than 1 hour (3600 seconds)
            if current_time - csv_file.stat().st_mtime > 3600:
                csv_file.unlink()
                print(f"Cleaned up old temp file: {csv_file}")
        except Exception as e:
            print(f"Error cleaning up {csv_file}: {e}")

@app.route('/api/run-scraper', methods=['POST'])
def run_scraper():
    """Execute the PCI document scraper in the background"""
    import subprocess
    import logging
    from pathlib import Path

    try:
        # Check if scraper is already running
        if scraper_status['running']:
            return jsonify({
                'success': False,
                'error': 'Scraper is already running'
            }), 409

        # First check and install dependencies
        deps_ok, deps_msg = check_and_install_dependencies()
        if not deps_ok:
            return jsonify({
                'success': False,
                'error': f'Dependency installation failed: {deps_msg}'
            }), 500

        # Get the path to the scraper script
        scraper_path = Path(__file__).parent / 'pci_change_scraper' / 'pci_scraper.py'

        print(f"Looking for scraper at: {scraper_path}")

        if not scraper_path.exists():
            return jsonify({
                'success': False,
                'error': f'Scraper script not found at {scraper_path}'
            }), 404

        # Reset status
        scraper_status['running'] = True
        scraper_status['progress'] = 'Starting scraper...'
        scraper_status['completed'] = False
        scraper_status['error'] = None

        # Start scraper in background thread
        scraper_dir = scraper_path.parent

        def run_scraper_thread():
            """Background thread to run the scraper"""
            original_cwd = os.getcwd()
            try:
                os.chdir(scraper_dir)
                cmd = [sys.executable, str(scraper_path.name)]
                print(f"Executing command: {' '.join(cmd)}")

                # Use Popen for non-blocking execution
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                # Stream output in real-time
                scraper_status['progress'] = 'Scraper running...'

                stdout, stderr = process.communicate(timeout=300)

                if process.returncode == 0:
                    scraper_status['completed'] = True
                    scraper_status['progress'] = 'Scraper completed successfully'
                    print(f"Scraper completed: {stdout[:200]}")
                else:
                    scraper_status['error'] = f'Scraper failed: {stderr[:500]}'
                    scraper_status['progress'] = 'Scraper failed'
                    print(f"Scraper failed: {stderr[:200]}")

            except subprocess.TimeoutExpired:
                scraper_status['error'] = 'Scraper timed out (5 minutes)'
                scraper_status['progress'] = 'Scraper timed out'
            except Exception as e:
                scraper_status['error'] = str(e)
                scraper_status['progress'] = f'Error: {str(e)}'
                print(f"Exception in scraper thread: {e}")
            finally:
                scraper_status['running'] = False
                os.chdir(original_cwd)

        # Start background thread
        thread = threading.Thread(target=run_scraper_thread, daemon=True)
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Scraper started in background',
            'status': 'running'
        })

    except Exception as e:
        scraper_status['running'] = False
        scraper_status['error'] = str(e)
        print(f"Exception in run_scraper: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scraper-status')
def get_scraper_status():
    """Get the current status of the scraper"""
    return jsonify({
        'running': scraper_status['running'],
        'progress': scraper_status['progress'],
        'completed': scraper_status['completed'],
        'error': scraper_status['error']
    })

@app.route('/api/changes')
def get_changes():
    """Get the detected changes from the scraper"""
    from pathlib import Path
    import json

    try:
        changes_file = Path(__file__).parent / 'pci_change_scraper' / 'changes.json'

        if not changes_file.exists():
            return jsonify({
                'success': True,
                'changes': {
                    'new_documents': [],
                    'updated_versions': [],
                    'removed_documents': [],
                    'unchanged_documents': []
                }
            })

        with open(changes_file, 'r', encoding='utf-8') as f:
            changes = json.load(f)

        return jsonify({
            'success': True,
            'changes': changes
        })

    except Exception as e:
        print(f"Error loading changes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/documents')
def get_documents():
    """Serve the CSV data as JSON"""
    from pathlib import Path
    try:
        csv_path = Path(__file__).parent / 'pci_change_scraper' / 'pci_documents.csv'

        if not csv_path.exists():
            return jsonify({
                'success': True,
                'documents': [],
                'count': 0,
                'message': 'No documents found. CSV file will be created after first successful scraping.'
            })

        import pandas as pd
        df = pd.read_csv(csv_path)
        documents = df.to_dict('records')

        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })

    except Exception as e:
        print(f"Error in get_documents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/historic')
def get_historic():
    """Get the historic changes data"""
    from pathlib import Path
    import json

    try:
        historic_file = Path(__file__).parent / 'pci_change_scraper' / 'historic.json'

        if not historic_file.exists():
            return jsonify({
                'success': True,
                'historic': []
            })

        with open(historic_file, 'r', encoding='utf-8') as f:
            historic = json.load(f)

        return jsonify({
            'success': True,
            'historic': historic
        })

    except Exception as e:
        print(f"Error loading historic: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run-pdf-extractor', methods=['POST'])
def run_pdf_extractor():
    """Execute the PCI PDF extractor with language selection and optional file upload"""
    import subprocess
    from pathlib import Path
    import tempfile
    
    # Clean up old temporary files before processing
    cleanup_old_temp_files()
    
    try:
        # Check if this is a file upload or JSON request
        if 'file' in request.files:
            # Handle file upload
            uploaded_file = request.files['file']
            language = request.form.get('language', 'EN').upper()
            
            if uploaded_file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            if not uploaded_file.filename.lower().endswith('.pdf'):
                return jsonify({
                    'success': False,
                    'error': 'Please upload a PDF file'
                }), 400
                
        else:
            # Handle JSON request (no file upload)
            data = request.json or {}
            language = data.get('language', 'EN').upper()
            uploaded_file = None
        
        # Validate language - only EN and FR supported
        valid_languages = ['EN', 'FR']
        if language not in valid_languages:
            return jsonify({
                'success': False,
                'error': f'Invalid language. Supported: {", ".join(valid_languages)}'
            }), 400
        
        # Get the path to the new PDF extractor script
        script_name = f"pdf_extractor_{language}.py"
        extractor_path = Path(__file__).parent / 'new_pci_pdf_extractor' / script_name
        
        print(f"Looking for PDF extractor at: {extractor_path}")
        
        if not extractor_path.exists():
            return jsonify({
                'success': False,
                'error': f'PDF extractor script not found: {script_name}'
            }), 404
        
        # Change to the extractor directory
        extractor_dir = extractor_path.parent
        original_cwd = os.getcwd()
        temp_file_path = None
        
        try:
            os.chdir(extractor_dir)
            print(f"Changed to directory: {os.getcwd()}")
            
            # Check if dependencies are installed
            deps_ok, deps_msg = check_pdf_extractor_dependencies()
            if not deps_ok:
                return jsonify({
                    'success': False,
                    'error': f'Dependencies missing: {deps_msg}'
                }), 500
            
            # If file uploaded, save it temporarily
            cmd = [sys.executable, str(extractor_path.name)]
            csv_file = None
            
            if uploaded_file:
                # Save uploaded file to system temporary directory
                import tempfile
                temp_fd, temp_path_str = tempfile.mkstemp(suffix='.pdf', prefix=f'pci_upload_{language}_')
                os.close(temp_fd)  # Close the file descriptor
                temp_file_path = Path(temp_path_str)
                
                uploaded_file.save(str(temp_file_path))
                print(f"Saved uploaded file to: {temp_file_path}")
                
                # Add file path as argument to the script
                cmd.append(str(temp_file_path))
                
                # Expected output CSV file name (in current working directory)
                csv_file = temp_file_path.stem + '_structured.csv'
            else:
                # Default pattern for files in the directory
                csv_file = f"PCI-DSS-v4-0-1-SAQ-D-Merchant-{language if language == 'EN' else ''}_structured.csv".replace('--', '-')
            
            print(f"Executing command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )
            
            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout[:500]}...")
            print(f"Stderr: {result.stderr[:500]}...")
            
            if result.returncode == 0:
                # Check for output files from new extractors
                output_files = []
                
                if uploaded_file and temp_file_path:
                    # For uploaded files, CSV is in the temp directory
                    temp_csv = temp_file_path.parent / csv_file
                    if temp_csv.exists():
                        # Store the CSV path in global variable for later retrieval
                        # Don't delete the temp CSV yet - we need it for download/display
                        pdf_extraction_results[language] = str(temp_csv)
                        output_files.append(csv_file)
                        print(f"Found output CSV: {temp_csv}")
                        print(f"Stored in memory for language: {language}")
                elif csv_file and os.path.exists(csv_file):
                    output_files.append(csv_file)
                    print(f"Found output CSV: {csv_file}")
                
                return jsonify({
                    'success': True,
                    'message': f'PDF extractor ({language}) executed successfully',
                    'output': result.stdout,
                    'errors': result.stderr if result.stderr else None,
                    'language': language,
                    'output_files': output_files
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'PDF extractor failed with return code {result.returncode}',
                    'output': result.stdout,
                    'errors': result.stderr
                }), 500
                
        finally:
            # Clean up temporary PDF file (but keep CSV for later retrieval)
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                    print(f"Cleaned up temporary PDF: {temp_file_path}")
                except Exception as e:
                    print(f"Failed to clean up temporary PDF: {e}")
            
            os.chdir(original_cwd)
            
    except subprocess.TimeoutExpired:
        print("PDF extractor timed out")
        return jsonify({
            'success': False,
            'error': 'PDF extractor execution timed out (2 minutes)'
        }), 408
        
    except Exception as e:
        print(f"Exception in run_pdf_extractor: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def check_pdf_extractor_dependencies():
    """Check if PDF extractor dependencies are installed"""
    import subprocess
    
    required_packages = ['PyPDF2']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {missing_packages}")
        print("Installing missing dependencies...")
        
        for package in missing_packages:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"✅ Successfully installed {package}")
                else:
                    print(f"❌ Failed to install {package}: {result.stderr}")
                    return False, f"Failed to install {package}: {result.stderr}"
            except Exception as e:
                print(f"❌ Error installing {package}: {e}")
                return False, f"Error installing {package}: {e}"
    
    return True, "All dependencies are installed"

@app.route('/api/pdf-extractor-results/<language>')
def get_pdf_extractor_results(language):
    """Get the results from PDF extractor"""
    from pathlib import Path

    try:
        language = language.upper()
        valid_languages = ['EN', 'FR']

        if language not in valid_languages:
            return jsonify({
                'success': False,
                'error': f'Invalid language. Supported: {", ".join(valid_languages)}'
            }), 400
        
        # Check if we have a stored result for this language
        if language in pdf_extraction_results:
            csv_file_path = pdf_extraction_results[language]
            csv_file = Path(csv_file_path)
            
            if not csv_file.exists():
                # File was deleted, remove from cache
                del pdf_extraction_results[language]
                return jsonify({
                    'success': False,
                    'error': f'Results file not found. Please run the extractor again.',
                    'language': language
                }), 404
        else:
            # Fallback: look in extractor directory for existing files
            extractor_dir = Path(__file__).parent / 'new_pci_pdf_extractor'
            csv_files = []
            
            if extractor_dir.exists():
                csv_files = list(extractor_dir.glob(f"*{language}*_structured.csv"))
                if not csv_files:
                    csv_files = list(extractor_dir.glob("*_structured.csv"))
            
            if csv_files:
                csv_file = max(csv_files, key=lambda p: p.stat().st_mtime)
            else:
                return jsonify({
                    'success': False,
                    'error': f'No results found for language {language}. Please run the extractor first.',
                    'language': language
                }), 404
        
        if csv_file:
            
            import pandas as pd
            import numpy as np
            df = pd.read_csv(csv_file)
            # Replace NaN values with empty strings to avoid JSON serialization issues
            df = df.replace({np.nan: '', 'NaN': '', 'nan': ''})
            
            # Rename 'id' column to 'req_num' if it exists for frontend compatibility
            if 'id' in df.columns:
                df = df.rename(columns={'id': 'req_num'})
            
            requirements = df.to_dict('records')

            return jsonify({
                'success': True,
                'requirements': requirements,
                'count': len(requirements),
                'language': language,
                'format': 'csv'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No results found for language {language}. Please run the extractor first.',
                'language': language
            }), 404
            
    except Exception as e:
        print(f"Error in get_pdf_extractor_results: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download-pdf-results/<language>/<format>')
def download_pdf_results(language, format):
    """Download the PDF extractor results as CSV or JSON"""
    from pathlib import Path

    try:
        language = language.upper()
        format = format.lower()

        if format not in ['csv']:
            return "Invalid format. Only 'csv' is supported.", 400

        # Check if we have a stored result for this language
        if language in pdf_extraction_results:
            file_path = Path(pdf_extraction_results[language])

            if not file_path.exists():
                # File was deleted, remove from cache
                del pdf_extraction_results[language]
                return f"Results file not found for language {language}. Please run the extractor again.", 404
        else:
            # Fallback: look in extractor directory
            extractor_dir = Path(__file__).parent / 'new_pci_pdf_extractor'
            csv_files = []

            if extractor_dir.exists():
                csv_files = list(extractor_dir.glob(f"*{language}*_structured.csv"))
                if not csv_files:
                    csv_files = list(extractor_dir.glob("*_structured.csv"))

            if not csv_files:
                return f"No CSV file found for language {language}", 404

            file_path = max(csv_files, key=lambda p: p.stat().st_mtime)

        download_name = f"pci_requirements_{language}.csv"

        return send_from_directory(
            file_path.parent,
            file_path.name,
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        print(f"Error in download_pdf_results: {e}")
        return f"Error: {str(e)}", 500

@app.route('/api/compare-requirements/<language>', methods=['POST'])
def compare_requirements(language):
    """Compare current requirements with stored reference"""
    from pathlib import Path
    import sys
    import tempfile
    import pandas as pd

    try:
        language = language.upper()

        # Import the comparator
        comparator_path = Path(__file__).parent / 'pci_compare'
        if str(comparator_path) not in sys.path:
            sys.path.insert(0, str(comparator_path))

        from compare_requirements import RequirementsComparator

        comparator = RequirementsComparator()

        # Check if current requirements data was sent in the request body
        data = request.get_json()

        if data and 'current_requirements' in data:
            # Use the provided current requirements (including edits)
            current_reqs = data['current_requirements']

            # Create a temporary CSV file with the current data
            temp_fd, temp_csv_path = tempfile.mkstemp(suffix='.csv', prefix=f'compare_temp_{language}_')
            os.close(temp_fd)

            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(current_reqs)

            # Ensure we have the right column name
            if 'req_num' in df.columns and 'id' not in df.columns:
                df = df.rename(columns={'req_num': 'id'})

            df.to_csv(temp_csv_path, index=False)

            current_csv = Path(temp_csv_path)
            cleanup_temp = True
        else:
            # Fallback to original behavior - use stored CSV file
            cleanup_temp = False
            current_csv = None

            # Check if we have a stored result for this language
            if language in pdf_extraction_results:
                current_csv = Path(pdf_extraction_results[language])

                if not current_csv.exists():
                    del pdf_extraction_results[language]
                    return jsonify({
                        'success': False,
                        'error': f'Current results file not found. Please run the extractor first.'
                    }), 404
            else:
                # Fallback: look in extractor directory
                extractor_dir = Path(__file__).parent / 'new_pci_pdf_extractor'
                csv_files = []

                if extractor_dir.exists():
                    csv_files = list(extractor_dir.glob(f"*{language}*_structured.csv"))
                    if not csv_files:
                        csv_files = list(extractor_dir.glob("*_structured.csv"))

                if csv_files:
                    current_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
                else:
                    return jsonify({
                        'success': False,
                        'error': f'No current results found for language {language}'
                    }), 404

        # Perform comparison
        result = comparator.compare(str(current_csv), language)

        # Clean up temporary file if created
        if cleanup_temp and current_csv.exists():
            try:
                current_csv.unlink()
            except Exception as e:
                print(f"Failed to clean up temp file: {e}")

        return jsonify(result)

    except Exception as e:
        print(f"Error in compare_requirements: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-reference/<language>', methods=['POST'])
def save_reference(language):
    """Save current requirements as reference for future comparisons"""
    from pathlib import Path
    import sys
    import tempfile
    import pandas as pd

    try:
        language = language.upper()

        # Import the comparator
        comparator_path = Path(__file__).parent / 'pci_compare'
        if str(comparator_path) not in sys.path:
            sys.path.insert(0, str(comparator_path))

        from compare_requirements import RequirementsComparator

        comparator = RequirementsComparator()

        # Check if current requirements data was sent in the request body
        data = request.get_json()

        if data and 'current_requirements' in data:
            # Use the provided current requirements (including edits)
            current_reqs = data['current_requirements']

            # Create a temporary CSV file with the current data
            temp_fd, temp_csv_path = tempfile.mkstemp(suffix='.csv', prefix=f'save_ref_temp_{language}_')
            os.close(temp_fd)

            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(current_reqs)

            # Ensure we have the right column name
            if 'req_num' in df.columns and 'id' not in df.columns:
                df = df.rename(columns={'req_num': 'id'})

            df.to_csv(temp_csv_path, index=False)

            current_csv = Path(temp_csv_path)
            cleanup_temp = True
        else:
            # Fallback to original behavior - use stored CSV file
            cleanup_temp = False
            current_csv = None

            # Check if we have a stored result for this language
            if language in pdf_extraction_results:
                current_csv = Path(pdf_extraction_results[language])

                if not current_csv.exists():
                    del pdf_extraction_results[language]
                    return jsonify({
                        'success': False,
                        'error': f'Current results file not found. Please run the extractor first.'
                    }), 404
            else:
                # Fallback: look in extractor directory
                extractor_dir = Path(__file__).parent / 'new_pci_pdf_extractor'
                csv_files = []

                if extractor_dir.exists():
                    csv_files = list(extractor_dir.glob(f"*{language}*_structured.csv"))
                    if not csv_files:
                        csv_files = list(extractor_dir.glob("*_structured.csv"))

                if csv_files:
                    current_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
                else:
                    return jsonify({
                        'success': False,
                        'error': f'No current results found for language {language}'
                    }), 404

        # Save as reference
        result = comparator.save_reference(str(current_csv), language)

        # Clean up temporary file if created
        if cleanup_temp and current_csv.exists():
            try:
                current_csv.unlink()
            except Exception as e:
                print(f"Failed to clean up temp file: {e}")

        return jsonify(result)

    except Exception as e:
        print(f"Error in save_reference: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/import-reference/<language>', methods=['POST'])
def import_reference(language):
    """Import a CSV file as reference for comparisons"""
    from pathlib import Path
    import sys

    try:
        language = language.upper()

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400

        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400

        if not uploaded_file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'Please upload a CSV file'
            }), 400

        # Import the comparator
        comparator_path = Path(__file__).parent / 'pci_compare'
        if str(comparator_path) not in sys.path:
            sys.path.insert(0, str(comparator_path))

        from compare_requirements import RequirementsComparator

        comparator = RequirementsComparator()

        # Save uploaded file temporarily
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(suffix='.csv', prefix=f'import_ref_{language}_')
        os.close(temp_fd)

        try:
            uploaded_file.save(temp_path)

            # Use comparator to save this as the reference
            result = comparator.save_reference(temp_path, language)

            return jsonify(result)

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    print(f"Failed to clean up temp file: {e}")

    except Exception as e:
        print(f"Error in import_reference: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reference-info/<language>')
def get_reference_info(language):
    """Get information about stored reference for a language"""
    from pathlib import Path
    import sys

    try:
        language = language.upper()

        # Import the comparator
        comparator_path = Path(__file__).parent / 'pci_compare'
        if str(comparator_path) not in sys.path:
            sys.path.insert(0, str(comparator_path))

        from compare_requirements import RequirementsComparator

        comparator = RequirementsComparator()

        # Get reference info
        info = comparator.get_reference_info(language)

        return jsonify(info)

    except Exception as e:
        print(f"Error in get_reference_info: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/generate-docx-with-tags', methods=['POST'])
def generate_docx_with_tags():
    """
    Generate a DOCX file with tags based on requirement IDs and language.
    This endpoint orchestrates the complete workflow:
    1. Receives requirement IDs and language from frontend
    2. Downloads DOCX from PCI website
    3. Transforms IDs and replaces form fields with tags
    4. Returns the tagged DOCX file for download
    """
    from pathlib import Path
    import tempfile
    import json

    try:
        # Get request data
        data = request.get_json()
        requirement_ids = data.get('requirement_ids', [])
        language = data.get('language', 'EN').upper()

        if not requirement_ids:
            return jsonify({
                'success': False,
                'error': 'No requirement IDs provided'
            }), 400

        print(f"Received request to generate DOCX with tags")
        print(f"  Language: {language}")
        print(f"  Number of IDs: {len(requirement_ids)}")

        # Add auto-fill directory to path
        auto_fill_path = Path(__file__).parent / 'auto-fill'
        if str(auto_fill_path) not in sys.path:
            sys.path.insert(0, str(auto_fill_path))

        # Import the docx_all module
        import docx_all

        # Create output directory for generated files
        output_dir = Path(__file__).parent / 'output' / 'tagged_docx'
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run the complete workflow
        print("Starting DOCX generation workflow...")
        result = docx_all.generate_docx_with_tags(
            requirement_ids,
            language,
            str(output_dir)
        )

        # Handle tuple return (result_path, stats)
        if isinstance(result, tuple):
            result_path, stats = result
        else:
            # Backward compatibility
            result_path = result
            stats = {
                'total_requirements': len(requirement_ids),
                'tags_found': 0,
                'missing_tags': len(requirement_ids),
                'transformed_variants': 0
            }

        if not result_path or not os.path.exists(result_path):
            return jsonify({
                'success': False,
                'error': 'Failed to generate DOCX with tags',
                'stats': stats
            }), 500

        print(f"Successfully generated DOCX: {result_path}")
        print(f"Statistics: {stats}")

        # Generate download URL
        filename = os.path.basename(result_path)
        download_url = f'/api/download-tagged-docx/{filename}'

        return jsonify({
            'success': True,
            'message': 'DOCX with tags generated successfully',
            'filename': filename,
            'download_url': download_url,
            'file_path': result_path,
            'stats': stats
        })

    except Exception as e:
        print(f"Error in generate_docx_with_tags: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download-tagged-docx/<filename>')
def download_tagged_docx(filename):
    """Download the generated tagged DOCX file"""
    from pathlib import Path

    try:
        output_dir = Path(__file__).parent / 'output' / 'tagged_docx'
        file_path = output_dir / filename

        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        return send_from_directory(
            str(output_dir),
            filename,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"Error in download_tagged_docx: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def check_and_install_all_dependencies_on_startup():
    """
    Install ALL required dependencies at first launch
    Returns True if successful, False otherwise
    """
    import subprocess

    # Liste complète de toutes les dépendances du projet
    all_packages = {
        'flask': 'flask',
        'selenium': 'selenium',
        'webdriver-manager': 'webdriver_manager',
        'pandas': 'pandas',
        'PyPDF2': 'PyPDF2',
        'numpy': 'numpy',
        'python-docx': 'docx',
        'lxml': 'lxml'
    }

    missing = []

    # Vérifier quels packages sont manquants
    print("\n" + "="*60)
    print("VÉRIFICATION DES DÉPENDANCES...")
    print("="*60)

    for pip_name, import_name in all_packages.items():
        try:
            __import__(import_name.replace('-', '_'))
            print(f"✅ {pip_name:<20} [OK]")
        except ImportError:
            missing.append(pip_name)
            print(f"❌ {pip_name:<20} [MANQUANT]")

    # Si des packages manquent, les installer
    if missing:
        print("\n" + "="*60)
        print(f"INSTALLATION DE {len(missing)} PACKAGE(S) MANQUANT(S)")
        print("="*60)
        print(f"Packages à installer : {', '.join(missing)}")
        print("\nCela peut prendre quelques minutes...")
        print("="*60 + "\n")

        for pkg in missing:
            print(f"⏳ Installation de {pkg}...", end=" ", flush=True)
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', pkg, '--quiet'],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print("✅")
                else:
                    print(f"❌\n   Erreur: {result.stderr[:200]}")
                    return False
            except subprocess.TimeoutExpired:
                print("❌ (Timeout)")
                return False
            except Exception as e:
                print(f"❌\n   Erreur: {str(e)[:200]}")
                return False

        print("\n" + "="*60)
        print("✅ TOUTES LES DÉPENDANCES SONT INSTALLÉES!")
        print("="*60 + "\n")
        time.sleep(2)  # Pause pour que l'utilisateur puisse lire
    else:
        print("\n✅ Toutes les dépendances sont déjà installées.\n")
        time.sleep(1)

    return True

def open_browser():
    """Ouvre le navigateur après un délai"""
    time.sleep(1.5)
    webbrowser.open_new('http://localhost:5001/')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("           DÉMARRAGE DE PCITOOLS")
    print("="*60 + "\n")

    # Installer les dépendances au démarrage
    if not check_and_install_all_dependencies_on_startup():
        print("\n❌ ERREUR lors de l'installation des dépendances.")
        print("Vérifiez votre connexion Internet et réessayez.")
        print("\nAppuyez sur Entrée pour quitter...")
        input()
        sys.exit(1)

    print("🚀 Démarrage du serveur Flask sur http://localhost:5001")
    print("📖 Le navigateur va s'ouvrir automatiquement...\n")

    # Ouvrir le navigateur dans un thread séparé
    threading.Timer(1, open_browser).start()

    # Lancer le serveur Flask
    app.run(host='localhost', port=5001, debug=False)