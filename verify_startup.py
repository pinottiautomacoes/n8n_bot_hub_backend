import sys
import os
sys.path.append(os.getcwd())

try:
    from app.main import app
    print("Application imported successfully!")
    print("Routes configured:")
    for route in app.routes:
        print(f"  - {route.path} [{route.name}]")
except Exception as e:
    print(f"Application failed to start: {e}")
    sys.exit(1)
