class WebsiteConfig:
    def __init__(self, config_db):
        self.title = "Bucherregal"
        self.timezone = None
        self.timezone_str = "+00:00"
        self.allow_registration = 0

        for one_config in config_db:
            if one_config[0] == "title":
                self.title = str(one_config[1])
            elif one_config[0] == "timezone_str":
                self.timezone_str = str(one_config[1])
                self.timezone = None
            elif one_config[0] == "allow_registration":
                self.allow_registration = int(one_config[1])
