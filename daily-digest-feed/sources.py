"""Source configuration for daily-digest-feed.

Edit this file to add/remove YouTube channels, newsletters, or other sources.
All other modules import from here — there should be no source lists anywhere else.
"""

YOUTUBE_SOURCES: dict[str, list[dict]] = {
    "overlanding": [
        {"name": "Casey 250",                "handle": "@Casey250",                 "channel_id": "UCaE68iLdChFimyvhXy2XPWA"},
        {"name": "This Story Till Now",      "handle": "@ThisStoryTillNow",         "channel_id": "UC_QteyvNZKtK5qPWlPbrl-Q"},
        {"name": "Life Style Overland",      "handle": "@LifeStyleOverland",        "channel_id": "UCJSHfhZHP8-iChAVCrXWTyA"},
        {"name": "VentureToRoam",            "handle": "@VentureToRoam",            "channel_id": "UCfAtRPIM8OOVhyVXWHnvaIQ"},
        {"name": "LetsGetLost",              "handle": "@LetsGetLost",              "channel_id": "UCwiFE-kz0FZR8JJv3DTlocQ"},
        {"name": "Ozark Overland Adventure", "handle": "@OzarkOverlandAdventures",  "channel_id": "UCgbmZmCWIzOwKzAN-0UaWHg"},
        {"name": "TrailRecon",               "handle": "@TrailRecon",               "channel_id": "UCEEgz9PD6iTRSB0VXNbWvRw"},
        {"name": "Epic Adventure Outfitters","handle": "@EpicAdventureOutfitters",  "channel_id": "UCjtrDgtexm4QwKkxI8frtFA"},
        {"name": "Lil and Jake",             "handle": "@lilandjake",               "channel_id": "UCI5nuVPmxCt4VwSprm-gpAg"},
        {"name": "Craving.Outdoors",         "handle": "@Craving.Outdoors",         "channel_id": "UCzHx4YhJTwZ_HG_D-Q1lpSA"},
    ],
    "power_platform": [
        {"name": "Matthew Devaney", "handle": "@MatthewDevaney", "channel_id": "UCuBK42yA0I1sfmsZTCL_t2w"},
        {"name": "Shane Young",     "handle": "@ShanesCows",     "channel_id": "UC7_OGRP8BYvtGB8eZdPG6Ng"},
        {"name": "Lisa Crosbie",    "handle": "@LisaCrosbie",    "channel_id": "UCvxCGKv4WSq49LfNIfZEEtg"},
        {"name": "Reza Dorrani",    "handle": "@RezaDorrani",    "channel_id": "UCvBYTqRx-n_8KzFO0MJlUVw"},
        {"name": "April Dunnam",    "handle": "@AprilDunnam",    "channel_id": "UCz_x76EBX5UXsV27drGNh6w"},
        {"name": "DamoBird365",     "handle": "@DamoBird365",    "channel_id": "UC-NCKrEw6CM8fidaIk-yrUQ"},
        {"name": "Sean Astrakhan",  "handle": "@Untethered365",  "channel_id": "UCEYgG-Fw0ghmP1Vnw_M3oGQ"},
        {"name": "Bright Ideas Agency", "handle": "@brightideasagency", "channel_id": "UCnv9vvr7tQVQ07iSe4rZgWQ"},
        {"name": "Daniel Anderson", "handle": "@DanielAndersonAU", "channel_id": "UCsYYpxfrYrZaKwFPGM7shtQ"},
        {"name": "Power Squared",   "handle": "@PowerSquared",   "channel_id": "UCoDxmKfgtkGeXezviLXUGIw"},
        {"name": "Steve Corey",     "handle": "@stevecorey365",  "channel_id": "UCOZthH-jESHnUuH2HDyYONg"},
        {"name": "Andrew Hess",     "handle": "@andrewhess123",  "channel_id": "UCH7RJ4zXEjFpfsm-6VZI8vw"},
    ],
    "fabric_powerbi": [
        {"name": "Guy in a Cube",    "handle": "@GuyInACube",    "channel_id": "UCFp1vaKzpfvoGai0vE5VJ0w"},
        {"name": "RADACAD",          "handle": "@RADACAD",       "channel_id": "UCsOfIwAXj1fT6LDqEDEAb4g"},
        {"name": "How to Power BI",  "handle": "@HowtoPowerBI",  "channel_id": "UCcfngi7_ASuo5jdWX0bNauQ"},
        {"name": "Fernan (Solutions Abroad)", "handle": "@SolutionsAbroad", "channel_id": "UCpbgBx--a_H9LL69A1Uz9yg"},
        {"name": "Power BI Tips",    "handle": "@PowerBITips",   "channel_id": "UCPwPrIpZwlfIKcoUpRwl9OQ"},
    ],
    "ai": [
        {"name": "NateBJones",    "handle": "@NateBJones",    "channel_id": "UC0C-17n9iuUQPylguM1d-lQ"},
        {"name": "Alex Finn",     "handle": "@AlexFinn",      "channel_id": "UCfQNB91qRP_5ILeu_S_bSkg"},
        {"name": "Chase AI",      "handle": "@ChaseAI",       "channel_id": "UCoy6cTJ7Tg0dqS-DI-_REsA"},
        {"name": "Nate Herk",     "handle": "@NateHerk",      "channel_id": "UC2ojq-nuP8ceeHqiroeKhBA"},
        {"name": "Paul J Lipsky", "handle": "@PaulJLipsky",   "channel_id": "UCmeU2DYiVy80wMBGZzEWnbw"},
        {"name": "Simon Scrapes",   "handle": "@SimonScrapes",    "channel_id": "UCdCR4-uYOg5ju-IUuDnfnQA"},
        {"name": "AI Daily Brief", "handle": "@AIDailyBrief",   "channel_id": "UCKelCK4ZaO6HeEI1KQjqzWA"},
        {"name": "John Savill's Technical Training", "handle": "@NTFAQGuy", "channel_id": "UCpIn7ox7j7bH_OFj7tYouOQ"},
        {"name": "Dewain Robinson", "handle": "@DewainRobinson", "channel_id": "UCSxb0EDb5vw4pRcgW0hQ8Ug"},
    ],
}

