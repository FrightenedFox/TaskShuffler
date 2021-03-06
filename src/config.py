from configparser import ConfigParser


def config(section, filename="../config.ini"):
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        params = dict(parser[section])
    else:
        raise Exception(f"File {filename} doesn't exists or there is no "
                        f"section {section}.")
    return params


if __name__ == "__main__":
    print(config("postgresql"))