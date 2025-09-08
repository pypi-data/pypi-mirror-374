#!/usr/bin/env python3

import os
import sys
import subprocess
import yaml
import argparse
import shutil
import platform
from pathlib import Path

def find_pac_command():
    """Find the pac command executable, handling Windows-specific cases"""
    # Try common command names
    pac_commands = ['pac']
    
    # On Windows, also try pac.exe and pac.cmd
    if platform.system() == 'Windows':
        pac_commands.extend(['pac.exe', 'pac.cmd'])
    
    for pac_cmd in pac_commands:
        try:
            # Try to run the command without arguments to see if it exists
            # This is more reliable than --version on Windows
            result = subprocess.run([pac_cmd], 
                                  capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
            # pac command returns non-zero when called without arguments, but that means it exists
            # We just need to check that it's not FileNotFoundError
            return pac_cmd
        except FileNotFoundError:
            continue
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception):
            # These errors mean the command exists but failed for another reason
            return pac_cmd
    
    # If no pac command found, try to provide better error message
    return None

def run_pac_command(args):
    """Run a pac command with proper error handling"""
    pac_cmd = find_pac_command()
    if not pac_cmd:
        print("\nERROR: 'pac' command not found!")
        print("\nThe Microsoft Power Platform CLI is required but not installed or not in PATH.")
        
        # Show different instructions based on OS
        if platform.system() == 'Windows':
            print("\nTo install on Windows:")
            print("1. Download from: https://aka.ms/PowerAppsCLI")
            print("2. Or install via winget: winget install Microsoft.PowerPlatformCLI")
            print("3. Or install via npm: npm install -g @microsoft/powerplatform-cli")
            print("\nIf already installed, try:")
            print("- Restart your terminal/command prompt")
            print("- Check if pac is in your PATH by running: where pac")
        else:
            print("\nTo install:")
            print("- Install via npm: npm install -g @microsoft/powerplatform-cli")
            print("- Or download from: https://aka.ms/PowerAppsCLI")
        
        print("\nAfter installation, restart your terminal and try again.")
        return None
    
    try:
        command = [pac_cmd] + args
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running pac command: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        if e.stdout:
            print(f"Command output: {e.stdout}")
        return None
    except Exception as e:
        print(f"Unexpected error running pac command: {e}")
        return None

def run_pac_command_with_status(args):
    """Run a pac command and return (success, stdout, stderr)"""
    pac_cmd = find_pac_command()
    if not pac_cmd:
        print("\nERROR: 'pac' command not found!")
        print("\nThe Microsoft Power Platform CLI is required but not installed or not in PATH.")
        
        # Show different instructions based on OS
        if platform.system() == 'Windows':
            print("\nTo install on Windows:")
            print("1. Download from: https://aka.ms/PowerAppsCLI")
            print("2. Or install via winget: winget install Microsoft.PowerPlatformCLI")
            print("3. Or install via npm: npm install -g @microsoft/powerplatform-cli")
            print("\nIf already installed, try:")
            print("- Restart your terminal/command prompt")
            print("- Check if pac is in your PATH by running: where pac")
        else:
            print("\nTo install:")
            print("- Install via npm: npm install -g @microsoft/powerplatform-cli")
            print("- Or download from: https://aka.ms/PowerAppsCLI")
        
        print("\nAfter installation, restart your terminal and try again.")
        return (False, None, None)
    
    try:
        command = [pac_cmd] + args
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
        return (result.returncode == 0, result.stdout, result.stderr)
    except Exception as e:
        print(f"Unexpected error running pac command: {e}")
        return (False, None, str(e))

def get_auth_list():
    """Get the list of available environments from pac auth list"""
    return run_pac_command(['auth', 'list'])

def get_pages_list():
    """Get the list of available Power Pages sites from pac pages list"""
    success, stdout, stderr = run_pac_command_with_status(['pages', 'list'])
    if success:
        return stdout
    else:
        # For pages list, we want to show the error details but still allow the program to continue
        # as it might just mean no pages exist in this environment
        print(f"Error running pac pages list (exit code indicates potential issue):")
        if stderr:
            print(f"Error details: {stderr}")
        if stdout:
            print(f"Command output: {stdout}")
        return None

