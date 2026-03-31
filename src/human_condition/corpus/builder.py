"""CorpusBuilder — orchestrate loading from all registered sources."""
from __future__ import annotations

import re

import requests

from human_condition.corpus.document import Document
from human_condition.corpus.registry import CorpusRegistry

# ── Registry Bootstrap ──────────────────────────────────────────────


def register_all_sources(registry: CorpusRegistry) -> None:
    """Register every corpus source loader."""
    registry.register("constitution", load_constitution)
    registry.register("communist_manifesto", load_communist_manifesto)
    registry.register("marx", load_marx)
    registry.register("plato", load_plato)
    registry.register("nietzsche", load_nietzsche)
    registry.register("confucius", load_confucius)
    registry.register("quran", load_quran)
    registry.register("bible", load_bible)
    registry.register("gutenberg", load_gutenberg)


# ── CorpusBuilder ──────────────────────────────────────────────────


class CorpusBuilder:
    """Orchestrates loading documents from all registered corpus sources."""

    def __init__(
        self, registry: CorpusRegistry | None = None, *, auto_register: bool = True
    ) -> None:
        self.registry = registry or CorpusRegistry()
        if auto_register:
            register_all_sources(self.registry)

    def build(self) -> list[Document]:
        """Load all documents from every registered source."""
        all_docs: list[Document] = []
        for source_id in self.registry.list_sources():
            docs = self.registry.load(source_id)
            all_docs.extend(docs)
        return all_docs


# ── Hardcoded Text Loader ──────────────────────────────────────────

