from datetime import datetime


class User:
    def __init__(self, post_db_lookup):
        self.id = post_db_lookup[0]
        self.email = post_db_lookup[1]
        self.username = post_db_lookup[2]
        self.display_name = post_db_lookup[3]
        self.permissions = post_db_lookup[4]
        self.email_is_public = post_db_lookup[5]
        self.registration_timestamp = post_db_lookup[6]

        registration_timestamp_tmp = datetime.fromtimestamp(self.registration_timestamp)
        self.registration_timestamp_str = registration_timestamp_tmp.strftime("%Y-%m-%d %H:%M")
