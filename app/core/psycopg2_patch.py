"""
Patch psycopg2 to handle Windows locale issues
This must be imported BEFORE any database connections are made
"""
import locale
import os
import sys

# Force UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Override locale to use UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        # If both fail, at least set the encoding
        pass

# Patch psycopg2's _connect function to handle encoding
def patch_psycopg2():
    try:
        import psycopg2
        import psycopg2.extensions
        
        # Register UTF-8 as the default client encoding
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
        
        print("[OK] psycopg2 patched for UTF-8 encoding")
    except Exception as e:
        print(f"[WARNING] Could not patch psycopg2: {e}")

# Apply patch when this module is imported
patch_psycopg2()
