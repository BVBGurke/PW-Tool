"""Lokale Sicherheitsbewertung für bereits generierte Passwörter.

Die Bewertung überträgt keine Werte und schreibt weder Passwörter noch abgeleitete
Entropie in Dateien. Sie beschreibt nur Mindestlänge, gewählten Zeichenvorrat und
eine theoretische Kombinationsgröße; sie ist kein Ersatz für ein Angriffsmodell.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from password_engine import CharacterSet, PasswordGenerator


@dataclass(frozen=True)
class PasswordSecurityReport:
    """Nicht sensibles Ergebnis einer lokalen Passwort-Sicherheitsbewertung."""

    profile_name: str
    password_count: int
    minimum_length: int
    alphabet_size: int
    estimated_entropy_bits: float
    rating: str
    all_distinct: bool
    all_passwords_have_expected_classes: bool
    advice: str

    def as_text(self) -> str:
        """Rendert ausschließlich nicht sensitive Metadaten für die TUI."""
        class_status = "ja" if self.all_passwords_have_expected_classes else "nein"
        distinct_status = "ja" if self.all_distinct else "nein"
        return "\n".join(
            (
                "Sicherheitscheck (nur lokal)",
                f"Profil: {self.profile_name}",
                f"Passwörter: {self.password_count}; kürzeste Länge: {self.minimum_length}",
                f"Zeichenvorrat: {self.alphabet_size} Zeichen; geschätzt: ca. {self.estimated_entropy_bits:.0f} Bit",
                f"Zeichenklassen je Passwort vorhanden: {class_status}; unterschiedliche Werte: {distinct_status}",
                f"Bewertung: {self.rating}",
                f"Hinweis: {self.advice}",
            )
        )


def _has_expected_classes(password: str, charset: CharacterSet) -> bool:
    """Prüft die Zeichenklassen, die zum ausgewählten Generatoralphabet gehören."""
    has_lower = any(character.islower() for character in password)
    has_upper = any(character.isupper() for character in password)
    has_digit = any(character.isdigit() for character in password)
    if charset == CharacterSet.NORMAL:
        return has_lower and has_upper and has_digit

    has_special = any(
        character in PasswordGenerator.CHARS_COMPLETE
        and not character.isalnum()
        for character in password
    )
    return has_lower and has_upper and has_digit and has_special


def assess_generated_passwords(
    passwords: tuple[str, ...],
    charset: CharacterSet,
) -> PasswordSecurityReport:
    """Bewertet die schwächste Länge eines lokalen Generierungsbatches.

    Die Entropieschätzung setzt voraus, dass die Werte durch den lokalen Generator
    mit gleichverteilter Auswahl aus dem gewählten Zeichenvorrat entstanden sind.
    Sie bewertet keine Wiederverwendung, keinen Zielservice und keine externen
    Datenlecks.
    """
    if not passwords:
        raise ValueError("At least one password is required for a security check")

    alphabet_size = len(PasswordGenerator.get_character_set(charset))
    minimum_length = min(len(password) for password in passwords)
    estimated_entropy_bits = minimum_length * math.log2(alphabet_size)
    all_distinct = len(set(passwords)) == len(passwords)
    all_passwords_have_expected_classes = all(
        _has_expected_classes(password, charset) for password in passwords
    )

    if minimum_length < 16 or estimated_entropy_bits < 80:
        rating = "schwach"
        advice = "Für neue Konten mindestens 16 Zeichen verwenden."
    elif minimum_length < 20 or estimated_entropy_bits < 112:
        rating = "ausreichend"
        advice = "Für wichtige Konten mindestens 20 Zeichen und den vollständigen Zeichenvorrat wählen."
    else:
        rating = "stark"
        advice = "Für jeden Dienst einen eigenen, nicht wiederverwendeten Wert verwenden."

    if not all_distinct:
        advice = "Der Batch enthält gleiche Werte; bitte neue Passwörter erzeugen."

    profile_name = (
        "maximal zufällig (direkter OS-CSPRNG)"
        if charset is CharacterSet.MAXIMUM
        else "vollständiger Zeichenvorrat"
        if charset is CharacterSet.COMPLETE
        else "kompatibler Zeichenvorrat"
    )

    return PasswordSecurityReport(
        profile_name=profile_name,
        password_count=len(passwords),
        minimum_length=minimum_length,
        alphabet_size=alphabet_size,
        estimated_entropy_bits=estimated_entropy_bits,
        rating=rating,
        all_distinct=all_distinct,
        all_passwords_have_expected_classes=all_passwords_have_expected_classes,
        advice=advice,
    )
