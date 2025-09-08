import click
import subprocess
import sys
import os
import time
import logging
import hashlib
import json
import io
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from cli.auth import get_authenticated_user, load_config, save_config

# Add local_model to path for offline functionality
LOCAL_MODEL_PATH = Path(__file__).parent.parent / "local_model"
sys.path.insert(0, str(LOCAL_MODEL_PATH))

try:
    from offline_test_generator import OfflineTestGenerator
    from .utils import read_file_content, detect_language, write_file_content
    OFFLINE_AVAILABLE = True
except ImportError as e:
    click.echo(f"⚠️  Offline functionality not available: {e}")
    OFFLINE_AVAILABLE = False

# Configure logging for offline operations
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_premium_status() -> bool:
    """Check if user has premium access (offline validation with hashed storage)"""
    try:
        # Get user info from auth
        user = get_authenticated_user()
        print("USER: ", user)
        if not user:
            return False
        
        # Check if user has premium plan
        user_plan = user.get('plan', 'free')
        if user_plan == 'free':
            return False
        
        # Get premium end date
        # premium_end_date = user.get('premium_end_date')
        # if not premium_end_date:
        #     return False
        
        # Check if premium is still valid
        # try:
        #     end_date = datetime.fromisoformat(premium_end_date.replace('Z', '+00:00'))
        #     if datetime.now() > end_date:
        #         print("plan has expired")
        #         return False
        # except:
        #     print("what?")
        #     return False
        
        # Store hashed premium info locally for offline validation
        # config = load_config()
        # premium_hash = hashlib.sha256(f"{user.get('user_id')}{premium_end_date}{user_plan}".encode()).hexdigest()
        # config['offline_premium_hash'] = premium_hash
        # config['offline_premium_end'] = premium_end_date
        # save_config(config)
        
        return True
        
    except Exception as e:
        # Fallback to offline validation if online check fails
        return check_offline_premium_status()

def check_offline_premium_status() -> bool:
    """Check premium status using locally stored hashed data"""
    try:
        config = load_config()
        
        # Check if we have stored premium info
        if 'offline_premium_hash' not in config or 'offline_premium_end' not in config:
            return False
        
        # Check if premium has expired
        premium_end = config['offline_premium_end']
        try:
            end_date = datetime.fromisoformat(premium_end.replace('Z', '+00:00'))
            if datetime.now() > end_date:
                # Clear expired premium info
                del config['offline_premium_hash']
                del config['offline_premium_end']
                save_config(config)
                return False
        except:
            return False
        
        return True
        
    except Exception:
        return False

@click.group()
def offline():
    """Offline mode - Generate tests using local model"""
    pass

@offline.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--positive', '-p', default=2, help='Number of positive test cases (default: 2)')
@click.option('--negative', '-n', default=1, help='Number of negative test cases (default: 1)')
@click.option('--framework', '-f', default='pytest', help='Testing framework (pytest, unittest)')
@click.option('--language', '-l', default=None, help='Programming language (auto-detected if not specified)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--timeout', '-t', default=180, help='Timeout in seconds (default: 180)')
def generate(file_path, positive, negative, framework, language, output, timeout):
    """Generate test cases for a file using local StarCoder2 model"""
    
    if not OFFLINE_AVAILABLE:
        click.echo("❌ Offline functionality not available")
        return
    
    # Check premium status
    if not check_premium_status():
        click.echo("❌ Offline mode is only available for premium users.")
        click.echo("If you are on the Free plan, this feature is not accessible.")
        click.echo("To upgrade your plan, please visit: https://thetestgenie.com/pricing")
        return
    
    # Validate input
    if positive < 0 or positive > 8:
        click.echo("❌ Positive test cases must be between 0 and 8")
        return
    
    if negative < 0 or negative > 8:
        click.echo("❌ Negative test cases must be between 0 and 8")
        return
    
    # Auto-detect language if not specified
    if not language:
        language = detect_language(file_path)
        click.echo(f"🔍 Auto-detected language: {language}")
    
    if language not in {"python", "cpp"}:
        click.echo(f"❌ Error: {language} is not supported in offline mode yet.\nSupported languages: python, cpp")
        return
    
    click.echo(f"🚀 TestGenie Offline - Generating tests for {file_path}")
    click.echo(f"📊 Parameters: {positive} positive, {negative} negative test cases")
    click.echo("=" * 60)
    
    # Setup logging to file (hide model output from user)
    log_file = Path.home() / ".testgenie" / "offline_generation.log"
    log_file.parent.mkdir(exist_ok=True)
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure file logging
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Add file handler to root logger
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)
    
    # Suppress all console output from StarCoder2_3B modules
    logging.getLogger('RuntimeInstaller').setLevel(logging.CRITICAL)
    logging.getLogger('ModelDownloader').setLevel(logging.CRITICAL)
    logging.getLogger('GGUFServer').setLevel(logging.CRITICAL)
    logging.getLogger('PromptHandler').setLevel(logging.CRITICAL)
    logging.getLogger('ResourceManager').setLevel(logging.CRITICAL)
    logging.getLogger('ResourceMonitor').setLevel(logging.CRITICAL)
    logging.getLogger('ProcessManager').setLevel(logging.CRITICAL)
    logging.getLogger('MemoryManager').setLevel(logging.CRITICAL)
    logging.getLogger('OfflineTestGenerator').setLevel(logging.CRITICAL)
    
    # Show loading indicator
    click.echo("🔄 Generating test cases... (This may take a few minutes)")
    click.echo("📝 Detailed logs are being saved to: ~/.testgenie/offline_generation.log")
    
    try:
        # Initialize offline test generator with correct model path
        models_dir = str(LOCAL_MODEL_PATH / "models")
        
        # Redirect all output to log file during generation
        with open(log_file, 'a') as log_f:
            with redirect_stdout(log_f), redirect_stderr(log_f):
                generator = OfflineTestGenerator(models_dir=models_dir)
                
                # Generate test cases
                start_time = time.time()
                success = generator.generate_tests_for_file(
                    file_path=file_path,
                    positive=positive,
                    negative=negative
                )
                
                end_time = time.time()
        
        # Process results outside the redirect context
        if success:
            # Get the generated test file path
            input_path = Path(file_path)
            test_file_path = input_path.parent / f"test_{input_path.stem}{input_path.suffix}"
            
            # Post-process the test file with proper imports and main function (like online)
            if test_file_path.exists():
                processed_test_file = save_test_file(
                    file_path=file_path,
                    test_content=read_file_content(str(test_file_path)),
                    language=language,
                    framework=framework,
                    positive_cases=positive,
                    negative_cases=negative,
                    output_path=str(test_file_path)
                )
                
                click.echo("=" * 60)
                click.echo(f"✅ Success! Test file generated: {processed_test_file}")
                click.echo(f"⏱️  Total time: {end_time - start_time:.2f} seconds")
                click.echo(f"🧪 You can run the tests with: python -m pytest {processed_test_file}")
                click.echo(f"📝 Detailed generation logs: ~/.testgenie/offline_generation.log")
            else:
                click.echo("❌ Test file was not created")
        else:
            click.echo("❌ Failed to generate test cases")
            
    except Exception as e:
        click.echo(f"❌ Error during test generation: {e}")
        click.echo(f"📝 Check detailed logs: ~/.testgenie/offline_generation.log")
        logging.exception("Test generation failed")
    finally:
        # Remove file handler to prevent duplicate logs
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)
                handler.close()

