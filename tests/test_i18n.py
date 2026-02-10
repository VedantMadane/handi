import unittest
from app.i18n import get_translations
from babel.support import Translations, NullTranslations

class TestI18n(unittest.TestCase):
    def test_get_translations_returns_translations(self):
        """Verify get_translations returns a valid Translations object."""
        # Using a locale that exists might return Translations, 'en' returns NullTranslations
        translations = get_translations("es")
        # It should be either Translations or NullTranslations
        self.assertTrue(isinstance(translations, (Translations, NullTranslations)))
        # It must have gettext method
        self.assertTrue(hasattr(translations, 'gettext'))

    def test_caching_behavior(self):
        """Verify that repeated calls return the same object instance (caching)."""
        t1 = get_translations("es")
        t2 = get_translations("es")

        # This assertion will fail until caching is implemented
        self.assertIs(t1, t2, "Translations should be cached and return the same object instance.")

    def test_different_locales(self):
        """Verify different locales return different translation objects."""
        t_en = get_translations("en")
        t_es = get_translations("es")
        self.assertIsNot(t_en, t_es)

if __name__ == '__main__':
    unittest.main()
