class ComptaError(Exception):
    """Exception de base pour les erreurs comptables."""


class ComptaImportError(ComptaError):
    """Erreur lors de l'import de données."""


class ComptaValidationError(ComptaError):
    """Erreur de validation des données."""


class ComptaExportError(ComptaError):
    """Erreur lors de l'export de données."""
