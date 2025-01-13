class FallbackRouter:
    def db_for_read(self, model, **hints):
        # Wenn eine Leseanfrage kommt, verwende die Fallback-Datenbank
        return 'fallback'

    def db_for_write(self, model, **hints):
        # Wenn eine Schreibanfrage kommt, verwende die Hauptdatenbank
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Erlaube Beziehungen zwischen Objekten in beiden Datenbanken
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Synchronisiere die Migrationsänderungen nur mit der Hauptdatenbank
        if db == 'default':
            return True
        return False