_TEXTS: dict[str, dict] = {
    "constitution": {
        "title": "US Constitution",
        "text": (
            "We the People of the United States, in Order to form a more "
            "perfect Union, establish Justice, insure domestic Tranquility, "
            "provide for the common defence, promote the general Welfare, "
            "and secure the Blessings of Liberty to ourselves and our "
            "Posterity, do ordain and establish this Constitution for the "
            "United States of America. "
            "Article I. All legislative Powers herein granted shall be "
            "vested in a Congress of the United States, which shall consist "
            "of a Senate and House of Representatives. No Person shall be "
            "a Senator who shall not have attained to the Age of thirty "
            "Years, and been nine Years a Citizen of the United States. "
            "The Congress shall have Power To lay and collect Taxes, Duties, "
            "Imposts and Excises, to pay the Debts and provide for the common "
            "Defence and general Welfare of the United States. "
            "No Bill of Attainder or ex post facto Law shall be passed. "
            "The Privilege of the Writ of Habeas Corpus shall not be "
            "suspended, unless when in Cases of Rebellion or Invasion "
            "the public Safety may require it. "
            "Congress shall make no law respecting an establishment of "
            "religion, or prohibiting the free exercise thereof; or "
            "abridging the freedom of speech, or of the press; or the "
            "right of the people peaceably to assemble, and to petition "
            "the Government for a redress of grievances. "
            "A well regulated Militia, being necessary to the security "
            "of a free State, the right of the people to keep and bear "
            "Arms, shall not be infringed. "
            "No Soldier shall, in time of peace be quartered in any house, "
            "without the consent of the Owner, nor in time of war, but "
            "in a manner to be prescribed by law. "
            "The right of the people to be secure in their persons, houses, "
            "papers, and effects, against unreasonable searches and seizures, "
            "shall not be violated, and no Warrants shall issue, but upon "
            "probable cause, supported by Oath or affirmation, and "
            "particularly describing the place to be searched, and the "
            "persons or things to be seized. "
            "In all criminal prosecutions, the accused shall enjoy the "
            "right to a speedy and public trial, by an impartial jury of "
            "the State and district wherein the crime shall have been "
            "committed. "
            "Excessive bail shall not be required, nor excessive fines "
            "imposed, nor cruel and unusual punishments inflicted. "
            "The enumeration in the Constitution, of certain rights, "
            "shall not be construed to deny or disparage others retained "
            "by the people. "
            "The powers not delegated to the United States by the "
            "Constitution, nor prohibited by it to the States, are "
            "reserved to the States respectively, or to the people."
        ),
    },
    "communist_manifesto": {
        "title": "The Communist Manifesto",
        "text": (
            "A spectre is haunting Europe — the spectre of communism. "
            "All the powers of old Europe have entered into a holy "
            "alliance to exorcise this spectre: Pope and Tsar, Metternich "
            "and Guizot, French Radicals and German police-spies. "
            "The history of all hitherto existing society is the history "
            "of class struggles. Freeman and slave, patrician and plebeian, "
            "lord and serf, guild-master and journeyman, in a word, oppressor "
            "and oppressed, stood in constant opposition to one another, "
            "carried on an uninterrupted, now hidden, now open fight, a fight "
            "that each time ended, either in a revolutionary re-constitution "
            "of society at large, or in the common ruin of the contending "
            "classes. "
            "The bourgeoisie, wherever it has got the upper hand, has put "
            "an end to all feudal, patriarchal, idyllic relations. It has "
            "pitilessly torn asunder the motley feudal ties that bound man "
            "to his natural superiors, and has left remaining no other nexus "
            "between man and man than naked self-interest, than callous "
            "cash payment. "
            "The bourgeoisie cannot exist without constantly revolutionising "
            "the instruments of production, and thereby the relations of "
            "production, and with them the whole relations of society. "
            "Modern bourgeois society, with its relations of production, "
            "of exchange and of property, a society that has conjured up "
            "such gigantic means of production and of exchange, is like "
            "the sorcerer who is no longer able to control the powers of "
            "the nether world whom he has called up by his spells. "
            "The weapons with which the bourgeoisie felled feudalism to "
            "the ground are now turned against the bourgeoisie itself. "
            "But not only has the bourgeoisie forged the weapons that "
            "bring it death; it has also called into existence the men "
            "who are to wield those weapons — the modern working class — "
            "the proletarians. "
            "The proletarians have nothing to lose but their chains. "
            "They have a world to win. Working men of all countries, "
            "unite!"
        ),
    },
    "marx": {
        "title": "Das Kapital (Excerpt)",
        "text": (
            "The wealth of those societies in which the capitalist mode "
            "of production prevails, presents itself as an immense "
            "accumulation of commodities. Its unit is therefore a single "
            "commodity. Our investigation must therefore begin with the "
            "analysis of a commodity. "
            "A commodity is, in the first place, an object outside us, "
            "a thing that by its properties satisfies human wants of some "
            "sort or another. The nature of such wants, whether, for "
            "instance, they spring from the stomach or from fancy, makes "
            "no difference. "
            "The usefulness of a thing makes it a use value. But this "
            "usefulness is not a thing apart from the object. The commodity "
            "itself, as an object with properties, is a use value or a "
            "article of utility. "
            "If we abstract from the utility of commodities, they have "
            "only one common property left — that of being products of "
            "labour. A definite quantity of congealed labour-time. "
            "The value of a commodity is determined by the total amount "
            "of social labour necessary to produce it. The magnitude of "
            "value of a commodity is determined by the quantity of the "
            "substance of the values — of the labour contained in it. "
            "The value of a commodity has a relative form of expression, "
            "a relative value, which is expressed by its exchangeability "
            "with other commodities. "
            "Commodities come into the world in the shape of use-values, "
            "or articles of property. The exchange of commodities implies "
            "a double alienation of the commodity from its owner."
        ),
    },
    "plato": {
        "title": "The Republic",
        "text": (
            "I went down yesterday to the Piraeus with Glaucon the son of "
            "Ariston, that I might offer up my prayers to the goddess; "
            "and also because I wanted to see in what manner they would "
            "celebrate the festival, which was a new thing. I was delighted "
            "with the procession of the inhabitants; but that of the "
            "Thracians was equally, if not more, beautiful. "
            "And what is our conclusion about justice? Is it merely the "
            "conventional language of society, or does it have an "
            "independent existence? We maintain that it does have an "
            "independent existence in the soul of every man. "
            "Until philosophers are kings, or the kings and princes of "
            "this world have the spirit and power of philosophy, cities "
            "will never cease from ill — no, nor the human race. "
            "And now, Glaucon, that we have come to an agreement that "
            "philosophers are those who grasp the eternal and immutable, "
            "and those who wander among the multitude of particulars are "
            "not philosophers — what follows? "
            "The soul of man is divided into three parts: reason, spirit, "
            "and appetite. When each part performs its proper function, "
            "the soul is just. Justice in the individual mirrors justice "
            "in the city. "
            "The story of the cave — behold, human beings living in an "
            "underground cave, which has a mouth open towards the light. "
            "Here they have been from their childhood, and have their legs "
            "and necks chained so that they cannot move, and can only see "
            "before them, being prevented by the chains from turning round "
            "their heads. "
            "And what do you think these people would say about appearances? "
            "To them, the truth would be literally nothing but the shadows "
            "of the images. "
            "Now consider what would happen if one of them were freed from "
            "his chains and compelled to stand up suddenly and turn his "
            "head round and walk toward the light. He would suffer sharp "
            "pains, and the glare would distress him, and he would not be "
            "able to see the realities of which in his former state he "
            "had seen the shadows."
        ),
    },
    "nietzsche": {
        "title": "Thus Spoke Zarathustra",
        "text": (
            "When Zarathustra was thirty years old, he left his home and "
            "the lake of his home, and went into the mountains. There he "
            "enjoyed his spirit and his solitude, and for ten years did "
            "not weary of it. But at last his heart changed — and rising "
            "one morning with the rosy dawn, he went before the sun, and "
            "spoke thus unto it: "
            "Thou great star! What would be thy happiness if thou hadst "
            "not those for whom thou shinest! For ten years hast thou "
            "come up hither to my cave: thou wouldst have wearied of it "
            "without me, my eagle, and my serpent. "
            "Behold, I am weary of my wisdom, like the bee that hath "
            "gathered too much honey; I need hands outstretched to take "
            "it. I would fain bestow and distribute, until the wise have "
            "once more become joyous in their folly, and the poor happy "
            "in their riches. "
            "God is dead. God remains dead. And we have killed him. "
            "How shall we comfort ourselves, the murderers of all murderers? "
            "What was holiest and mightiest of all that the world has yet "
            "owned has bled to death under our knives: who will wipe this "
            "blood from us? What water is there for us to clean ourselves? "
            "What festivals of atonement, what sacred games shall we have "
            "to invent? Is not the greatness of this deed too great for us? "
            "Must we ourselves not become gods simply to appear worthy of it? "
            "I teach you the overman. Man is something that shall be "
            "overcome. What have ye done to overcome him? All beings "
            "hitherto have created something beyond themselves: and ye "
            "want to be the ebb of this great flood, and even go back "
            "to the beast rather than overcome man? "
            "Man is a rope, tied between beast and overman — a rope over "
            "an abyss. What is great in man is that he is a bridge and "
            "not an end: that can be loved in man, that he is an overture "
            "and a going under. "
            "The will to power is the will of life. All living things are "
            "the will to power — and not merely self-preservation, as "
            "Darwin would have us believe. The desire for power is the "
            "fundamental instinct of all things."
        ),
    },
    "confucius": {
        "title": "The Analects",
        "text": (
            "The Master said: Is it not pleasant to learn with a constant "
            "perseverance and delight? Is it not delightful to have friends "
            "coming from distant quarters? Is he not a man of complete "
            "virtue, who feels no discomposure though men may take no note "
            "of him? "
            "The Master said: It is rare, indeed, for a man with cunning "
            "words and a flattering appearance to be benevolent. "
            "Tseng Tzu said: I daily examine myself on three points: "
            "whether I have been unfaithful in planning for others; whether "
            "I have been unreliable in dealing with friends; and whether "
            "I have failed to practice what I have been taught. "
            "The Master said: He who learns but does not think is lost. "
            "He who thinks but does not learn is in great danger. "
            "The Master said: By nature, men are nearly alike; by practice, "
            "they get to be wide apart. "
            "The Master said: At fifteen I set my heart on learning. "
            "At thirty I stood firm. At forty I had no doubts. At fifty "
            "I knew the decrees of Heaven. At sixty my ear was obedient. "
            "At seventy I follow what my heart desires without transgressing "
            "the norm. "
            "The Master said: If you govern the people by laws and keep "
            "them in order by punishments, they will evade their punishments, "
            "but have no sense of shame. If you govern them by virtue and "
            "keep them in order by the rules of propriety, they will have "
            "a sense of shame, and moreover, they will become good. "
            "The Master said: The gentleman understands what is right; "
            "the small man understands what is profitable."
        ),
    },
}

