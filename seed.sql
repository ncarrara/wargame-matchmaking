--CREATE DATABASE warhammer;

\c warhammer;
--
--DROP TABLE IF EXISTS match_participants CASCADE;
--DROP TABLE IF EXISTS matches CASCADE;
--DROP TABLE IF EXISTS venues CASCADE;
--DROP TABLE IF EXISTS factions CASCADE;
--DROP TABLE IF EXISTS players CASCADE;
--DROP TABLE IF EXISTS chat_messages CASCADE;
--DROP TABLE IF EXISTS contact_messages CASCADE;

CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    pseudo VARCHAR(20),
    email VARCHAR(100) UNIQUE NOT NULL,
    mmr INTEGER NOT NULL DEFAULT 2000,
    games_number INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS factions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS venues (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    address VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    venue_id SERIAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    state VARCHAR(10) NOT NULL CHECK (state IN ('open','ongoing', 'closed', 'cancel')),
    ranked BOOLEAN NOT NULL,


    CONSTRAINT fk_created_by FOREIGN KEY (created_by)
        REFERENCES players(id) ON DELETE CASCADE,

    CONSTRAINT fk_venue_id FOREIGN KEY (venue_id)
        REFERENCES venues(id) ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS match_participants (
    match_id INTEGER NOT NULL,
    is_ready BOOLEAN NOT NULL DEFAULT FALSE,
    player_id INTEGER NOT NULL,
    faction_id INTEGER NOT NULL,
    mmr_before INTEGER NOT NULL,
    mmr_after INTEGER NOT NULL,
    result VARCHAR(10) NOT NULL CHECK (result IN ('undefined','win', 'lose', 'draw')),

    PRIMARY KEY (match_id, player_id),

    CONSTRAINT fk_match FOREIGN KEY (match_id)
        REFERENCES matches(id) ON DELETE CASCADE,

    CONSTRAINT fk_player FOREIGN KEY (player_id)
        REFERENCES players(id) ON DELETE CASCADE,

    CONSTRAINT fk_faction FOREIGN KEY (faction_id)
        REFERENCES factions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    destination_player_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_match_chat FOREIGN KEY (match_id)
        REFERENCES matches(id) ON DELETE CASCADE,

    CONSTRAINT fk_player_chat FOREIGN KEY (player_id)
        REFERENCES players(id) ON DELETE CASCADE
);

-- Optional: index for fast lookups of messages in a match lobby
CREATE INDEX idx_chat_messages_match_id ON chat_messages(match_id);
CREATE INDEX idx_chat_messages_player_id ON chat_messages(player_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);


--INSERT INTO players (id, name, email, password_hash) VALUES ('2', 'jean', 'jean@gmail.com','hash');

INSERT INTO factions (id, name) VALUES ('0', 'Grand Cathay');
INSERT INTO factions (id, name) VALUES ('1', 'Wild Herd');
INSERT INTO factions (id, name) VALUES ('2', 'Chracian Warhost');
INSERT INTO factions (id, name) VALUES ('3', 'Bretonnian Exiles');
INSERT INTO factions (id, name) VALUES ('4', 'Tomb Kings of Khemri');
INSERT INTO factions (id, name) VALUES ('5', 'Mortuary Cult');
INSERT INTO factions (id, name) VALUES ('6', 'Kingdom of Bretonnia');
INSERT INTO factions (id, name) VALUES ('7', 'Errantry Crusade');
INSERT INTO factions (id, name) VALUES ('8', 'Vampire Counts');
INSERT INTO factions (id, name) VALUES ('9', 'Beastmen Brayherds');
INSERT INTO factions (id, name) VALUES ('10', 'High Elf Realms');
INSERT INTO factions (id, name) VALUES ('11', 'Warriors of Chaos');
INSERT INTO factions (id, name) VALUES ('12', 'Royal Clan');
INSERT INTO factions (id, name) VALUES ('13', 'City-State of Nuln');
INSERT INTO factions (id, name) VALUES ('14', 'Chaos Dwarfs');
INSERT INTO factions (id, name) VALUES ('15', 'Wood Elf Realms');
INSERT INTO factions (id, name) VALUES ('16', 'Nomadic Waaagh!');
INSERT INTO factions (id, name) VALUES ('17', 'Orc & Goblin Tribes');
INSERT INTO factions (id, name) VALUES ('18', 'Nehekharan Royal Hosts');
INSERT INTO factions (id, name) VALUES ('19', 'Heralds of Darkness');
INSERT INTO factions (id, name) VALUES ('20', 'Troll Horde');
INSERT INTO factions (id, name) VALUES ('21', 'Orion''s WildHunt');
INSERT INTO factions (id, name) VALUES ('22', 'Wolves of the Sea');
INSERT INTO factions (id, name) VALUES ('23', 'Expeditionary Force');
INSERT INTO factions (id, name) VALUES ('24', 'Daemons of Chaos');
INSERT INTO factions (id, name) VALUES ('25', 'Dark Elves');
INSERT INTO factions (id, name) VALUES ('26', 'Empire of Man');
INSERT INTO factions (id, name) VALUES ('27', 'Dwarfen Mountain Holds');
INSERT INTO factions (id, name) VALUES ('28', 'Ogre Kingdoms');
INSERT INTO factions (id, name) VALUES ('29', 'Host of Talsyn');
INSERT INTO factions (id, name) VALUES ('30', 'Lizardmen');
INSERT INTO factions (id, name) VALUES ('31', 'Skaven');

INSERT INTO venues (id, name, address) VALUES ('0', 'Warhall', 'online');
INSERT INTO venues (id, name, address) VALUES ('1', 'Table Top Simulator', 'online');
INSERT INTO venues (id, name, address) VALUES ('2', 'At home', 'online');
INSERT INTO venues (id, name, address) VALUES ('3', 'Other', 'online');
INSERT INTO venues (id, name, address) VALUES ('4', 'French Wargame Café', 'Paris 12');
INSERT INTO venues (id, name, address) VALUES ('5', 'Café du Vieux Monde', 'Rennes');
INSERT INTO venues (id, name, address) VALUES ('6','les chevaliers de la duchesse', ' 44');
INSERT INTO venues (id, name, address) VALUES ('7','les gobelins du bocage', '14');
INSERT INTO venues (id, name, address) VALUES ('8','les lutins du Cotentin', ' 50');
INSERT INTO venues (id, name, address) VALUES ('9','Sartrouville Figurines et Jeux (SJF)', '78');
INSERT INTO venues (id, name, address) VALUES ('10','Club Ludique de Boulogne Billancourt (CLUBB)', '92');
INSERT INTO venues (id, name, address) VALUES ('11','Les stratèges du Vieux Monde', '10');
INSERT INTO venues (id, name, address) VALUES ('12','Championnet', '75');
INSERT INTO venues (id, name, address) VALUES ('13','Nice Wargame Association', '6');
INSERT INTO venues (id, name, address) VALUES ('14','Jeux tu il', '6');
INSERT INTO venues (id, name, address) VALUES ('15','Jeune Garde de Lyon', '1');
INSERT INTO venues (id, name, address) VALUES ('16','Tassin', '69');
INSERT INTO venues (id, name, address) VALUES ('17','Lyon War Club', '69');
INSERT INTO venues (id, name, address) VALUES ('18','Mootland', '38');
INSERT INTO venues (id, name, address) VALUES ('19','RoGg', '76');
INSERT INTO venues (id, name, address) VALUES ('20','Old World Gard et alentours', '30');
INSERT INTO venues (id, name, address) VALUES ('21','Terra Olonna', '85');
INSERT INTO venues (id, name, address) VALUES ('22','Les Lanciers', ' 33');
INSERT INTO venues (id, name, address) VALUES ('23','La Licorne Ludique', ' 50');
INSERT INTO venues (id, name, address) VALUES ('24','La Horde d''Or', '92');
INSERT INTO venues (id, name, address) VALUES ('25','Alap du Puteaux', ' 92');
INSERT INTO venues (id, name, address) VALUES ('26','Fig Oxitan', ' 31');
INSERT INTO venues (id, name, address) VALUES ('27','Les Griffons', ' 31');
INSERT INTO venues (id, name, address) VALUES ('28','futur recrue XV Légion', '76');
INSERT INTO venues (id, name, address) VALUES ('29','Figurines et Jeux', '27');
INSERT INTO venues (id, name, address) VALUES ('30','Les gueulards', ' 45');
INSERT INTO venues (id, name, address) VALUES ('31','bonnelles', ' 78');
INSERT INTO venues (id, name, address) VALUES ('32','Évry', ' 91');
INSERT INTO venues (id, name, address) VALUES ('33','vert saint denis', ' 77');
INSERT INTO venues (id, name, address) VALUES ('34','gw paris 12', '75');
INSERT INTO venues (id, name, address) VALUES ('35','rathelot', '');
INSERT INTO venues (id, name, address) VALUES ('36','montigny le bretonneux', '78');