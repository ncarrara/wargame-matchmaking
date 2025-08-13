DROP TABLE players CASCADE;
DROP TABLE players CASCADE;
DROP TABLE factions CASCADE;
DROP TABLE matches CASCADE;
DROP TABLE match_participants CASCADE;

CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    mmr INTEGER NOT NULL DEFAULT 2000,
    discord_id BIGINT UNIQUE  NOT NULL,
    discord_username VARCHAR(50),
    discord_discriminator SERIAL
);

CREATE TABLE IF NOT EXISTS factions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS match_participants (
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    faction_id INTEGER NOT NULL,
    mmr_before INTEGER NOT NULL,
    mmr_after INTEGER NOT NULL,
    result VARCHAR(10) NOT NULL CHECK (result IN ('win', 'lose', 'draw')),

    PRIMARY KEY (match_id, player_id),

    CONSTRAINT fk_match FOREIGN KEY (match_id)
        REFERENCES matches(id) ON DELETE CASCADE,

    CONSTRAINT fk_player FOREIGN KEY (player_id)
        REFERENCES players(id) ON DELETE CASCADE,

    CONSTRAINT fk_faction FOREIGN KEY (faction_id)
        REFERENCES factions(id) ON DELETE CASCADE
);

--INSERT INTO players (id, name, email,password_hash) VALUES ('0', 'nicolas', 'nicolas@gmail.com','hash');
--INSERT INTO players (id, name, email, password_hash) VALUES ('1', 'florent', 'flo@gmail.com','hash');
--INSERT INTO players (id, name, email, password_hash) VALUES ('2', 'jean', 'jean@gmail.com','hash');
--INSERT INTO factions (id, name) VALUES ('0', 'dark elves');
--INSERT INTO factions (id, name) VALUES ('1', 'empire (grand army)');
--INSERT INTO factions (id, name) VALUES ('2', 'high elves (traitors)');