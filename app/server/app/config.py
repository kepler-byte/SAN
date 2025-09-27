from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

if not MONGO_URI:
    raise ValueError("MONGO_URI or MONGODB_URL environment variable is required")

# ตรวจสอบและปรับปรุง connection string สำหรับ MongoDB Atlas
if "mongodb.net" in MONGO_URI and "ssl=true" not in MONGO_URI:
    # เพิ่ม SSL parameters ถ้ายังไม่มี
    separator = "&" if "?" in MONGO_URI else "?"
    MONGO_URI += f"{separator}ssl=true&retryWrites=true&w=majority"