def check_site_exists_in_environment(site_id):
    """Check if a site with the given ID exists in the current environment"""
    pages_list = get_pages_list()
    
    if not pages_list:
        return False
    
    # Parse the pages list to find sites
    lines = pages_list.strip().split('\n')
    
    for line in lines:
        # Look for lines that contain site information (with index, website id, and friendly name)
        if '[' in line and ']' in line and len(line.split()) >= 3:
            try:
                # Extract website id
                parts = line.strip().split()
                if len(parts) >= 3:
                    website_id = parts[1]  # f3d0c1af-e8c9-451a-920d-18c75f80f252
                    if website_id == site_id:
                        return True
            except (ValueError, IndexError):
                continue
    
    return False

def select_site_interactive():
    """Interactive site selection from pac pages list"""
    print("\nGetting available sites from current environment...")
    pages_list = get_pages_list()
    
    if not pages_list:
        print("Failed to get pages list")
        sys.exit(1)
    
    print("\nAvailable sites:")
    print(pages_list)
    
    # Parse the pages list to extract site information
    lines = pages_list.strip().split('\n')
    sites = []
    
    for line in lines:
        # Look for lines that contain site information (with index, website id, and friendly name)
        if '[' in line and ']' in line and len(line.split()) >= 3:
            try:
                # Extract index, website id, and friendly name
                parts = line.strip().split()
                if len(parts) >= 3:
                    index_part = parts[0]  # [1]
                    website_id = parts[1]  # f3d0c1af-e8c9-451a-920d-18c75f80f252
                    friendly_name = ' '.join(parts[2:])  # OREF - oref-dev
                    
                    if index_part.startswith('[') and index_part.endswith(']'):
                        index = int(index_part[1:-1])
                        sites.append((index, website_id, friendly_name))
            except (ValueError, IndexError):
                continue
    
    if not sites:
        print("No sites found in the current environment")
        sys.exit(1)
    
    # Interactive site selection
    while True:
        try:
            print(f"\nEnter the index number of the site to download:")
            choice = input("Site Index: ").strip()
            index = int(choice)
            
            # Find the selected site
            selected_site = None
            for site_index, website_id, friendly_name in sites:
                if site_index == index:
                    selected_site = (website_id, friendly_name)
                    break
            
            if selected_site:
                website_id, friendly_name = selected_site
                print(f"Selected site: {friendly_name} (ID: {website_id})")
                return website_id, friendly_name
            else:
                print(f"Invalid index {index}. Please try again.")
                
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)

