from tibiawikisql.database import Table, Integer, Text, Column, Blob, Real, ForeignKey, Boolean


class Achievement(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    grade = Column(Integer)
    points = Column(Integer)
    description = Column(Text)
    spoiler = Column(Text)
    secret = Column(Boolean)
    premium = Column(Integer)
    version = Column(Text)
    timestamp = Column(Integer)


class Charm(Table):
    id = Column(Integer, auto_increment=True)
    name = Column(Text)
    type = Column(Text)
    description = Column(Text)
    points = Column(Integer)
    image = Column(Blob)


class Creature(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    article = Column(Text)
    hitpoints = Column(Integer)
    experience = Column(Integer)
    armor = Column(Integer)
    speed = Column(Integer)
    classz = Column(Text, name="class")
    bestiary_class = Column(Text)
    bestiary_level = Column(Text)
    bestiary_occurrence = Column(Text)
    type = Column(Text)
    max_damage = Column(Integer)
    summon_cost = Column(Integer)
    convince_cost = Column(Integer)
    illusionable = Column(Boolean)
    pushable = Column(Boolean)
    paralysable = Column(Boolean)
    sees_invisible = Column(Integer)
    boss = Column(Integer)
    modifier_physical = Column(Integer)
    modifier_earth = Column(Integer)
    modifier_fire = Column(Integer)
    modifier_ice = Column(Integer)
    modifier_energy = Column(Integer)
    modifier_death = Column(Integer)
    modifier_holy = Column(Integer)
    modifier_drown = Column(Integer)
    modifier_hpdrain = Column(Integer)
    abilities = Column(Text)
    walks_through = Column(Text)
    walks_around = Column(Text)
    version = Column(Text)
    image = Column(Blob)
    timestamp = Column(Integer)


class Item(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    article = Column(Text)
    stackable = Column(Boolean, default=False)
    value = Column(Integer)
    price = Column(Integer)
    weight = Column(Real)
    classz = Column(Text, name="class")
    type = Column(Text)
    flavor_text = Column(Text)
    version = Column(Text)
    client_id = Column(Integer)
    image = Column(Blob)
    timestamp = Column(Integer)


class CreatureDrop(Table, table_name="creature_drop"):
    creature_id = Column(ForeignKey(Integer, table="creature", column="id"))
    item_id = Column(ForeignKey(Integer, table="item", column="id"))
    chance = Column(Real)
    min = Column(Integer)
    max = Column(Integer)


class ItemAttribute(Table, table_name="item_attribute"):
    item_id = Column(ForeignKey(Integer, "item", "id"))
    name = Column(Text)
    value = Column(Text)


class DatabaseInfo(Table, table_name="database_info"):
    key = Column(Text, primary_key=True)
    value = Column(Text)


class House(Table):
    id = Column(Integer, primary_key=True)
    house_id = Column(Integer)
    title = Column(Text)
    name = Column(Text)
    city = Column(Text)
    street = Column(Text)
    beds = Column(Integer)
    rent = Column(Integer)
    size = Column(Integer)
    rooms = Column(Integer)
    floors = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    guildhall = Column(Integer)
    version = Column(Text)
    timestamp = Column(Integer)


class Imbuement(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    tier = Column(Text)
    type = Column(Text)
    effect = Column(Text)
    version = Column(Text)
    image = Column(Blob)
    timestamp = Column(Integer)


class ImbuementMaterial(Table, table_name="imbuement_material"):
    imbuement_id = Column(ForeignKey(Integer, "imbuement", "id"))
    item_id = Column(ForeignKey(Integer, "item", "id"))
    amount = Column(Integer)


class ItemKey(Table, table_name="item_key"):
    id = Column(Integer)
    title = Column(Text)
    number = Column(Integer, primary_key=True)
    item_id = Column(ForeignKey(Integer, "item", "id"))
    name = Column(Text)
    material = Column(Text)
    location = Column(Text)
    origin = Column(Text)
    notes = Column(Text)
    version = Column(Text)
    timestamp = Column(Integer)


class Map(Table):
    z = Column(Integer, primary_key=True)
    image = Column(Blob)


class Spell(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    words = Column(Text)
    type = Column(Text)
    classz = Column(Text, name="class")
    element = Column(Text)
    level = Column(Integer)
    mana = Column(Integer)
    soul = Column(Integer, default=0)
    premium = Column(Integer)
    price = Column(Integer)
    cooldown = Column(Integer)
    knight = Column(Boolean, default=False)
    sorcerer = Column(Boolean, default=False)
    druid = Column(Boolean, default=False)
    paladin = Column(Boolean, default=False)
    image = Column(Blob)
    timestamp = Column(Integer)


class Npc(Table):
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    name = Column(Text)
    city = Column(Text)
    job = Column(Text)
    version = Column(Text)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    image = Column(Blob)
    timestamp = Column(Integer)


class NpcBuying(Table, table_name="npc_buying"):
    npc_id = Column(ForeignKey(Integer, "npc", "id"))
    item_id = Column(ForeignKey(Integer, "item", "id"), nullable=False)
    value = Column(Integer, nullable=False)
    currency_id = Column(ForeignKey(Integer, "item", "id"), nullable=False)


class NpcSelling(Table, table_name="npc_selling"):
    npc_id = Column(ForeignKey(Integer, "npc", "id"))
    item_id = Column(ForeignKey(Integer, "item", "id"), nullable=False)
    value = Column(Integer, nullable=False)
    currency_id = Column(ForeignKey(Integer, "item", "id"), nullable=False)


class NpcDestination(Table, table_name="npc_destination"):
    npc_id = Column(ForeignKey(Integer, "npc", "id"))
    name = Column(Text)
    price = Column(Integer)
    notes = Column(Text)


class NpcSpell(Table, table_name="npc_spell"):
    npc_id = Column(ForeignKey(Integer, "npc", "id"))
    spell_id = Column(ForeignKey(Integer, "spell", "id"))
    knight = Column(Integer)
    sorcerer = Column(Integer)
    paladin = Column(Integer)
    druid = Column(Integer)


class Quest(Table):
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    location = Column(Text)
    legend = Column(Text)
    level_required = Column(Integer)
    level_recommended = Column(Integer)
    premium = Column(Integer)
    version = Column(Text)
    timestamp = Column(Integer)


class QuestDanger(Table, table_name="quest_danger"):
    quest_id = Column(ForeignKey(Integer, "quest", "id"))
    creature_id = Column(ForeignKey(Integer, "creature", "id"), nullable=False)


class QuestReward(Table, table_name="quest_reward"):
    quest_id = Column(ForeignKey(Integer, "quest", "id"))
    item_id = Column(ForeignKey(Integer, "item", "id"), nullable=False)


class RashidPosition(Table, table_name="rashid_position"):
    day = Column(Integer, primary_key=True)
    city = Column(Text)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)


def create_tables(conn):
    """
    Creates all the tables in the database.
    Parameters
    ----------
    conn: sqlite3.Connection

    """
    for table in Table.all_tables():
        conn.execute(table.drop())
        conn.execute(table.create_table())
