import re
from datetime import datetime, timezone
from decimal import Decimal
from .models import Product, SearchRequest

BLOCKED = {"discontinued","end of sale","end of life","obsolete","retired","inactive","unavailable for ordering","superseded and no longer orderable"}


def _norm(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9.]+", value.lower()))


def _spec_match(wanted: str, offered: str | None) -> bool | None:
    if not offered:
        return None
    wanted_tokens, offered_tokens = _norm(wanted), _norm(offered)
    return bool(wanted_tokens) and (wanted_tokens <= offered_tokens or len(wanted_tokens & offered_tokens) / len(wanted_tokens) >= .6)


def score_product(product: Product, request: SearchRequest) -> Product:
    p = product.model_copy(deep=True)
    p.requested_quantity = request.quantity
    p.quantity_shortfall = None if p.available_quantity is None else max(0, request.quantity - p.available_quantity)
    p.extended_price = p.unit_price * request.quantity if p.unit_price is not None else None
    p.availability_status = "Not provided by distributor" if p.available_quantity is None else ("In stock" if p.available_quantity >= request.quantity else f"Insufficient quantity — shortfall {p.quantity_shortfall}")
    offered = {k.lower(): v for k, v in p.technical_specifications.items()}
    outcomes, mandatory_failure, missing_essential = [], False, False
    for requirement in request.requirements:
        value = offered.get(requirement.name.lower())
        match = _spec_match(requirement.value, value)
        if match is True:
            p.matched_requirements.append(f"{requirement.name}: {requirement.value}")
        else:
            status = "not provided" if match is None else f"offered {value}"
            p.exceptions.append(f"{requirement.name}: requested {requirement.value}; {status}")
            mandatory_failure |= requirement.mandatory
            missing_essential |= requirement.mandatory and match is None
        outcomes.append(1 if match else 0)
    technical = round(50 * sum(outcomes) / len(outcomes)) if outcomes else 25
    category = 15 if request.category.lower() == p.category.lower() else 0
    regional = 15 if p.eligible_countries and request.country in p.eligible_countries else 0
    quantity = 10 if p.available_quantity is not None and p.available_quantity >= request.quantity else (5 if p.available_quantity else 0)
    price = 0 if p.unit_price is None else (5 if request.maximum_unit_price is None or p.unit_price <= request.maximum_unit_price else 0)
    warranty = 5 if (not request.warranty_required or p.warranty) else 0
    p.score_breakdown = {"mandatory_technical_specifications":technical,"product_type_and_intended_use":category,"regional_availability":regional,"available_quantity":quantity,"price_or_budget_compliance":price,"warranty_and_support":warranty}
    p.confidence_score = sum(p.score_breakdown.values())
    if missing_essential:
        p.confidence_score = min(p.confidence_score, 79)
        p.confidence_level = "Requires verification"
    elif mandatory_failure:
        p.confidence_score = min(p.confidence_score, 79)
        p.confidence_level = "Possible match — exception"
    elif p.confidence_score >= 90: p.confidence_level = "Excellent match"
    elif p.confidence_score >= 80: p.confidence_level = "Strong match"
    elif p.confidence_score >= 70: p.confidence_level = "Possible match"
    else: p.confidence_level = "Do not recommend"
    return p


def match_products(products: list[Product], request: SearchRequest):
    primary, regional, lifecycle = [], [], []
    for raw in products:
        if raw.lifecycle_status is None:
            lifecycle.append(score_product(raw, request)); continue
        if raw.lifecycle_status.lower() in BLOCKED or not raw.orderable:
            continue
        item = score_product(raw, request)
        if not item.eligible_countries or request.country not in item.eligible_countries:
            if item.confidence_score >= 55: regional.append(item)
            continue
        mandatory_failed = any("requested" in error for error in item.exceptions)
        if item.confidence_score >= 70 and (not mandatory_failed or request.allow_exceptions):
            primary.append(item)
    primary.sort(key=lambda x: x.confidence_score, reverse=True)
    for rank, item in enumerate(primary[:5], 1): item.rank = rank
    return primary[:5], regional[:5], lifecycle[:5]
