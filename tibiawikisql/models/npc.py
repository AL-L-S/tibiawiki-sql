import re
import sqlite3

from tibiawikisql import schema, abc
from tibiawikisql.parsers.utils import convert_tibiawiki_position, parse_item_offers, parse_item_trades, parse_spells, \
    parse_destinations, clean_links


class Npc(abc.Row, abc.Parseable, table=schema.Npc):
    """
    Represents a non-playable character.

    Attributes
    ----------
    id: :class:`int`
        The id of the  containing article.
    title: :class:`str`
        The title of the containing article.
    timestamp: :class:`int`
        The last time the containing article was edited.
    raw_attributes: :class:`dict`
        A dictionary containing attributes that couldn't be parsed.
    name: :class:`str`
        The in-game name of the NPC.
    job: :class:`str`
        The NPC's job.
    city: :class:`str`
        The city where the NPC is located.
    x: :class:`int`
        The x coordinates of the NPC.
    y: :class:`int`
        The y coordinates of the NPC.
    z: :class:`int`
        The z coordinates of the NPC.
    version: :class:`str`
        The client version where the NPC was implemented.
    image: :class:`bytes`
        The npc's image in bytes.
    sells: list[:class:`NpcSellOffer`]
        Items sold by the NPC.
    buys: list[:class:`NpcSellOffer`]
        Items bought by the NPC.
    destinations: list[:class:`NpcSellOffer`]
        Places where the NPC can travel to.
    teachable_spells: list[:class:`NpcSpell`]
        Spells teached by the NPC.
    """
    map = {
        "name": ("name", lambda x: x),
        "actualname": ("name", lambda x: x),
        "job": ("job", lambda x: x),
        "city": ("city", lambda x: x),
        "posx": ("x", lambda x: convert_tibiawiki_position(x)),
        "posy": ("y", lambda x: convert_tibiawiki_position(x)),
        "posz": ("z", lambda x: int(x)),
        "implemented": ("version", lambda x: x)
    }
    pattern = re.compile(r"Infobox[\s_]NPC")

    @classmethod
    def from_article(cls, article):
        npc = super().from_article(article)
        if npc is None:
            return None
        if "buys" in npc.raw_attributes:
            buy_items = parse_item_offers(npc.raw_attributes["buys"])
            npc.buying = []
            for item, price, currency in buy_items:
                # Some items have extra requirements, separated with ;, so we remove them
                item = item.split(";")[0]
                if not currency.strip():
                    currency = "Gold Coin"
                value = None
                if price.strip():
                    value = int(price)
                npc.buying.append(NpcBuyOffer(item_name=item.strip(), currency_name=currency, value=value, npc_id=npc.id))
        if "sells" in npc.raw_attributes:
            sell_items = parse_item_offers(npc.raw_attributes["sells"])
            npc.selling = []
            for item, price, currency in sell_items:
                # Some items have extra requirements, separated with ;, so we remove them
                item = item.split(";")[0]
                if not currency.strip():
                    currency = "Gold Coin"
                value = None
                if price.strip():
                    value = int(price)
                npc.selling.append(NpcSellOffer(item_name=item.strip(), currency_name=currency, value=value, npc_id=npc.id))
            # Items traded by npcs (these have a different template)
            trade_items = parse_item_trades(npc.raw_attributes["sells"])
            for item, price, currency in trade_items:
                item = item.split(";")[0]
                value = None
                if price.strip():
                    value = int(price)
                if not currency.strip():
                    currency = "Gold Coin"
                npc.selling.append(NpcSellOffer(item_name=item.strip(), currency_name=currency,value=value, npc_id=npc.id))
            spell_list = parse_spells(npc.raw_attributes["sells"])
            npc.teachable_spells = []
            for group, spells in spell_list:
                for spell in spells:
                    spell = spell.strip()
                    knight = paladin = sorcerer = druid = False
                    if "knight" in group.lower():
                        knight = True
                    elif "paladin" in group.lower():
                        paladin = True
                    elif "druid" in group.lower():
                        druid = True
                    elif "sorcerer" in group.lower():
                        sorcerer = True
                    else:
                        def in_jobs(vocation, _npc):
                            return vocation in _npc.raw_attributes.get("job", "").lower() \
                                   or vocation in _npc.raw_attributes.get("job2", "").lower() \
                                   or vocation in _npc.raw_attributes.get("job3", "").lower()
                        knight = in_jobs("knight", npc)
                        paladin = in_jobs("paladin", npc)
                        druid = in_jobs("druid", npc)
                        sorcerer = in_jobs("sorcerer", npc)
                    exists = False
                    # Exceptions:
                    if npc.name == "Ursula":
                        paladin = True
                    elif npc.name == "Eliza":
                        paladin = druid = sorcerer = knight = True
                    elif npc.name == "Elathriel":
                        druid = True
                    for j, s in enumerate(npc.teachable_spells):
                        # Spell was already in list, so we update vocations
                        if s.spell_name == spell:
                            npc.teachable_spells[j] = NpcSpell(npc_id=npc.id,spell_name=spell, knight=knight or s.knight, paladin=paladin or s.paladin, druid=druid or s.druid, sorcerer=sorcerer or s.sorcerer)
                            exists = True
                            break
                    if not exists:
                        npc.teachable_spells.append(NpcSpell(npc_id=npc.id, spell_name=spell, knight=knight, paladin=paladin, druid=druid, sorcerer=sorcerer))
        destinations = []
        if "notes" in npc.raw_attributes and "{{Transport" in npc.raw_attributes["notes"]:
            destinations.extend(parse_destinations(npc.raw_attributes["notes"]))
        if "sells" in npc.raw_attributes and "{{Transport" in npc.raw_attributes["sells"]:
            destinations.extend(parse_destinations(npc.raw_attributes["sells"]))
        npc.destinations = []
        for destination, price, notes in destinations:
            destination.strip()
            notes = clean_links(notes.strip())
            price = int(price)
            if not notes:
                notes = None
            npc.destinations.append(NpcDestination(npc_id=npc.id, name=destination, price=price, notes=notes))
        return npc

    def insert(self, c):
        super().insert(c)
        for offer in getattr(self, "buying", []):
            offer.insert(c)
        for offer in getattr(self, "selling", []):
            offer.insert(c)
        for spell in getattr(self, "teachable_spells", []):
            spell.insert(c)
        for destination in getattr(self, "destinations", []):
            destination.insert(c)


