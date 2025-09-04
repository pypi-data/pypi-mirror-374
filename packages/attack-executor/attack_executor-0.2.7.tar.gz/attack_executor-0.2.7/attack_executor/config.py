import configparser

def load_config(config_file_path="config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file_path)

    return config

if __name__ == "__main__":
    config_dict = load_config()
    print(config_dict)
