import sqlite3
import requests
import re
from bs4 import BeautifulSoup
from disease_db import search_and_print


# =========================================================
# AAYURVIDHI HEALTHCARE SEARCH SYSTEM
# =========================================================

DB_PATH = "data/healthcare.db"

HEADERS = {
    "User-Agent": "AayurvidhiHealthcareSystem/1.0"
}

MEDLINE_SEARCH = "https://wsearch.nlm.nih.gov/ws/query"

TIMEOUT = 15


# =========================================================
# NON-MEDICAL WORDS
# =========================================================

NON_MEDICAL = {
    "football", "cricket", "basketball", "tennis",
    "badminton", "hockey", "volleyball",
    "movie", "movies", "song", "songs", "music",
    "weather", "politics", "election",
    "python", "javascript", "programming", "coding",
    "github", "computer", "laptop",
    "iphone", "android",
    "pizza", "recipe", "restaurant",
    "travel", "hotel",
    "college", "exam", "mathematics", "math",
    "physics", "chemistry", "history", "geography",
    "game", "gaming"
}


# =========================================================
# COMMON MEDICAL TOPIC ALIASES
# =========================================================

ALIASES = {

    "fever":
        "fever.html",

    "parkinson":
        "parkinsonsdisease.html",

    "parkinson disease":
        "parkinsonsdisease.html",

    "parkinsons disease":
        "parkinsonsdisease.html",

    "multiple sclerosis":
        "multiplesclerosis.html",

    "ms":
        "multiplesclerosis.html",

    "diabetes":
        "diabetes.html",

    "diabetes mellitus":
        "diabetes.html",

    "hypertension":
        "highbloodpressure.html",

    "high blood pressure":
        "highbloodpressure.html",

    "asthma":
        "asthma.html",

    "migraine":
        "migraine.html",

    "pneumonia":
        "pneumonia.html",

    "osteoporosis":
        "osteoporosis.html",

    "lupus":
        "lupus.html",

    "glaucoma":
        "glaucoma.html",

    "endometriosis":
        "endometriosis.html",

    "leukemia":
        "leukemia.html",

    "kidney disease":
        "kidneydiseases.html",

    "kidney diseases":
        "kidneydiseases.html",

    "heart disease":
        "heartdiseases.html",

    "heart diseases":
        "heartdiseases.html",

    "liver disease":
        "liverdiseases.html",

    "liver diseases":
        "liverdiseases.html"
}


# =========================================================
# CLEAN TEXT
# =========================================================

