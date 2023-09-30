from datetime import datetime, timezone


class BookRequest:
    def __init__(self, post_db_lookup):
        self.user_id = post_db_lookup[0]
        self.post_id = post_db_lookup[1]
        self.comment = post_db_lookup[2]
        self.request_timestamp = post_db_lookup[3]
        self.is_approved = post_db_lookup[4]
        self.user = None
        self.request_timestamp_utc = datetime.fromtimestamp(self.request_timestamp, timezone.utc)

        request_timestamp_tmp = datetime.fromtimestamp(self.request_timestamp)
        self.request_timestamp_str = request_timestamp_tmp.strftime("%Y-%m-%d %H:%M")
