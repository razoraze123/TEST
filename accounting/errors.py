class ComptaError(Exception):
    """Exception de base pour les erreurs comptables.

    ---

    Base exception for accounting errors.
    """


class ComptaImportError(ComptaError):
    """Erreur lors de l'import de données.

    ---

    Error while importing data.
    """


class ComptaValidationError(ComptaError):
    """Erreur de validation des données.

    ---

    Data validation error.
    """


class ComptaExportError(ComptaError):
    """Erreur lors de l'export de données.

    ---

    Error while exporting data.
    """
