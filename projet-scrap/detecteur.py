from bs4 import BeautifulSoup
from cerveau import analyser_requete


def generer_selecteur(tag) -> str:
    """Retourne un sélecteur CSS simple pour un tag BeautifulSoup."""
    if tag.get("id"):
        return f"#{tag['id']}"
    if tag.get("class"):
        return f"{tag.name}.{' '.join(tag.get('class'))}"
    return tag.name


def detecter_selecteur(html: str, question: str) -> str:
    """Détecte l'élément correspondant à la question et renvoie un sélecteur."""
    type_cible = analyser_requete(question)
    soup = BeautifulSoup(html, "html.parser")

    if type_cible == "lien":
        element = soup.find("a")
    elif type_cible == "titre":
        element = soup.find(["h1", "h2", "h3"])
    else:
        element = None

    if not element:
        return ""
    return generer_selecteur(element)