def select_environment_interactive(prompt_message):
    """Interactive environment selection"""
    print(f"\n{prompt_message}")
    auth_list = get_auth_list()
    
    if not auth_list:
        print("Failed to get authentication list")
        sys.exit(1)
    
    print("\nAvailable environments:")
    print(auth_list)
    
    # Parse the auth list to extract environment names and indices
    lines = auth_list.strip().split('\n')
    environments = []
    
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('Index'):
            environments.append((i, line.strip()))
    
    if not environments:
        print("No environments found")
        sys.exit(1)
    
    environments.append((-1, "Add new environment"))
    
    # Simple input selection (you can enhance this with arrow key navigation later)
    while True:
        try:
            print(f"\nEnter the index number of the environment (or 0 for a new environment):")
            choice = input("Index: ").strip()
            index = int(choice)
            
            if index == 0:
                # Add new environment
                new_env_url = input("Enter the URL for the new environment: ").strip()
                print(f"Creating a new environment at {new_env_url}...")
                success, stdout, stderr = run_pac_command_with_status(['auth', 'create', '--url', new_env_url])
                if success:
                    print("New environment added successfully!")
                    # Re-fetch and display the updated list of environments
                    auth_list = get_auth_list()
                    if not auth_list:
                        print("Failed to get authentication list")
                        sys.exit(1)
                    
                    print("\nUpdated environments:")
                    print(auth_list)
                    continue
                else:
                    print(f"Failed to create new environment: {stderr}")
                    continue

            # Validate the index exists
            success, stdout, stderr = run_pac_command_with_status(['auth', 'select', '--index', str(index)])
            if success:
                print(f"Selected environment at index {index}")
                return index
            else:
                print(f"Invalid index {index}. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)

def load_site_config(folder_path):
    """Load site configuration from website.yml in the given folder"""
    website_yml_path = Path(folder_path) / 'website.yml'
    
    if not website_yml_path.exists():
        print(f"Error: website.yml not found in {folder_path}")
        sys.exit(1)
    
    try:
        with open(website_yml_path, 'r') as file:
            data = yaml.safe_load(file)
            site_id = data.get('adx_websiteid')
            if not site_id:
                print(f"Error: adx_websiteid not found in {website_yml_path}")
                sys.exit(1)
            
            # Get the project name from the folder name
            project_name = Path(folder_path).name
            
            return {
                'site_id': site_id,
                'project_name': project_name
            }
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def run_command(command):
    """Run a shell command and return the result"""
    print(f"Executing: {' '.join(command) if isinstance(command, list) else command}")
    
    if isinstance(command, str):
        result = subprocess.run(command, shell=True, text=True)
    else:
        result = subprocess.run(command, text=True)
    
    return result.returncode

def download_site(web_site_id, download_path="./"):
    """Download site from selected environment"""
    print(f"\nDownloading site with ID: {web_site_id}")
    
    # Convert to absolute path for better cross-platform compatibility
    download_path = str(Path(download_path).resolve())
    
    # Use run_pac_command_with_status to get proper error handling
    # Try different command formats for Windows compatibility
    if platform.system() == 'Windows':
        # Windows: Use full parameter names for better compatibility
        success, stdout, stderr = run_pac_command_with_status(['pages', 'download', '--webSiteId', web_site_id, '--path', download_path, '--modelVersion', '2', '--overwrite'])
    else:
        # Unix/Mac: Use short flags
        success, stdout, stderr = run_pac_command_with_status(['pages', 'download', '--webSiteId', web_site_id, '--path', download_path, '-mv', '2', '-o'])
    
    if success:
        if stdout:
            print(stdout)
        return 0
    else:
        if stderr:
            print(f"Download error: {stderr}")
        return 1

def upload_site(upload_path):
    """Upload site to selected environment"""
    print(f"\nUploading site from path: {upload_path}")
    
    # Use run_pac_command_with_status to get proper error handling
    success, stdout, stderr = run_pac_command_with_status(['pages', 'upload', '--path', upload_path, '--modelVersion', '2'])
    
    if success:
        if stdout:
            print(stdout)
        return 0
    else:
        if stderr:
            print(f"Upload error: {stderr}")
        return 1

def is_site_folder(folder_path):
    """Check if a folder is a Power Pages site folder by looking for website.yml"""
    website_yml_path = Path(folder_path) / 'website.yml'
    return website_yml_path.exists()

def get_current_directory():
    """Get current working directory - cross-platform compatible"""
    return os.getcwd()

def select_folder_interactive(base_path="./"):
    """Interactive folder selection for uploading"""
    base_dir = Path(base_path).resolve()
    
    # Get all directories in the base path
    folders = [f for f in base_dir.iterdir() 
              if f.is_dir() and f.name not in ['.git', '__pycache__', '.vscode', 'node_modules']]
    
    if not folders:
        print(f"No folders found in {base_dir}")
        return None
    
    print(f"\nAvailable folders in {base_dir}:")
    
    # Show folders with indication if they're site folders
    for i, folder in enumerate(folders, 1):
        site_indicator = " (Power Pages site)" if is_site_folder(folder) else ""
        print(f"[{i}] {folder.name}{site_indicator}")
    
    # Interactive folder selection
    while True:
        try:
            print(f"\nEnter the folder number to upload:")
            choice = input("Folder Index: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(folders):
                selected_folder = folders[index]
                print(f"Selected folder: {selected_folder}")
                return str(selected_folder)
            else:
                print(f"Invalid index {index + 1}. Please try again.")
                
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None

def get_first_site_automatically():
    """Automatically get the first (and typically only) site from pac pages list"""
    print("\nGetting available sites from current environment...")
    pages_list = get_pages_list()
    
    if not pages_list:
        print("Failed to get pages list")
        sys.exit(1)
    
    print("\nAvailable sites:")
    print(pages_list)
    
    # Parse the pages list to extract site information
    lines = pages_list.strip().split('\n')
    
    for line in lines:
        # Look for lines that contain site information (with index, website id, and friendly name)
        if '[' in line and ']' in line and len(line.split()) >= 3:
            try:
                # Extract index, website id, and friendly name
                parts = line.strip().split()
                if len(parts) >= 3:
                    index_part = parts[0]  # [1]
                    website_id = parts[1]  # f3d0c1af-e8c9-451a-920d-18c75f80f252
                    friendly_name = ' '.join(parts[2:])  # OREF - oref-dev
                    
                    if index_part.startswith('[') and index_part.endswith(']'):
                        print(f"Found site: {friendly_name} (ID: {website_id})")
                        return website_id, friendly_name
            except (ValueError, IndexError):
                continue
    
    print("No sites found in the current environment")
    sys.exit(1)

def download_site_command(download_path=None):
    """Download a Power Pages site from a selected environment"""
    
    # Set default download path if not provided
    if download_path is None:
        download_path = "./"
    
    print(f"Download path: {download_path}")
    
    # Select source environment for download
    select_environment_interactive("Select environment to download from:")
    
    # Select site from the current environment
    site_id, site_friendly_name = select_site_interactive()
    
    # Download the site
    if download_site(site_id, download_path) != 0:
        print("Download failed!")
        sys.exit(1)
    
    print("Download completed successfully!")
    print(f"Site '{site_friendly_name}' (ID: {site_id}) has been downloaded to {download_path}")

def upload_site_command(folder_path=None):
    """Upload a Power Pages site from a local folder"""
    
    # If no path provided, check if we're in a site folder or need to select one
    if folder_path is None:
        current_dir = get_current_directory()
        
        # Check if current directory is a site folder
        if is_site_folder(current_dir):
            print(f"Detected Power Pages site in current directory: {current_dir}")
            confirm = input("Upload from current directory? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                folder_path = current_dir
            else:
                folder_path = select_folder_interactive()
        else:
            print("Current directory is not a Power Pages site folder.")
            folder_path = select_folder_interactive()
    
    if not folder_path:
        print("No folder selected. Operation cancelled.")
        return
    
    # Verify the selected folder is a site folder
    if not is_site_folder(folder_path):
        print(f"\nERROR: {folder_path} does not appear to be a Power Pages site folder.")
        print("A Power Pages site folder should contain a 'website.yml' file.")
        sys.exit(1)
    
    print(f"\nPreparing to upload Power Pages site from: {folder_path}")
    
    # Load the site configuration to get the site ID
    site_config = load_site_config(folder_path)
    site_id = site_config['site_id']
    project_name = site_config['project_name']
    
    print(f"Site ID from website.yml: {site_id}")
    print(f"Project name: {project_name}")
    
    # Select target environment for upload
    select_environment_interactive("Select TARGET environment to upload to:")
    
    # Safety check: Ensure the site exists in the target environment
    print(f"\nChecking if site with ID {site_id} exists in target environment...")
    if not check_site_exists_in_environment(site_id):
        print(f"\nERROR: Site with ID {site_id} does not exist in the target environment!")
        print("This is a safety check to prevent accidentally creating new sites or overwriting wrong sites.")
        print("\nPlease ensure:")
        print(f"1. A site with ID {site_id} exists in the target environment")
        print("2. You have selected the correct target environment")
        print(f"3. The website.yml file in {folder_path} contains the correct site ID")
        print("\nUpload cancelled for safety.")
        sys.exit(1)
    
    print(f"✓ Site with ID {site_id} found in target environment. Proceeding with upload...")
    
    # Upload the site
    if upload_site(folder_path) != 0:
        print("Upload failed!")
        sys.exit(1)
    
    print("Upload completed successfully!")

def transfer_site(download_path=None, upload_path=None):
    """Main function to transfer site between environments"""
    
    # Set default paths if not provided
    if download_path is None:
        download_path = "./"
    
    print(f"Download path: {download_path}")
    
    # Select source environment for download
    select_environment_interactive("Select SOURCE environment to download from:")
    
    # Select site from the current environment
    site_id, site_friendly_name = select_site_interactive()
    
    # Download the site
    if download_site(site_id, download_path) != 0:
        print("Download failed!")
        sys.exit(1)
    
    print("Download completed successfully!")
    
    # Find the downloaded folder
    if upload_path is None:
        download_dir = Path(download_path)
        downloaded_folders = [f for f in download_dir.iterdir() 
                            if f.is_dir() and f.name != '.git' and f.name != '__pycache__']
        
        if len(downloaded_folders) == 1:
            upload_path = str(downloaded_folders[0])
            print(f"Found downloaded folder: {upload_path}")
        elif len(downloaded_folders) > 1:
            print("\nMultiple folders found. Select the downloaded site folder:")
            for i, folder in enumerate(downloaded_folders, 1):
                print(f"[{i}] {folder.name}")
            
            while True:
                try:
                    choice = input("\nEnter folder number: ").strip()
                    folder_index = int(choice) - 1
                    if 0 <= folder_index < len(downloaded_folders):
                        upload_path = str(downloaded_folders[folder_index])
                        print(f"Selected folder: {upload_path}")
                        break
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
                except KeyboardInterrupt:
                    print("\nOperation cancelled.")
                    sys.exit(0)
        else:
            print("No downloaded folder found!")
            sys.exit(1)
    
    print(f"Upload path: {upload_path}")
    
    # Select target environment for upload
    select_environment_interactive("Select TARGET environment to upload to:")
    
    # Safety check: Ensure the site exists in the target environment
    print(f"\nChecking if site with ID {site_id} exists in target environment...")
    if not check_site_exists_in_environment(site_id):
        print(f"\nERROR: Site with ID {site_id} does not exist in the target environment!")
        print("This is a safety check to prevent accidentally creating new sites or overwriting wrong sites.")
        print("\nPlease ensure:")
        print(f"1. A site with ID {site_id} exists in the target environment")
        print("2. You have selected the correct target environment")
        print("\nTransfer cancelled for safety.")
        
        # Still delete the downloaded folder since transfer won't proceed
        try:
            if upload_path:
                print(f"\nCleaning up downloaded folder: {upload_path}")
                shutil.rmtree(upload_path)
                print("Folder deleted successfully!")
        except Exception as e:
            print(f"Failed to delete folder: {e}")
        
        sys.exit(1)
    
    print(f"✓ Site with ID {site_id} found in target environment. Proceeding with upload...")
    
    # Upload the site
    if upload_site(upload_path) != 0:
        print("Upload failed!")
        sys.exit(1)
    
    print("Upload completed successfully!")
    print("Site transfer completed!\n")

    # Delete the downloaded folder
    try:
        if upload_path:
            print(f"Deleting downloaded folder: {upload_path}")
            shutil.rmtree(upload_path)
            print("Folder deleted successfully!")
    except Exception as e:
        print(f"Failed to delete folder: {e}")

def print_custom_help():
    """Print custom help message with proper alias formatting"""
    help_text = """usage: zooz [-h] {transfer-site,transfer,t,download-site,download,d,upload-site,upload,u} ...

Zooz CLI - Transfer Power Pages sites between environments

positional arguments:
  {transfer-site,transfer,t,download-site,download,d,upload-site,upload,u}
                        Available commands
    transfer-site, transfer, t
                        Transfer a site between environments
    download-site, download, d
                        Download a Power Pages site from a selected environment
    upload-site, upload, u
                        Upload a Power Pages site from a local folder

options:
  -h, --help            show this help message and exit"""
    print(help_text)

def main():
    # Handle help manually before argparse to show custom format
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        print_custom_help()
        sys.exit(0)
        
    parser = argparse.ArgumentParser(
        description='Zooz CLI - Transfer Power Pages sites between environments',
        prog='zooz',
        add_help=False  # Disable default help to use our custom one
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # transfer-site command (alias: transfer, t)
    transfer_parser = subparsers.add_parser(
        'transfer-site',
        aliases=['transfer', 't'],
        help='Transfer a site between environments'
    )
    transfer_parser.add_argument(
        '--download-path',
        default='./',
        help='Path where to download the site (default: ./)'
    )
    transfer_parser.add_argument(
        '--upload-path',
        help='Path from where to upload the site (default: auto-detected from downloaded folder)'
    )
    
    # download-site command (alias: download, d)
    download_parser = subparsers.add_parser(
        'download-site',
        aliases=['download', 'd'],
        help='Download a Power Pages site from a selected environment'
    )
    download_parser.add_argument(
        '--download-path',
        default='./',
        help='Path where to download the site (default: ./)'
    )

    # upload-site command (alias: upload, u)
    upload_parser = subparsers.add_parser(
        'upload-site',
        aliases=['upload', 'u'],
        help='Upload a Power Pages site from a local folder'
    )
    upload_parser.add_argument(
        '--folder-path',
        help='Path to the site folder to upload (default: auto-detect from current directory or interactive selection)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command in ['transfer-site', 'transfer', 't']:
        transfer_site(args.download_path, args.upload_path)
    elif args.command in ['download-site', 'download', 'd']:
        download_site_command(args.download_path)
    elif args.command in ['upload-site', 'upload', 'u']:
        upload_site_command(args.folder_path)

if __name__ == '__main__':
    main()