def clean(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize(text):

    text = clean(text).lower()

    text = re.sub(
        r"[^\w\s-]",
        "",
        text
    )

    return clean(text)


# =========================================================
# NON-MEDICAL CHECK
# =========================================================

def is_non_medical(query):

    words = set(
        normalize(query).split()
    )

    return bool(
        words.intersection(
            NON_MEDICAL
        )
    )


# =========================================================
# LOCAL DATABASE
# =========================================================

def search_local(query):

    try:

        conn = sqlite3.connect(
            DB_PATH
        )

        cursor = conn.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        """)

        tables = [
            row[0]
            for row in cursor.fetchall()
        ]

        results = {}

        for table in tables:

            cursor.execute(
                f'PRAGMA table_info("{table}")'
            )

            columns = [
                row[1]
                for row in cursor.fetchall()
            ]

            if not columns:
                continue

            conditions = []
            values = []

            for column in columns:

                conditions.append(
                    f'LOWER(CAST("{column}" AS TEXT)) LIKE ?'
                )

                values.append(
                    "%" + query.lower() + "%"
                )

            sql = f"""
                SELECT *
                FROM "{table}"
                WHERE {" OR ".join(conditions)}
                LIMIT 10
            """

            try:

                cursor.execute(
                    sql,
                    values
                )

                rows = cursor.fetchall()

                if rows:
                    results[table] = rows

            except Exception:
                pass

        conn.close()

        return results

    except Exception:

        return {}


# =========================================================
# DOWNLOAD PAGE
# =========================================================

def get_page(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if response.status_code == 200:

            return response.text

    except Exception:

        pass

    return None


# =========================================================
# DIRECT MEDLINEPLUS PAGE
# =========================================================

def direct_medline_page(query):

    normalized = normalize(query)

    # -----------------------------------------------------
    # Known topics
    # -----------------------------------------------------

    if normalized in ALIASES:

        url = (
            "https://medlineplus.gov/"
            + ALIASES[normalized]
        )

        html = get_page(url)

        if html:

            return url, html

    # -----------------------------------------------------
    # Generic URL
    # -----------------------------------------------------

    slug = re.sub(
        r"[^a-z0-9]",
        "",
        normalized
    )

    possible = [
        f"https://medlineplus.gov/{slug}.html",
        f"https://medlineplus.gov/{slug}s.html"
    ]

    for url in possible:

        html = get_page(url)

        if not html:
            continue

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        h1 = soup.find("h1")

        if not h1:
            continue

        title = normalize(
            h1.get_text(
                " ",
                strip=True
            )
        )

        if (
            title == normalized
            or normalized in title
            or title in normalized
        ):

            return url, html

    return None


# =========================================================
# MEDLINEPLUS SEARCH API
# =========================================================

def search_medlineplus(
    query
):

    try:

        response = requests.get(
            MEDLINE_SEARCH,
            params={
                "db": "healthTopics",
                "term": query,
                "retmax": 20
            },
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if response.status_code != 200:

            return []

        soup = BeautifulSoup(
            response.text,
            "xml"
        )

        results = []

        for document in soup.find_all(
            "document"
        ):

            title = ""
            url = ""

            for content in document.find_all(
                "content"
            ):

                name = content.get(
                    "name",
                    ""
                ).lower()

                value = clean(
                    content.get_text(
                        " ",
                        strip=True
                    )
                )

                if name == "title":
                    title = value

                elif name == "url":
                    url = value

            if title and url:

                results.append({
                    "title": title,
                    "url": url
                })

        return results

    except Exception:

        return []


# =========================================================
# SEARCH FALLBACK
# =========================================================

def search_fallback(
    query
):

    results = search_medlineplus(
        query
    )

    wanted = normalize(query)

    # Exact match
    for result in results:

        title = normalize(
            result["title"]
        )

        if title == wanted:

            html = get_page(
                result["url"]
            )

            if html:

                return (
                    result["url"],
                    html
                )

    # Phrase match
    for result in results:

        title = normalize(
            result["title"]
        )

        if (
            wanted in title
            or title in wanted
        ):

            html = get_page(
                result["url"]
            )

            if html:

                return (
                    result["url"],
                    html
                )

    return None


# =========================================================
# FIND MEDICAL PAGE
# =========================================================

def find_medical_page(
    query
):

    # Direct first
    result = direct_medline_page(
        query
    )

    if result:

        return result

    # Search fallback
    return search_fallback(
        query
    )


# =========================================================
# EXTRACT PAGE INFORMATION
# =========================================================

def extract_information(
    html
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Remove unnecessary content
    for tag in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
        "header",
        "form"
    ]):

        tag.decompose()

    information = {}

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    h1 = soup.find("h1")

    if h1:

        information["title"] = clean(
            h1.get_text(
                " ",
                strip=True
            )
        )

    # -----------------------------------------------------
    # SECTION DEFINITIONS
    # -----------------------------------------------------

    section_names = {

        "summary":
            "Overview",

        "about":
            "Overview",

        "what is":
            "Overview",

        "causes":
            "Causes",

        "symptoms":
            "Symptoms",

        "signs and symptoms":
            "Symptoms",

        "treatment":
            "Treatment",

        "treatments":
            "Treatment",

        "treatments and therapies":
            "Treatment",

        "prevention":
            "Prevention",

        "risk factors":
            "Risk Factors",

        "complications":
            "Complications",

        "diagnosis":
            "Diagnosis",

        "diagnosis and tests":
            "Diagnosis",

        "tests":
            "Diagnosis",

        "when to call the doctor":
            "When to Seek Medical Help",

        "when to see a doctor":
            "When to Seek Medical Help",

        "when to seek medical help":
            "When to Seek Medical Help"
    }

    # -----------------------------------------------------
    # FIND HEADINGS
    # -----------------------------------------------------

    headings = soup.find_all(
        ["h2", "h3", "h4"]
    )

    for heading in headings:

        heading_text = clean(
            heading.get_text(
                " ",
                strip=True
            )
        )

        key = normalize(
            heading_text
        )

        category = section_names.get(
            key
        )

        if not category:
            continue

        pieces = []

        # -------------------------------------------------
        # Collect elements after heading
        # -------------------------------------------------

        element = heading.find_next_sibling()

        while element:

            if element.name in [
                "h1",
                "h2",
                "h3",
                "h4"
            ]:

                break

            # Paragraph
            if element.name == "p":

                text = clean(
                    element.get_text(
                        " ",
                        strip=True
                    )
                )

                if text:
                    pieces.append(
                        text
                    )

            # List
            elif element.name in [
                "ul",
                "ol"
            ]:

                for li in element.find_all(
                    "li"
                ):

                    text = clean(
                        li.get_text(
                            " ",
                            strip=True
                        )
                    )

                    if text:
                        pieces.append(
                            "• " + text
                        )

            # Other useful block
            elif element.name in [
                "div",
                "section"
            ]:

                text = clean(
                    element.get_text(
                        " ",
                        strip=True
                    )
                )

                if text and len(text) > 20:

                    pieces.append(
                        text
                    )

            element = (
                element.find_next_sibling()
            )

        if pieces:

            text = "\n".join(
                pieces
            )

            # Avoid duplicate sections
            if category not in information:

                information[category] = text

    # -----------------------------------------------------
    # FALLBACK OVERVIEW
    # -----------------------------------------------------

    if "Overview" not in information:

        main = (
            soup.find("main")
            or soup.find("article")
            or soup.body
        )

        if main:

            paragraphs = []

            for p in main.find_all(
                "p"
            ):

                text = clean(
                    p.get_text(
                        " ",
                        strip=True
                    )
                )

                if len(text) > 30:

                    paragraphs.append(
                        text
                    )

            if paragraphs:

                information["Overview"] = (
                    "\n".join(
                        paragraphs[:5]
                    )
                )

    return information


# =========================================================
# MEDICAL ENCYCLOPEDIA
# =========================================================

def encyclopedia_search(
    query
):

    try:

        response = requests.get(
            MEDLINE_SEARCH,
            params={
                "db": "medicalEncyclopedia",
                "term": query,
                "retmax": 10
            },
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if response.status_code != 200:

            return None

        soup = BeautifulSoup(
            response.text,
            "xml"
        )

        wanted = normalize(query)

        for document in soup.find_all(
            "document"
        ):

            title = ""
            url = ""

            for content in document.find_all(
                "content"
            ):

                name = content.get(
                    "name",
                    ""
                ).lower()

                value = clean(
                    content.get_text(
                        " ",
                        strip=True
                    )
                )

                if name == "title":
                    title = value

                elif name == "url":
                    url = value

            if (
                title
                and url
                and (
                    normalize(title) == wanted
                    or wanted in normalize(title)
                )
            ):

                html = get_page(
                    url
                )

                if html:

                    return url, html

    except Exception:

        pass

    return None


# =========================================================
# RXNORM
# =========================================================

def search_rxnorm(
    query
):

    try:

        response = requests.get(
            "https://rxnav.nlm.nih.gov/"
            "REST/rxcui.json",
            params={
                "name": query
            },
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:

            return []

        data = response.json()

        ids = (
            data
            .get("idGroup", {})
            .get("rxnormId", [])
        )

        results = []

        for rxcui in ids[:10]:

            url = (
                "https://rxnav.nlm.nih.gov/"
                f"REST/rxcui/{rxcui}/properties.json"
            )

            r = requests.get(
                url,
                headers=HEADERS,
                timeout=10
            )

            if r.status_code != 200:
                continue

            properties = (
                r.json()
                .get(
                    "properties",
                    {}
                )
            )

            if properties.get("name"):

                results.append({
                    "rxcui": rxcui,
                    "name": properties["name"],
                    "synonym": properties.get(
                        "synonym",
                        ""
                    )
                })

        return results

    except Exception:

        return []


# =========================================================
# DISPLAY LOCAL
# =========================================================

def display_local(
    results
):

    print(
        "\n[LOCAL AAYURVIDHI DATABASE]"
    )

    if not results:

        print(
            "No local matches found."
        )

        return

    for table, rows in results.items():

        print(
            f"\nTable: {table}"
        )

        for row in rows:

            print(
                "  ",
                row
            )


# =========================================================
# DISPLAY MEDICAL INFORMATION
# =========================================================

def display_information(
    information,
    source
):

    print(
        "\n[PATIENT INFORMATION]"
    )

    if not information:

        print(
            "Medical page found, but "
            "no readable sections were extracted."
        )

        print(
            "\nSource:"
        )

        print(
            source
        )

        return

    order = [
        "Overview",
        "Causes",
        "Symptoms",
        "Risk Factors",
        "Diagnosis",
        "Treatment",
        "Prevention",
        "Complications",
        "When to Seek Medical Help"
    ]

    for section in order:

        if section not in information:

            continue

        print(
            "\n" + "=" * 60
        )

        print(
            section
        )

        print(
            "=" * 60
        )

        print(
            information[section]
        )

    print(
        "\nSource:"
    )

    print(
        source
    )


# =========================================================
# DISPLAY MEDICINES
# =========================================================

def display_medicines(
    medicines
):

    if not medicines:
        return

    print(
        "\n[MEDICINE INFORMATION - RxNorm]"
    )

    for medicine in medicines:

        print(
            f"\nMedicine: {medicine['name']}"
        )

        print(
            f"RxCUI: {medicine['rxcui']}"
        )

        if medicine["synonym"]:

            print(
                f"Synonym: {medicine['synonym']}"
            )


# =========================================================
# MAIN SEARCH
# =========================================================

def search_healthcare_system(
    query
):

    query = query.strip()

    if search_and_print(query):
        return



    print(
        "\n" + "=" * 70
    )

    print(
        " AAYURVIDHI MEDICAL SEARCH"
    )

    print(
        "=" * 70
    )

    print(
        f"\nSearch: {query}"
    )

    # -----------------------------------------------------
    # EMPTY
    # -----------------------------------------------------

    if not query:

        print(
            "\nRESULT: NULL"
        )

        return

    # -----------------------------------------------------
    # NON-MEDICAL
    # -----------------------------------------------------

    if is_non_medical(query):

        print(
            "\nRESULT: NULL"
        )

        print(
            "This query is outside the "
            "medical/healthcare domain."
        )

        return

    # -----------------------------------------------------
    # LOCAL
    # -----------------------------------------------------

    local_results = search_local(
        query
    )

    display_local(
        local_results
    )

    # -----------------------------------------------------
    # MEDLINEPLUS
    # -----------------------------------------------------

    print(
        "\nSearching medical sources..."
    )

    page = find_medical_page(
        query
    )

    medical_information = None
    source = None

    if page:

        source, html = page

        medical_information = (
            extract_information(
                html
            )
        )

        # Make sure a title exists
        if "title" not in medical_information:

            medical_information[
                "title"
            ] = query.title()

        print(
            "\nMedical topic found:"
        )

        print(
            medical_information["title"]
        )

    # -----------------------------------------------------
    # MEDICAL ENCYCLOPEDIA FALLBACK
    # -----------------------------------------------------

    if not medical_information:

        encyclopedia = (
            encyclopedia_search(
                query
            )
        )

        if encyclopedia:

            source, html = encyclopedia

            medical_information = (
                extract_information(
                    html
                )
            )

            if "title" not in medical_information:

                medical_information[
                    "title"
                ] = query.title()

            print(
                "\nMedical Encyclopedia topic found:"
            )

            print(
                medical_information["title"]
            )

    # -----------------------------------------------------
    # RXNORM
    # -----------------------------------------------------

    medicines = search_rxnorm(
        query
    )

    # -----------------------------------------------------
    # NOTHING
    # -----------------------------------------------------

    if (
        not medical_information
        and not local_results
        and not medicines
    ):

        print(
            "\nRESULT: NULL"
        )

        print(
            "No relevant medical information "
            "was found."
        )

        return

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    if medical_information:

        display_information(
            medical_information,
            source
        )

    display_medicines(
        medicines
    )

    # -----------------------------------------------------
    # SAFETY
    # -----------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        "Aayurvidhi provides health "
        "information from medical sources."
    )

    print(
        "It does not diagnose diseases "
        "or prescribe medicines."
    )

    print(
        "-" * 70
    )


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":

    query = input(
        "\nEnter a disease, symptom, "
        "medical condition, body problem, "
        "or medicine: "
    )

    search_healthcare_system(
        query
    )