NEWSLETTER_SOURCES: list[dict] = [
    {
        "key": "power_platform_weekly",
        "name": "Power Platform Weekly",
        "url": "https://www.ppweekly.com/",
        "feed_url": "https://www.ppweekly.com/feed",
        "type": "substack",
    },
    {
        "key": "power_platform_dev_weekly",
        "name": "Power Platform Dev Weekly",
        "url": "https://www.ppdevweekly.com/",
        "feed_url": "https://www.ppdevweekly.com/feed",
        "type": "substack",
    },
    {
        "key": "power_bi_weekly",
        "name": "Power BI Weekly",
        "url": "https://powerbiweekly.info/",
        "feed_url": None,  # No RSS — scrape latest issue-N.html
        "type": "custom",
    },
]


# ---------------------------------------------------------------------------
# Release Plans (releaseplans.net)
# ---------------------------------------------------------------------------
RELEASE_PLANS_SOURCE: dict = {
    "url": "https://releaseplans.net/data/release-plans.json",
    "products": [
        "Power Apps",
        "Power Automate",
        "AI Builder",
        "Power Pages",
        "Microsoft Dataverse",
        "Microsoft Power Platform governance and administration",
        "Microsoft Copilot Studio",
    ],
}


# ---------------------------------------------------------------------------
# Microsoft 365 Roadmap (public JSON API behind microsoft.com/microsoft-365/roadmap)
# ---------------------------------------------------------------------------
# NO product filter — include everything. Power Platform items may overlap with
# RELEASE_PLANS_SOURCE; duplicates are intentional (better duplicates than gaps,
# since Microsoft moves roadmap items between surfaces).
M365_ROADMAP_SOURCE: dict = {
    "url": "https://www.microsoft.com/releasecommunications/api/v1/m365",
}


def all_youtube_sources() -> list[tuple[str, dict]]:
    """Flatten YouTube sources to (category, source_dict) tuples for parallel fetching."""
    return [(cat, src) for cat, srcs in YOUTUBE_SOURCES.items() for src in srcs]


def total_source_count() -> int:
    """Total discrete source count (YouTube channels + newsletters + release plans + roadmap)."""
    return (
        sum(len(v) for v in YOUTUBE_SOURCES.values())
        + len(NEWSLETTER_SOURCES)
        + 1  # release_plans is one source
        + 1  # m365_roadmap is one source
    )
