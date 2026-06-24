#!/usr/bin/env python
"""
Script untuk mengecek status instalasi Tesseract OCR
"""

import sys
import os
import subprocess

def check_tesseract():
    print("=" * 60)
    print("Tesseract OCR Installation Check")
    print("=" * 60)
    
    # Check 1: Try import pytesseract
    print("\n[1] Checking pytesseract import...")
    try:
        import pytesseract
        print("    ✓ pytesseract imported successfully")
    except ImportError as e:
        print(f"    ✗ Failed to import pytesseract: {e}")
        print("    → Install with: pip install pytesseract")
        return False
    
    # Check 2: Check common Tesseract paths
    print("\n[2] Checking Tesseract installation paths...")
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    
    found_path = None
    for path in common_paths:
        if os.path.exists(path):
            print(f"    ✓ Found: {path}")
            found_path = path
            break
    
    if not found_path:
        print("    ✗ Tesseract not found in common locations")
        print("    → Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    # Check 3: Try to get version
    print("\n[3] Checking Tesseract version...")
    try:
        if found_path:
            pytesseract.pytesseract_cmd = found_path
        
        version = pytesseract.get_tesseract_version()
        print(f"    ✓ Tesseract version: {version}")
    except Exception as e:
        print(f"    ✗ Failed to get version: {e}")
        return False
    
    # Check 4: Try simple OCR
    print("\n[4] Testing OCR functionality...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        
        # Create simple test image
        test_img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(test_img)
        draw.text((10, 10), "Test OCR", fill='black')
        
        # Save temp image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            test_img.save(tmp.name)
            temp_path = tmp.name
        
        # Try OCR
        text = pytesseract.image_to_string(test_img)
        
        print(f"    ✓ OCR test successful")
        print(f"    Extracted text: '{text.strip()}'")
        
        # Cleanup
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"    ✗ OCR test failed: {e}")
        return False
    
    # Check 5: Check language data
    print("\n[5] Checking available languages...")
    try:
        from pytesseract import Output
        result = pytesseract.image_to_data(
            Image.new('RGB', (1, 1)),
            output_type=Output.DICT
        )
        print(f"    ✓ Language data available")
    except Exception as e:
        print(f"    ⚠ Language data check warning: {e}")
    
    print("\n" + "=" * 60)
    print("✓ All checks passed! Tesseract is ready to use.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = check_tesseract()
    sys.exit(0 if success else 1)
