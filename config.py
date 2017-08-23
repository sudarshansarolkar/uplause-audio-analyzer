import toml

broadcasters = {}
audio = {}

with open("config.toml") as conffile:
    config = toml.loads(conffile.read())
    print (config)
    print (config["broadcasters"]["uplause"])

    global broadcasters
    broadcasters = config["broadcasters"]

    global audio
    audio = config["audio"]