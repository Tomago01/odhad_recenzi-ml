import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import json

DATA_FILE = "data/reviews.csv"
PROGRESS_FILE = "data/progress.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "cs-CZ,cs;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# 241 overených filmů ze žebříčků CSFD
# Top 1-46 (nejlepsi), Top 100-199 (nejlepsi), Nejhorsi 1-99
FILMS = [
    # === TOP 1-46 (nejlepsi filmy) ===
    (2294, "vykoupeni-z-veznice-shawshank"),
    (10135, "forrest-gump"),
    (2292, "zelena-mile"),
    (2671, "sedm"),
    (2982, "prelet-nad-kukaccim-hnizdem"),
    (8653, "schindleruv-seznam"),
    (1644, "kmotr"),
    (6178, "dvanact-rozhnevanych-muzu"),
    (306731, "nedotknutelni"),
    (4570, "pelisky"),
    (1248, "terminator-2-den-zuctovani"),
    (8852, "pulp-fiction-historky-z-podsveti"),
    (4711, "pan-prstenu-spolecenstvo-prstenu"),
    (4712, "pan-prstenu-navrat-krale"),
    (1645, "kmotr-ii"),
    (223734, "temny-rytir"),
    (2356, "mlceni-jehnatek"),
    (5911, "tenkrat-na-zapade"),
    (9499, "matrix"),
    (240479, "gran-torino"),
    (5910, "hodny-zly-a-osklivy"),
    (8650, "dobyvatele-ztracene-archy"),
    (5954, "rain-man"),
    (18780, "sedm-statecnych"),
    (5342, "vyssi-princip"),
    (8641, "indiana-jones-a-posledni-krizova-vyprava"),
    (8265, "vetrelec"),
    (332773, "le-mans-66"),
    (301401, "rivalove"),
    (6642, "smrtonosna-past"),
    (1245, "vetrelci"),
    (15046, "podraz"),
    (8652, "zachrante-vojina-ryana"),
    (821, "s-certy-nejsou-zerty"),
    (773, "leon"),
    (5992, "marecku-podejte-mi-pero"),
    (2971, "amadeus"),
    (8806, "obecna-skola"),
    (5238, "star-wars-epizoda-v-imperium-vraci-uder"),
    (4713, "pan-prstenu-dve-veze"),
    (4123, "l-a-prisne-tajne"),
    (3092, "cesta-do-hlubin-studakovy-duse"),
    (15031, "butch-cassidy-a-sundance-kid"),
    (10128, "navrat-do-budoucnosti"),
    (8271, "gladiator"),
    (254156, "pocatek"),
    # === TOP 100-199 (nejlepsi filmy) ===
    (8283, "posledni-skaut"),
    (22205, "princezna-mononoke"),
    (7827, "frajer-luke"),
    (792366, "spider-man-napric-paralelnimi-svety"),
    (901, "trainspotting"),
    (9568, "truman-show"),
    (23443, "svetaci"),
    (168, "medved"),
    (117077, "hanebny-pancharti"),
    (42136, "cesta-do-fantazie"),
    (3157, "skola-zaklad-zivota"),
    (600912, "zelena-kniha"),
    (1098951, "duna-cast-druha"),
    (5435, "sedm-samuraju"),
    (8541, "jara-cimrman-lezici-spici"),
    (224384, "americky-gangster"),
    (7698, "sbal-prachy-a-vypadni"),
    (2335, "zjizvena-tvar"),
    (136224, "batman-zacina"),
    (8545, "vrchni-prchni"),
    (8266, "cerny-jestrab-sestrelen"),
    (6648, "predator"),
    (3311, "12-opic"),
    (16103, "rocky"),
    (45608, "osudovy-dotek"),
    (4999, "obchod-na-korze"),
    (1000488, "trinact-zivotu"),
    (6995, "memento"),
    (6741, "lvi-kral"),
    (2439, "smrtonosna-zbran-2"),
    (83776, "snehurka-a-sedm-trpasliku"),
    (10102, "carodejuv-ucen"),
    (7222, "ponorka"),
    (1628, "sam-doma"),
    (252669, "temny-rytir-povstal"),
    (5915, "pro-par-dolaru-navic"),
    (234768, "jak-vycvicit-draka"),
    (307556, "na-hrane-zitrka"),
    (182289, "hotel-rwanda"),
    (286035, "top-gun-maverick"),
    (10125, "vynalez-zkazy"),
    (9430, "tri-orisky-pro-popelku"),
    (8543, "nejista-sezona"),
    (8644, "jursky-park"),
    (3094, "cisaruv-pekar-pekaruv-cisar"),
    (2668, "hra"),
    (257071, "zmizeni"),
    (8668, "dobry-vojak-svejk"),
    (4978, "smrt-krasnych-srncu"),
    (5401, "olovena-vesta"),
    (277770, "cernobily-svet"),
    (6251, "sloni-muz"),
    (43924, "hleda-se-nemo"),
    (8805, "kolja"),
    (5991, "limonadovy-joe-aneb-konska-opera"),
    (23587, "zivot-briana"),
    (675173, "gentlemani"),
    (9558, "spolecnost-mrtvych-basniku"),
    (5696, "most-pres-reku-kwai"),
    (2428, "zpivani-v-desti"),
    (150988, "ratatouille-dobru-chut"),
    (221020, "skryta-identita"),
    (10129, "navrat-do-budoucnosti-ii"),
    (1634, "apokalypsa"),
    (7123, "pink-floyd-the-wall"),
    (2315, "carlitova-cesta"),
    (1474749, "rozzum-v-divocine"),
    (419102, "tvoje-jmeno"),
    (1625, "harry-potter-a-vezen-z-azkabanu"),
    (393331, "avengers-nekonecna-vojna"),
    (8853, "gauneri"),
    (54763, "spider-man-paralelni-svety"),
    (4786, "vsichni-dobri-rodaci"),
    (1482, "kid"),
    (1279, "zivot-je-krasny"),
    (269587, "kralova-rec"),
    (6670, "slavnosti-snezenek"),
    (32107, "cetnik-ze-saint-tropez"),
    (10995, "svet-podle-prota"),
    (8680, "poslusne-hlasim"),
    (4983, "ucho"),
    (8505, "nebe-a-dudy"),
    (189557, "obchodnik-se-smrti"),
    (546, "skala"),
    (18184, "toy-story-pribeh-hracek"),
    (1329, "vec"),
    (358992, "whiplash"),
    (4562, "ceska-soda"),
    (8815, "prednosta-stanice"),
    (5475, "duchacek-to-zaridi"),
    (4386, "okno-do-dvora"),
    (1472, "diktator"),
    (43677, "laska-nebeska"),
    (18113, "agent-bez-minulosti"),
    (136076, "bournuv-mytus"),
    (16097, "rambo-prvni-krev"),
    (18777, "velky-utek"),
    # === NEJHORSI filmy 1-99 (pro negativni recenze) ===
    (264179, "maly-herkules"),
    (42816, "waterloo-po-cesku"),
    (7050, "playgirls-ii"),
    (174182, "supersmradi-mali-geniove-2"),
    (29952, "plump-fiction"),
    (279546, "titanic-ii"),
    (189983, "trhni-si"),
    (215217, "invaze-svetu"),
    (89504, "panika-ve-vzduchu"),
    (484028, "dokonaly-polibek"),
    (8597, "jak-ukrast-dagmaru"),
    (150282, "octopus-2"),
    (1268501, "cool-girl"),
    (20355, "mali-geniove"),
    (239161, "2012-soudny-den"),
    (74686, "3-nindzove-v-zabavnim-parku"),
    (215254, "panic-je-nanic"),
    (26960, "nexus"),
    (319022, "posledni-vykrik"),
    (7049, "playgirls"),
    (2660, "nebat-se-a-nakrast"),
    (10780, "turbulence-2-strach-z-letani"),
    (12016, "blanche-kralovna-zbojniku"),
    (10755, "prdosi"),
    (241321, "jurske-komando"),
    (49214, "pavouci-2"),
    (167300, "pes-fotbalista-evropsky-pohar"),
    (42742, "lidozrout"),
    (240359, "pribehy-ze-zivota-alzbety-knezny-cachticke"),
    (216279, "cesta-upiru-van-helsing-vs-dracula"),
    (40135, "orient-expres"),
    (34890, "pan-prevleku"),
    (601777, "kdyz-draka-boli-hlava"),
    (20105, "kod-omega"),
    (240892, "tyranosaurus-zhouba-azteku"),
    (257343, "nezlobte-mimozemstany"),
    (503963, "jak-se-mori-revizori"),
    (142848, "bili-zabijaci"),
    (15429, "dna-stvoreni-netvora"),
    (73699, "vlad-narazec"),
    (88070, "python-2"),
    (88782, "maximalni-turbulence"),
    (164926, "krokodyl-2"),
    (9950, "mrtvy-bod"),
    (1518669, "krtkuv-svet"),
    (248178, "transformers-recyklace"),
    (343970, "decibely-lasky"),
    (235792, "krveziznive-opice"),
    (13178, "panika"),
    (4490, "krokodyl"),
    (91860, "laska-mezi-superstar"),
    (93095, "digimon"),
    (42741, "zralok-utoci-2"),
    (140580, "lovec-zraloku"),
    (346744, "maturita"),
    (1442802, "princezna-na-hrasku"),
    (14855, "mlady-draci-ninja-2"),
    (355312, "monstrum-z-hlubin"),
    (17222, "celisti-pomsta"),
    (600922, "teambuilding"),
    (257805, "ocelovy-muz"),
    (404534, "vanocni-kamenak"),
    (9058, "kanarska-spojka"),
    (220058, "crash-road"),
    (224830, "saxana-a-lexikon-kouzel"),
    (231571, "transmorphers"),
    (331378, "hurikan-smrti"),
    (901759, "vsude-dobre-sam-doma-nejlip"),
    (8589, "byl-jednou-jeden-polda-iii-major-maisner-a-tancici-drak"),
    (235645, "zabijak-bez-tvare"),
    (131733, "megalodon"),
    (276171, "immortalitas"),
    (243043, "disaster-movie"),
    (279140, "navrat-cerneho-rytire"),
    (240590, "valka-svetu-2-dalsi-vlna"),
    (120687, "air-marshal"),
    (140579, "octopus"),
    (108847, "divoke-pivo"),
    (223872, "blondata-a-blondatejsi"),
    (14505, "falesny-unos"),
    (71486, "unik-z-alcatrazu"),
    (310843, "jurassic-shark"),
    (229516, "smrtici-temnota"),
    (162926, "ledova-planeta"),
    (236019, "vetrelec-vs-lovec"),
    (229857, "cepel-smrti"),
    (20641, "krysy"),
    (291650, "bitva-o-los-angeles"),
    (221083, "duch-podzemi"),
    (257481, "terminatori"),
    (279581, "viva-high-school-musical-mexiko"),
    (34147, "bohove-musi-byt-v-cine-legracni"),
    (283404, "megazralok-versus-crocosaurus"),
    (83079, "operace-boeing-747"),
    (131364, "tygri-srdce"),
    (21597, "poklad-piratu"),
    (341860, "navrat-vrazdicich-bestii"),
    (292500, "gladiatori-z-pekla"),
]

