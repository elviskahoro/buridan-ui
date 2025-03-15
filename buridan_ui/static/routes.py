# ... base prefixes for different sections
_GS_Base = "/getting-started/"
_P = "/pantry/"
_C = "/charts/"

# ... main site routes

# ... getting started paths
GettingStartedRoutes = [
    {"name": "Introduction", "path": f"{_GS_Base}introduction", "dir": "introduction"},
    {"name": "Installation", "path": f"{_GS_Base}installation", "dir": "installation"},
    {"name": "Who is Buridan?", "path": f"{_GS_Base}who-is-buridan", "dir": "buridan"},
    {"name": "Changelog", "path": f"{_GS_Base}changelog", "dir": "changelog"},
]

# ... pantry component paths
PantryRoutes = sorted(
    [
        {"name": "Logins", "path": f"{_P}logins", "dir": "logins"},
        {"name": "Standard Forms", "path": f"{_P}standard-forms", "dir": "forms"},
        {"name": "Standard Tables", "path": f"{_P}standard-tables", "dir": "tables"},
        {"name": "Pricing Sections", "path": f"{_P}pricing-sections", "dir": "pricing"},
        {"name": "Popups", "path": f"{_P}popups", "dir": "popups"},
        {
            "name": "Payments & Billing",
            "path": f"{_P}payments-and-billing",
            "dir": "payments",
        },
        {
            "name": "Onboarding & Progress",
            "path": f"{_P}onboarding-and-progress",
            "dir": "onboardings",
        },
        {"name": "Menus", "path": f"{_P}menus", "dir": "menus"},
        {"name": "Backgrounds", "path": f"{_P}backgrounds", "dir": "backgrounds"},
        {"name": "Featured", "path": f"{_P}featured", "dir": "featured"},
        {"name": "Descriptive Lists", "path": f"{_P}descriptive-lists", "dir": "lists"},
        {"name": "Timeline", "path": f"{_P}timeline", "dir": "timeline"},
        {"name": "Animations", "path": f"{_P}animations", "dir": "animations"},
        {"name": "Prompt Boxes", "path": f"{_P}prompt-boxes", "dir": "prompts"},
        {"name": "Cards", "path": f"{_P}cards", "dir": "cards"},
        {"name": "Subscribe", "path": f"{_P}subscribe", "dir": "subscribe"},
        {
            "name": "Frequently Asked Questions",
            "path": f"{_P}frequently-asked-questions",
            "dir": "faq",
        },
        {"name": "Footers", "path": f"{_P}footers", "dir": "footers"},
        {"name": "Inputs", "path": f"{_P}inputs", "dir": "inputs"},
    ],
    key=lambda x: x["name"],
)

# ... chart component paths
ChartRoutes = sorted(
    [
        {"name": "Bar Charts", "path": f"{_C}bar-charts", "dir": "bar"},
        {"name": "Area Charts", "path": f"{_C}area-charts", "dir": "area"},
        {"name": "Line Charts", "path": f"{_C}line-charts", "dir": "line"},
        {"name": "Pie Charts", "path": f"{_C}pie-charts", "dir": "pie"},
        {"name": "Radar Charts", "path": f"{_C}radar-charts", "dir": "radar"},
        {"name": "Scatter Charts", "path": f"{_C}scatter-charts", "dir": "scatter"},
        {"name": "Doughnut Charts", "path": f"{_C}doughnut-charts", "dir": "doughnut"},
    ],
    key=lambda x: x["name"],
)


# ... navigation menu paths
NavigationRoutes = [
    {"name": "Home", "path": "/"},
    {"name": "Getting Started", "path": GettingStartedRoutes[0]["path"]},
    {"name": "Pantry", "path": PantryRoutes[0]["path"]},
    {"name": "Charts", "path": ChartRoutes[0]["path"]},
]
