"""Validation qualité d'un enregistrement de prix, à l'ingestion (bronze).

Fonctions pures (aucune dépendance BDD/Kafka) : facilement testables et
réutilisables. `validate_record` renvoie la liste des raisons de rejet
(vide = enregistrement valide).

Forme attendue d'un message (cf. extract_producer) :
    source, currency, coin_id, price_usd, price_eur, price_gbp,
    change_24h, market_cap, timestamp
"""

import math
import re
from datetime import datetime, timedelta, timezone

# coin_id : minuscules/chiffres/tirets, 1 à 50 caractères (format CoinGecko).
_COIN_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,49}")

# Une variation sur 24 h ne peut pas descendre sous -100 % (prix >= 0). La borne
# haute est volontairement large : elle sert juste à attraper les valeurs absurdes.
CHANGE_MIN_PCT = -100.0
CHANGE_MAX_PCT = 10000.0

# Tolérance d'horloge : un timestamp légèrement dans le futur reste acceptable.
FUTURE_SKEW = timedelta(hours=1)


def _is_finite_number(value) -> bool:
    """True si value est un nombre réel fini (exclut bool, NaN, inf)."""
    if isinstance(value, bool):
        return False
    if not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


def parse_timestamp(value):
    """Parse un timestamp ISO 8601 en datetime naïf UTC, ou None si invalide."""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        text = value.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def validate_record(message: dict, *, now: datetime = None) -> list:
    """Retourne la liste des raisons de rejet (vide = valide)."""
    errors = []

    if not isinstance(message, dict):
        return ["message n'est pas un dict"]

    # coin_id — obligatoire, format CoinGecko
    coin_id = message.get("coin_id")
    if not coin_id or not isinstance(coin_id, str):
        errors.append("coin_id manquant ou non-string")
    elif not _COIN_ID_RE.fullmatch(coin_id):
        errors.append(f"coin_id de format invalide: {coin_id!r}")

    # price_usd — obligatoire, strictement positif
    price_usd = message.get("price_usd")
    if price_usd is None:
        errors.append("price_usd manquant (None)")
    elif not _is_finite_number(price_usd):
        errors.append(f"price_usd non numérique/fini: {price_usd!r}")
    elif price_usd <= 0:
        errors.append(f"price_usd <= 0: {price_usd}")

    # price_eur / price_gbp — optionnels, mais >= 0 si présents
    for key in ("price_eur", "price_gbp"):
        value = message.get(key)
        if value is None:
            continue
        if not _is_finite_number(value):
            errors.append(f"{key} non numérique/fini: {value!r}")
        elif value < 0:
            errors.append(f"{key} < 0: {value}")

    # change_24h — optionnel, dans une bande de sanité
    change = message.get("change_24h")
    if change is not None:
        if not _is_finite_number(change):
            errors.append(f"change_24h non numérique/fini: {change!r}")
        elif not (CHANGE_MIN_PCT <= change <= CHANGE_MAX_PCT):
            errors.append(f"change_24h hors bande [{CHANGE_MIN_PCT}, {CHANGE_MAX_PCT}]: {change}")

    # market_cap — optionnel, >= 0 si présent
    market_cap = message.get("market_cap")
    if market_cap is not None:
        if not _is_finite_number(market_cap):
            errors.append(f"market_cap non numérique/fini: {market_cap!r}")
        elif market_cap < 0:
            errors.append(f"market_cap < 0: {market_cap}")

    # timestamp — obligatoire, parseable, pas trop dans le futur
    ts_raw = message.get("timestamp")
    ts = parse_timestamp(ts_raw)
    if ts is None:
        errors.append(f"timestamp manquant ou non parseable: {ts_raw!r}")
    else:
        reference = now or datetime.utcnow()
        if ts > reference + FUTURE_SKEW:
            errors.append(f"timestamp dans le futur: {ts.isoformat()}")

    return errors


def is_valid(message: dict, *, now: datetime = None) -> bool:
    """Raccourci booléen de validate_record."""
    return not validate_record(message, now=now)