class NpcOffer:
    def __init__(self, **kwargs):
        self.npc_id = kwargs.get("npc_id")
        self.npc_name = kwargs.get("npc_name")
        self.item_id = kwargs.get("item_id")
        self.item_name = kwargs.get("item_name")
        self.currency_id = kwargs.get("currency_id")
        self.currency_name = kwargs.get("currency_name")
        self.value = kwargs.get("value")


class NpcSellOffer(NpcOffer, abc.Row, table=schema.NpcSelling):
    """
    Represents an item sellable by an NPC.

    Attributes
    ----------
    npc_id: :class:`int`
        The article id of the npc that sells the item.
    npc_name: :class:`str`
        The name of the npc that sells the item.
    item_id: :class:`int`
        The id of the item sold by the npc.
    item_name: :class:`str`
        The name of the item sold by the npc.
    currency_id: :class:`int`
        The item id of the currency used to buy the item.
    currency_name: :class:`str`
        The name of the currency used to buy the item
    value: :class:`str`
        The value of the item in the specified currency.
    """
    __slots__ = ("npc_id", "npc_name", "item_id", "item_name", "currency_id", "currency_name", "currency_value")

    def insert(self, c):
        try:
            if getattr(self, "item_id", None) and getattr(self, "value", None) and getattr(self, "currency_id", None):
                super().insert(c)
            elif getattr(self, "value", 0):
                query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                            VALUES(
                            ?,
                            (SELECT id from item WHERE title = ?),
                            ?,
                            (SELECT id from item WHERE title = ?))"""
                c.execute(query, (self.npc_id, self.item_name, self.value, self.currency_name))
            else:
                query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                                        VALUES(
                                        ?,
                                        (SELECT id from item WHERE title = ?),
                                        (SELECT price from item WHERE title = ?),
                                        (SELECT id from item WHERE title = ?))"""
                c.execute(query, (self.npc_id, self.item_name, self.item_name, self.currency_name))
        except sqlite3.IntegrityError:
            pass