FIELDNAMES = ["text", "stars", "sentiment", "film_id"]


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"film_index": 0, "total": 0, "positive": 0, "negative": 0}


def save_progress(index, total, positive, negative):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({
            "film_index": index,
            "total": total,
            "positive": positive,
            "negative": negative,
        }, f)


def load_seen_texts():
    seen = set()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                seen.add(row["text"][:100])
    print(f"Nacteno {len(seen)} existujicich recenzi pro deduplikaci")
    return seen


def append_to_csv(review):
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(review)


def scrape_film_reviews(film_id, film_slug, seen_texts, page=1):
    url = f"https://www.csfd.cz/film/{film_id}-{film_slug}/recenze/"
    if page > 1:
        url += f"?page={page}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}")
            return [], False
    except Exception as e:
        print(f"  Chyba: {e}")
        return [], False

    soup = BeautifulSoup(resp.text, "html.parser")
    reviews = []

    articles = soup.find_all("article", attrs={"data-film-review": True})

    for article in articles:
        comment = article.find("span", class_="comment")
        if not comment:
            continue
        text = comment.get_text(strip=True)

        if len(text) < 100:
            continue

        key = text[:100]
        if key in seen_texts:
            continue

        stars_span = article.find(
            "span", class_=lambda c: c and c.startswith("stars stars-")
        )
        if not stars_span:
            continue

        classes = stars_span.get("class", [])
        stars = None
        for cls in classes:
            if cls.startswith("stars-") and cls != "stars-":
                try:
                    stars = int(cls.split("-")[1])
                    break
                except:
                    continue

        if stars is None:
            continue

        if stars == 3:
            continue

        # Ukládáme pouze negativní recenze (1-2 hvězdičky)
        if stars >= 4:
            continue

        sentiment = "negative"

        seen_texts.add(key)
        reviews.append({
            "text": text,
            "stars": stars,
            "sentiment": sentiment,
            "film_id": film_id,
        })

    has_next = bool(soup.find("a", class_="page-next")) or bool(
        soup.find("a", string=lambda t: t and "dalsi" in t.lower())
    )

    return reviews, has_next


def main():
    os.makedirs("data", exist_ok=True)

    progress = load_progress()
    start_index = progress["film_index"]
    total = progress["total"]
    positive = progress["positive"]
    negative = progress["negative"]

    seen_texts = load_seen_texts()

    print(f"Startuji od filmu {start_index}/{len(FILMS)}, zatim {total} recenzi ({positive} pos, {negative} neg)")

    for i, (film_id, film_slug) in enumerate(FILMS):
        if i < start_index:
            continue

        print(f"\nFilm {i+1}/{len(FILMS)}: {film_slug} (id={film_id})")

        page = 1
        while True:
            reviews, has_next = scrape_film_reviews(film_id, film_slug, seen_texts, page)

            for r in reviews:
                append_to_csv(r)
                total += 1
                negative += 1

            print(f"  Stranka {page}: {len(reviews)} novych | Celkem: {total} (pos={positive}, neg={negative})")

            if not has_next or page >= 10:
                break

            page += 1
            time.sleep(1.5)

        save_progress(i + 1, total, positive, negative)
        time.sleep(2)

    print(f"\nHotovo! Celkem {total} recenzi ({positive} pozitivnich, {negative} negativnich)")


if __name__ == "__main__":
    main()
