"""Entry point for Railway - Redirects to app.main"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        # Import and run the actual main function
        from app.main import main
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