class NpcBuyOffer(NpcOffer, abc.Row, table=schema.NpcBuying):
    """
        Represents an item buyable by an NPC.

        Attributes
        ----------
        npc_id: :class:`int`
            The article id of the npc that buys the item.
        npc_name: :class:`str`
            The name of the npc that buys the item.
        item_id: :class:`int`
            The id of the item bought by the npc.
        item_name: :class:`str`
            The name of the item bought by the npc.
        currency_id: :class:`int`
            The item id of the currency used to sell the item.
        currency_name: :class:`str`
            The name of the currency used to sell the item
        value: :class:`str`
            The value of the item in the specified currency.
        """
    __slots__ = ("npc_id", "npc_name", "item_id", "item_name", "currency_id", "currency_name", "currency_value")

    def insert(self, c):
        try:
            if getattr(self, "item_id", None) and getattr(self, "value", None) and getattr(self, "currency_id", None):
                super().insert(c)
            elif getattr(self, "value", 0):
                query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                            VALUES(
                            ?,
                            (SELECT id from item WHERE title = ?),
                            ?,
                            (SELECT id from item WHERE title = ?))"""
                c.execute(query, (self.npc_id, self.item_name, self.value, self.currency_name))
            else:
                query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                                        VALUES(
                                        ?,
                                        (SELECT id from item WHERE title = ?),
                                        (SELECT price from item WHERE title = ?),
                                        (SELECT id from item WHERE title = ?))"""
                c.execute(query, (self.npc_id, self.item_name, self.item_name, self.currency_name))
        except sqlite3.IntegrityError:
            pass


class NpcSpell(abc.Row, table=schema.NpcSpell):
    """
    Represents a spell that a NPC can teach.

    Attributes
    ----------
    npc_id: :class:`int`
        The article id of the npc that teaches the spell.
    npc_name: :class:`str`
        The name of the npc that teaches the spell.
    spell_id: :class:`int`
        The article id of the spell taught by the npc.
    spell_name: :class:`str`
        The name of the spell taught by the npc.
    knight: :class:`bool`
        If the spell is taught to knights.
    paladin: :class:`bool`
        If the spell is taught to paladins.
    druid: :class:`bool`
        If the spell is taught to druids.
    sorcerer: :class:`bool`
        If the spell is taught to sorcerers.
    """
    __slots__ = ("npc_id", "npc_name", "spell_id", "spell_name", "knight", "sorcerer", "paladin", "druid")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.npc_name = kwargs.get("npc_name")
        self.spell_name = kwargs.get("spell_name")

    def __repr__(self):
        try:
            return "%s(spell_name=%r)" % (self.__class__.__name__, self.spell_name)
        except AttributeError:
            return "%s(npc_id=%r, npc_name=%r)" % (self.__class__.__name__, self.npc_id, self.spell_id)

    def insert(self, c):
        if getattr(self, "spell_id", None):
            super().insert(c)
        else:
            query = f"""INSERT INTO {self.table.__tablename__}({','.join(c.name for c in self.table.columns)})
                        VALUES(?, (SELECT id from spell WHERE title = ?), ?, ?, ?, ?)"""
            c.execute(query, (self.npc_id, self.spell_name, self.knight, self.sorcerer, self.paladin, self.druid))


class NpcDestination(abc.Row, table=schema.NpcDestination):
    """
    Represents a NPC's travel destination

    Attributes
    ----------
    npc_id: :class:`int`
        The article id of the NPC.
    npc_name: :class:`str`
        The name of the NPC.
    name: :class:`str`
        The name of the destination
    price: :class:`int`
        The price in gold to travel.
    notes: :class:`str`
        Notes about the destination, such as requirements.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.npc_name = kwargs.get("npc_name")
