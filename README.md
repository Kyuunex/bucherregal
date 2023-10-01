# Bucherregal
Bucherregal is a Book Giveaway Service where registered users can offer books for free and also take books that are offered by others. 
Non-registered users can view the list of available books. The project includes user registration, book management, 
and supporting resources like book authors, genres, condition, and more.

# Features
- OpenGraph for embedding
- RSS feed
- 2FA account security
- API functionality
- Requests system, reject/approve
- CRUD operations on books
- Search functionality

### Planned Features:
- Sending messages to another user
- Attachments with image processing for saving storage space
- Profile editing
- Spam filtering

# Quick Installation for testing, debugging and evaluation
Note: on Windows, use Git Bash, on Linux, use your usual terminal.
```bash
git clone https://github.com/Kyuunex/bucherregal.git -b master
cd bucherregal
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
./test.py
```

### [Installation Instructions for Production (Non-Docker)](https://github.com/Kyuunex/bucherregal/blob/master/installation.md)
### [Endpoint Documentation](https://github.com/Kyuunex/bucherregal/blob/master/documentation.md)
