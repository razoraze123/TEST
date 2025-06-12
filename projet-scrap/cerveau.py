from transformers import pipeline

_classifier = None


def _get_classifier():
    global _classifier
    if _classifier is None:
        # DistilBERT zero-shot-classification pipeline
        _classifier = pipeline("zero-shot-classification", model="distilbert-base-uncased")
    return _classifier


def analyser_requete(question: str) -> str:
    """Analyse la question utilisateur et renvoie le type de cible."""
    classifier = _get_classifier()
    labels = ["lien", "titre"]
    result = classifier(question, labels)
    return result["labels"][0]