_QURAN_API_BASE = "https://api.quran.com/api/v4"

_BIBLE_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers",
    "Deuteronomy", "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "Psalms", "Proverbs", "Ecclesiastes",
    "Isaiah", "Jeremiah", "Matthew", "Mark",
    "Luke", "John", "Acts", "Romans", "Revelation",
]


def _load_hardcoded(source_key: str) -> list[Document]:
    """Load a hardcoded text from the _TEXTS dict by its key."""
    info = _TEXTS.get(source_key)
    if info is None:
        return []
    return [
        Document(
            source=source_key,
            title=info["title"],
            text=_normalize(info["text"]),
            metadata={"origin": "inline"},
        )
    ]


def load_constitution() -> list[Document]:
    return _load_hardcoded("constitution")


def load_communist_manifesto() -> list[Document]:
    return _load_hardcoded("communist_manifesto")


def load_marx() -> list[Document]:
    return _load_hardcoded("marx")


def load_plato() -> list[Document]:
    return _load_hardcoded("plato")


def load_nietzsche() -> list[Document]:
    return _load_hardcoded("nietzsche")


def load_confucius() -> list[Document]:
    return _load_hardcoded("confucius")


def load_quran() -> list[Document]:
    """Fetch the full Quran from the Quran.com API, one chapter per Document."""
    try:
        resp = requests.get(
            f"{_QURAN_API_BASE}/chapters?language=en",
            timeout=30,
        )
        resp.raise_for_status()
        chapters = resp.json()["chapters"]
    except requests.RequestException as exc:
        return [
            Document(
                source="quran",
                title="API Unavailable",
                text=f"Failed to fetch from Quran API: {exc}",
                metadata={"status": "error"},
            )
        ]
    docs: list[Document] = []
    for chapter in chapters:
        chapter_id = chapter["id"]
        try:
            url = (
                f"{_QURAN_API_BASE}/verses/by_chapter/"
                f"{chapter_id}?language=en&words=false&translations=131"
            )
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            verses = resp.json()["verses"]
            lines = []
            for v in verses:
                for t in v.get("translations", []):
                    t_text = t.get("text", "")
                    t_text = re.sub(r"<[^>]+>", "", t_text)
                    lines.append(t_text)
                    break
            text = _normalize("\n".join(lines))
        except requests.RequestException:
            text = "[Failed to fetch]"
        docs.append(
            Document(
                source="quran",
                title=chapter.get("name_simple", f"Chapter {chapter_id}"),
                text=text,
                metadata={
                    "chapter_number": chapter_id,
                    "revelation_place": chapter.get("revelation_place", ""),
                },
            )
        )
    return docs


