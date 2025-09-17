from app.database import init_db
import asyncio

# Run the async init_db function
asyncio.run(init_db())
print("Database tables created successfully!")