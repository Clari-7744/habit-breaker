config = """CREATE TABLE IF NOT EXISTS config (
    user_id BIGINT NOT NULL,
    habit TEXT NOT NULL,
    pretty_name TEXT NOT NULL
)"""
slash_guilds = """CREATE TABLE IF NOT EXISTS slash_guilds (
	guild_id BIGINT NOT NULL PRIMARY KEY
)"""
logs = """CREATE TABLE IF NOT EXISTS logs (
    user_id BIGINT NOT NULL,
    habit TEXT NOT NULL,
    timestamp BIGINT NOT NULL
)"""
messages = """CREATE TABLE IF NOT EXISTS messages (
    channel_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    habit TEXT NOT NULL
)"""
all_schemas = config, slash_guilds, logs, messages
