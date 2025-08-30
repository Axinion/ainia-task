#!/usr/bin/env python3
"""
Export demo bundle for AI Buddy.

This script creates a zip file containing all generated reports, snapshots,
and documentation for easy sharing and demonstration.
"""

import sys
import zipfile
from pathlib import Path
import subprocess

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def ensure_reports_exist():
    """Ensure reports directory exists and has content."""
    reports_dir = Path("./reports")
    
    if not reports_dir.exists() or not list(reports_dir.glob("*.md")):
        print("📊 Reports directory empty or missing. Generating reports...")
        
        try:
            # Import and run the report module in-process
            from ai_buddy.report import main as report_main
            
            # Set up sys.argv to simulate command line arguments
            original_argv = sys.argv.copy()
            sys.argv = ["export_demo_bundle.py", "--all", "--period", "7d", "--format", "both"]
            
            # Run the report generation
            report_main()
            
            # Restore original argv
            sys.argv = original_argv
            
            print("✅ Reports generated successfully!")
            
        except Exception as e:
            print(f"❌ Failed to generate reports: {e}")
            return False
    
    return True


def create_demo_bundle():
    """Create the demo bundle zip file."""
    bundle_path = Path("./demo_bundle.zip")
    
    # Remove existing bundle if it exists
    if bundle_path.exists():
        bundle_path.unlink()
    
    print("📦 Creating demo bundle...")
    
    with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add reports
        reports_dir = Path("./reports")
        if reports_dir.exists():
            for file_path in reports_dir.glob("*"):
                if file_path.is_file():
                    arcname = f"reports/{file_path.name}"
                    zipf.write(file_path, arcname)
                    print(f"   📄 Added: {arcname}")
        
        # Add snapshots
        snapshots_dir = Path("./data/snapshots")
        if snapshots_dir.exists():
            for file_path in snapshots_dir.glob("*.json"):
                arcname = f"snapshots/{file_path.name}"
                zipf.write(file_path, arcname)
                print(f"   📊 Added: {arcname}")
        
        # Add README
        readme_path = Path("./README.md")
        if readme_path.exists():
            zipf.write(readme_path, "README.md")
            print(f"   📖 Added: README.md")
        
        # Add project structure info
        project_info = f"""AI Buddy Demo Bundle
Generated: {Path().cwd()}
Contains:
- Reports: Generated parent reports for all children
- Snapshots: Child profile snapshots with updated skills
- README: Project documentation

To use:
1. Extract this zip file
2. Open README.md for project overview
3. Browse reports/ for parent reports
4. Check snapshots/ for child progress data
"""
        
        zipf.writestr("BUNDLE_INFO.txt", project_info)
        print(f"   ℹ️  Added: BUNDLE_INFO.txt")
    
    return bundle_path


def main():
    """Main function to create demo bundle."""
    print("🎁 Creating AI Buddy Demo Bundle")
    print("=" * 40)
    
    try:
        # Ensure reports exist
        if not ensure_reports_exist():
            print("❌ Cannot create bundle without reports")
            sys.exit(1)
        
        # Create the bundle
        bundle_path = create_demo_bundle()
        
        # Print summary
        print("\n" + "=" * 40)
        print(f"✅ Demo bundle created successfully!")
        print(f"📦 Bundle location: {bundle_path.absolute()}")
        
        # Show bundle contents
        with zipfile.ZipFile(bundle_path, 'r') as zipf:
            file_count = len(zipf.namelist())
            print(f"📊 Bundle contains {file_count} files")
        
        print("\n🎯 Bundle ready for sharing!")
        
    except Exception as e:
        print(f"❌ Error creating demo bundle: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
