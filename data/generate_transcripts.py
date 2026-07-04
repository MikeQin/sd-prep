"""Generate synthetic sales-call transcripts for the Rilla on-site prep exercise."""
import json
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent / "transcripts"

VERTICALS = ["home_services", "apartment_leasing"]

REPS = [
    {"id": "rep-01", "name": "Jordan Blake", "vertical": "home_services", "tier": "strong"},
    {"id": "rep-02", "name": "Casey Nguyen", "vertical": "home_services", "tier": "average"},
    {"id": "rep-03", "name": "Riley Thompson", "vertical": "home_services", "tier": "weak"},
    {"id": "rep-04", "name": "Morgan Ellis", "vertical": "apartment_leasing", "tier": "strong"},
    {"id": "rep-05", "name": "Avery Kim", "vertical": "apartment_leasing", "tier": "average"},
    {"id": "rep-06", "name": "Drew Patel", "vertical": "apartment_leasing", "tier": "weak"},
]

CUSTOMER_NAMES = [
    "Pat Romero", "Sam Osei", "Jamie Cruz", "Taylor Novak", "Alex Farrow",
    "Chris Bellamy", "Robin Hart", "Skyler Voss", "Quinn Alvarado", "Reese Dunlap",
]

OPENERS = {
    "home_services": [
        "Hi {customer}, thanks for having me out today to look at your {system}.",
        "Good afternoon, I'm with the team that called about your {system} estimate.",
    ],
    "apartment_leasing": [
        "Hi {customer}, welcome in! Thanks for scheduling a tour with us today.",
        "Hey {customer}, great to meet you, ready to see the community?",
    ],
}

DISCOVERY_REP = [
    "So tell me, what's prompting you to look into this now?",
    "What's most important to you as you're making this decision?",
    "Have you looked at other options before reaching out to us?",
]

DISCOVERY_CUSTOMER = [
    "Honestly our old unit finally gave out last week.",
    "We're just comparing a few places before we decide.",
    "We want something reliable that won't cost us more down the road.",
]

PRICING_REP = [
    "Based on what we've walked through, the total price for this would be {price}.",
    "For the package we discussed, the total cost is {price}.",
]

OBJECTION_CUSTOMER = [
    "That's a bit more than I expected, it feels too expensive.",
    "I'll need to talk to my spouse before we commit to anything.",
    "We were planning to shop around a little more first.",
]

OBJECTION_HANDLING = {
    "strong": [
        "Totally fair, a lot of folks feel that way at first. Let's break down what's included so you can see the value, and I can walk you through financing.",
    ],
    "average": [
        "I understand, it is an investment. We do have financing options if that helps.",
    ],
    "weak": [
        "Okay, well, the price is the price, but let me know if you change your mind.",
    ],
}

NEXT_STEP_REP = {
    "strong": [
        "Let's go ahead and schedule this for next week, and I'll follow up tomorrow to confirm everything.",
    ],
    "average": [
        "Why don't I send over the paperwork and we can follow up in a few days?",
    ],
    "weak": [
        "Alright, well, feel free to reach out whenever you're ready.",
    ],
}

NEXT_STEP_CUSTOMER = {
    "strong": ["Sounds good, let's do it.", "Yes, let's move forward with that."],
    "average": ["Okay sure, send it over.", "Alright, we can look at it."],
    "weak": ["Yeah, maybe.", "We'll see."],
}

CLOSING_CUSTOMER_NO_COMMIT = [
    "We'll think about it and let you know.",
    "Not sure yet, we'll be in touch.",
]


def _duration_for(text: str) -> float:
    return max(1.5, len(text.split()) * 0.4)


def _build_turns(rep: dict, customer_name: str, vertical: str) -> tuple[list[dict], float]:
    turns: list[dict] = []
    t = 0.0

    def add(speaker: str, text: str) -> None:
        nonlocal t
        dur = _duration_for(text)
        turns.append({"speaker": speaker, "start": round(t, 1), "end": round(t + dur, 1), "text": text})
        t += dur

    system = random.choice(["HVAC system", "water heater", "electrical panel"]) if vertical == "home_services" else ""
    opener = random.choice(OPENERS[vertical]).format(customer=customer_name, system=system)
    add("rep", opener)
    add("customer", "Thanks for coming, come on in." if vertical == "home_services" else "Thanks, excited to see it!")

    add("rep", random.choice(DISCOVERY_REP))
    add("customer", random.choice(DISCOVERY_CUSTOMER))

    price = random.choice(["$4,200", "$6,800", "$1,150/month", "$980/month"])
    add("rep", random.choice(PRICING_REP).format(price=price))

    tier = rep["tier"]
    raises_objection = tier != "strong" or random.random() < 0.5
    if raises_objection:
        add("customer", random.choice(OBJECTION_CUSTOMER))
        add("rep", random.choice(OBJECTION_HANDLING[tier]))

    add("rep", random.choice(NEXT_STEP_REP[tier]))
    if tier == "weak" and random.random() < 0.6:
        add("customer", random.choice(CLOSING_CUSTOMER_NO_COMMIT))
    else:
        add("customer", random.choice(NEXT_STEP_CUSTOMER[tier]))

    return turns, round(t, 1)


def generate_all() -> list[dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    calls = []
    call_index = 1
    start_date = date(2026, 5, 1)
    for rep in REPS:
        num_calls = random.randint(4, 5)
        for _ in range(num_calls):
            customer_name = random.choice(CUSTOMER_NAMES)
            turns, duration = _build_turns(rep, customer_name, rep["vertical"])
            call = {
                "call_id": f"{rep['vertical'][:2]}-{call_index:04d}",
                "vertical": rep["vertical"],
                "rep_id": rep["id"],
                "rep_name": rep["name"],
                "customer_name": customer_name,
                "date": str(start_date + timedelta(days=call_index)),
                "duration_seconds": duration,
                "turns": turns,
            }
            calls.append(call)
            call_index += 1
    for call in calls:
        path = OUTPUT_DIR / f"{call['call_id']}.json"
        path.write_text(json.dumps(call, indent=2))
    return calls


if __name__ == "__main__":
    generated = generate_all()
    print(f"Generated {len(generated)} transcripts in {OUTPUT_DIR}")
