class BookPostDeletedUser:
    def __init__(self, author_id):
        self.id = author_id
        self.email = author_id
        self.username = author_id
        self.display_name = "Deleted User"
        self.permissions = 0
        self.email_is_public = 0
        self.registration_timestamp = 0