@offline.command()
def install():
    """Install model and dependencies"""
    click.echo("Installing model and dependencies...")
    
    if not OFFLINE_AVAILABLE:
        click.echo("❌ Offline functionality not available. Please check model installation.")
        return
    
    try:
        # Add local_model to path for imports
        sys.path.insert(0, str(LOCAL_MODEL_PATH))
        from model_downloader import ModelDownloader
        from runtime_installer import RuntimeInstaller
        
        # Install runtime dependencies
        installer = RuntimeInstaller()
        if installer.install_all():
            click.echo("✅ Runtime dependencies installed successfully")
        else:
            click.echo("❌ Failed to install runtime dependencies")
            return
        
        # Download model
        models_dir = str(LOCAL_MODEL_PATH / "models")
        downloader = ModelDownloader(models_dir)
        model_url = "https://drive.google.com/file/d/1Pdmqn3AqXdlaZyj7iPVCAcRVHP3n9Eht/view?usp=sharing"
        
        if downloader.download_model(model_url):
            click.echo("✅ Model downloaded successfully")
        else:
            click.echo("❌ Failed to download model")
            return
            
        click.echo("✅ Installation completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Installation failed: {e}")
        logging.exception("Installation failed")

@offline.command()
@click.option('--port', '-p', default=8123, help='Port to start server on (default: 8123)')
@click.option('--timeout', '-t', default=300, help='Server timeout in seconds (default: 300)')
def start(port, timeout):
    """Start the model server"""
    click.echo(f"Starting model server on port {port}...")
    
    if not OFFLINE_AVAILABLE:
        click.echo("❌ Offline functionality not available. Please check model installation.")
        return
    
    try:
        # Add local_model to path for imports
        sys.path.insert(0, str(LOCAL_MODEL_PATH))
        from server_manager import GGUFServer
        
        server = GGUFServer(model_path="models/model.gguf", port=port)
        
        if server.start():
            click.echo(f"✅ Server started successfully on port {port}")
            click.echo("Press Ctrl+C to stop the server")
            
            try:
                # Keep server running
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                click.echo("\n🛑 Stopping server...")
                server.stop()
                click.echo("✅ Server stopped")
        else:
            click.echo("❌ Failed to start server")
            
    except Exception as e:
        click.echo(f"❌ Server startup failed: {e}")
        logging.exception("Server startup failed")

