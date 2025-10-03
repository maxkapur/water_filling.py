import asyncio

from .interface import main

if __name__ == "__main__":
    print("Serving app on http://localhost:5000")
    asyncio.run(main())
