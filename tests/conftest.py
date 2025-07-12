# tests/conftest.py
import sys, os

# เอาโฟลเดอร์โปรเจกต์ (parent ของ tests/) เข้า sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)