def save_test_file(file_path: str, test_content: str, language: str, framework: str, positive_cases: int, negative_cases: int, output_path: Optional[str] = None) -> str:
    """Save the generated test content to a file (exactly like online implementation)"""
    if not output_path:
        # Generate output filename based on input file
        input_path = Path(file_path)

    # Add imports and main execution based on language and framework
    if language == 'python':
        if framework == 'pytest':
            # For pytest, just add the test content
            import_statement = f"from {Path(file_path).stem} import *\n\n"
            full_content = import_statement + test_content
            test_execution = "\n# Run all test cases\n"
            for i in range(1, positive_cases + 1):
                test_execution += f"test_positive_case_{i}()\n"
            for i in range(1, negative_cases + 1):
                test_execution += f"test_negative_case_{i}()\n"
            test_execution += f"print('ALL TEST CASES PASSED!')"
            full_content = full_content + test_execution
        elif framework == 'unittest':
            # For unittest, add proper class structure
            import_statement = f"import unittest\nfrom {Path(file_path).stem} import *\n\n"
            class_start = "class TestSuite(unittest.TestCase):\n"
            class_end = "\n\nif __name__ == '__main__':\n    unittest.main()\n"
            # Indent the test content for unittest class
            indented_content = "\n".join("    " + line if line.strip() else line for line in test_content.split('\n'))
            full_content = import_statement + class_start + indented_content + class_end

    elif language == 'cpp':
        # Include the original C++ file header
        original_file_name = Path(file_path).name
        includes = f"#include <iostream>\n#include <exception>\n#include \"{original_file_name}\"\n\n"
        if framework == 'gtest':
            # For gtest, add proper includes
            gtest_includes = f"#include <gtest/gtest.h>\n\n#include \"{original_file_name}\"\n\n"
            full_content = gtest_includes + test_content
        else:
            # Default format
            main_function = "\nint main() {\n    std::cout << \"Running all test cases...\\n\";\n"
            # Call all test cases based on user input
            for i in range(1, positive_cases + 1):
                main_function += f"    positive_test_case_{i}();\n"
            for i in range(1, negative_cases + 1):
                main_function += f"    negative_test_case_{i}();\n"
            main_function += "    return 0;\n}\n"
            full_content = includes + test_content + main_function

    else:
        full_content = test_content

    if output_path is None:
        # Generate output path based on input file
        input_path = Path(file_path)
        if input_path.suffix:
            output_path = input_path.parent / f"test_{input_path.stem}{input_path.suffix}"
        else:
            output_path = input_path.parent / f"test_{input_path.name}"

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        click.echo(f"✅ Test file generated successfully: {output_path}")
        return str(output_path)
    except Exception as e:
        click.echo(f"❌ Error saving test file: {e}")
        return ""

def post_process_test_file(test_file_path: str, source_file_path: str, language: str, framework: str, positive_cases: int, negative_cases: int, output_path: Optional[str] = None) -> str:
    """Post-process the generated test file with proper imports and structure"""
    
    try:
        # Read the generated test content
        test_content = read_file_content(test_file_path)
        
        # Apply post-processing based on language and framework
        if language == 'python':
            if framework == 'pytest':
                # Ensure pytest import and proper structure
                if "import pytest" not in test_content:
                    test_content = "import pytest\n" + test_content
                
                # Add dynamic import for source file
                source_filename = Path(source_file_path).stem
                import_statement = f"import sys\nimport os\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nfrom {source_filename} import *\n\n"
                
                if not test_content.startswith(import_statement):
                    test_content = import_statement + test_content
                    
            elif framework == 'unittest':
                # Ensure unittest import and proper class structure
                if "import unittest" not in test_content:
                    test_content = "import unittest\n" + test_content
                
                # Add dynamic import for source file
                source_filename = Path(source_file_path).stem
                import_statement = f"import sys\nimport os\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nfrom {source_filename} import *\n\n"
                
                if not test_content.startswith(import_statement):
                    test_content = import_statement + test_content
                
                # Ensure proper unittest class structure
                if "class TestSuite(unittest.TestCase):" not in test_content:
                    if "class TestSuite" in test_content:
                        test_content = test_content.replace("class TestSuite", "class TestSuite(unittest.TestCase)")
                    else:
                        # Wrap content in unittest class
                        class_start = "class TestSuite(unittest.TestCase):\n"
                        class_end = "\n\nif __name__ == '__main__':\n    unittest.main()\n"
                        indented_content = "\n".join("    " + line if line.strip() else line for line in test_content.split('\n'))
                        test_content = class_start + indented_content + class_end
        
        elif language == 'cpp':
            # Add proper includes for C++
            original_file_name = Path(source_file_path).name
            includes = f"#include <iostream>\n#include <exception>\n#include \"{original_file_name}\"\n\n"
            
            if not test_content.startswith(includes):
                test_content = includes + test_content
            
            # Add main function if not present
            if "int main()" not in test_content:
                main_function = "\nint main() {\n    std::cout << \"Running all test cases...\\n\";\n"
                for i in range(1, positive_cases + 1):
                    main_function += f"    positive_test_case_{i}();\n"
                for i in range(1, negative_cases + 1):
                    main_function += f"    negative_test_case_{i}();\n"
                main_function += "    return 0;\n}\n"
                test_content += main_function
        
        # Write the processed content back
        write_file_content(test_file_path, test_content)
        
        return test_file_path
        
    except Exception as e:
        click.echo(f"⚠️  Warning: Post-processing failed: {e}")
        return test_file_path 