def load_bible() -> list[Document]:
    """Fetch Bible books from bible-api.com (World English Bible, public domain)."""
    docs: list[Document] = []
    for book_name in _BIBLE_BOOKS:
        try:
            url = f"https://bible-api.com/{book_name}?translation=web"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            docs.append(
                Document(
                    source="bible",
                    title=book_name,
                    text=_normalize(data.get("text", "")),
                    metadata={"translation": "web"},
                )
            )
        except requests.RequestException:
            docs.append(
                Document(
                    source="bible",
                    title=book_name,
                    text="[Failed to fetch]",
                    metadata={"translation": "web", "status": "error"},
                )
            )
    return docs if docs else [
        Document("bible", "Fallback", "Bible API unavailable")
    ]


def load_gutenberg() -> list[Document]:
    """Download texts from Project Gutenberg via nltk."""
    try:
        import nltk
    except ImportError:
        raise ImportError(
            "nltk required for Gutenberg corpus: pip install nltk"
        )
    nltk.download("gutenberg", quiet=True)

    fileids = nltk.corpus.gutenberg.fileids()
    docs: list[Document] = []
    for gid in sorted(fileids):
        try:
            raw = nltk.corpus.gutenberg.raw(gid)
        except Exception:
            continue
        title = gid.replace(".txt", "").replace("_", " ").title()
        docs.append(
            Document(
                source="gutenberg",
                title=title,
                text=_normalize(raw),
                metadata={"gutenberg_id": gid},
            )
        )
    return docs if docs else [
        Document("gutenberg", "Fallback", "Gutenberg corpus unavailable")
    ]


# ── Utility ────────────────────────────────────────────────────────


def _normalize(text: str) -> str:
    """Collapse runs of whitespace into single spaces, strip."""
    text = re.sub(r"[\r\n]+", "\n", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    return text.strip()
