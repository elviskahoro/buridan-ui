import reflex as rx
from buridan_ui.private._sunburst import sunburst_chart


def sunburst_v1():
    data = {
        "name": "nivo",
        "color": "hsl(137, 70%, 50%)",
        "children": [
            {
                "name": "viz",
                "color": "hsl(355, 70%, 50%)",
                "children": [
                    {
                        "name": "stack",
                        "color": "hsl(178, 70%, 50%)",
                        "children": [
                            {
                                "name": "cchart",
                                "color": "hsl(334, 70%, 50%)",
                                "loc": 160137,
                            },
                            {
                                "name": "xAxis",
                                "color": "hsl(181, 70%, 50%)",
                                "loc": 100495,
                            },
                            {
                                "name": "yAxis",
                                "color": "hsl(300, 70%, 50%)",
                                "loc": 47687,
                            },
                            {
                                "name": "layers",
                                "color": "hsl(72, 70%, 50%)",
                                "loc": 133820,
                            },
                        ],
                    },
                    {
                        "name": "ppie",
                        "color": "hsl(126, 70%, 50%)",
                        "children": [
                            {
                                "name": "chart",
                                "color": "hsl(55, 70%, 50%)",
                                "children": [
                                    {
                                        "name": "pie",
                                        "color": "hsl(146, 70%, 50%)",
                                        "children": [
                                            {
                                                "name": "outline",
                                                "color": "hsl(137, 70%, 50%)",
                                                "loc": 117768,
                                            },
                                            {
                                                "name": "slices",
                                                "color": "hsl(136, 70%, 50%)",
                                                "loc": 145897,
                                            },
                                            {
                                                "name": "bbox",
                                                "color": "hsl(335, 70%, 50%)",
                                                "loc": 176069,
                                            },
                                        ],
                                    },
                                    {
                                        "name": "donut",
                                        "color": "hsl(150, 70%, 50%)",
                                        "loc": 144252,
                                    },
                                    {
                                        "name": "gauge",
                                        "color": "hsl(221, 70%, 50%)",
                                        "loc": 59646,
                                    },
                                ],
                            },
                            {
                                "name": "legends",
                                "color": "hsl(252, 70%, 50%)",
                                "loc": 39325,
                            },
                        ],
                    },
                ],
            },
            {
                "name": "colors",
                "color": "hsl(261, 70%, 50%)",
                "children": [
                    {"name": "rgb", "color": "hsl(280, 70%, 50%)", "loc": 111041},
                    {"name": "hsl", "color": "hsl(183, 70%, 50%)", "loc": 73788},
                ],
            },
            {
                "name": "utils",
                "color": "hsl(267, 70%, 50%)",
                "children": [
                    {"name": "randomize", "color": "hsl(338, 70%, 50%)", "loc": 177910},
                    {
                        "name": "resetClock",
                        "color": "hsl(310, 70%, 50%)",
                        "loc": 145103,
                    },
                    {"name": "noop", "color": "hsl(80, 70%, 50%)", "loc": 54077},
                    {"name": "tick", "color": "hsl(89, 70%, 50%)", "loc": 38852},
                    {"name": "forceGC", "color": "hsl(56, 70%, 50%)", "loc": 88715},
                    {
                        "name": "stackTrace",
                        "color": "hsl(343, 70%, 50%)",
                        "loc": 198908,
                    },
                    {"name": "dbg", "color": "hsl(133, 70%, 50%)", "loc": 40039},
                ],
            },
            {
                "name": "generators",
                "color": "hsl(33, 70%, 50%)",
                "children": [
                    {"name": "address", "color": "hsl(17, 70%, 50%)", "loc": 153915},
                    {"name": "city", "color": "hsl(302, 70%, 50%)", "loc": 7888},
                    {"name": "animal", "color": "hsl(222, 70%, 50%)", "loc": 35397},
                    {"name": "movie", "color": "hsl(266, 70%, 50%)", "loc": 151913},
                    {"name": "user", "color": "hsl(229, 70%, 50%)", "loc": 141468},
                ],
            },
            {
                "name": "set",
                "color": "hsl(278, 70%, 50%)",
                "children": [
                    {"name": "clone", "color": "hsl(144, 70%, 50%)", "loc": 119882},
                    {"name": "intersect", "color": "hsl(135, 70%, 50%)", "loc": 161260},
                    {"name": "merge", "color": "hsl(300, 70%, 50%)", "loc": 135843},
                    {"name": "reverse", "color": "hsl(309, 70%, 50%)", "loc": 32119},
                    {"name": "toArray", "color": "hsl(118, 70%, 50%)", "loc": 196788},
                    {"name": "toObject", "color": "hsl(61, 70%, 50%)", "loc": 139088},
                    {"name": "fromCSV", "color": "hsl(193, 70%, 50%)", "loc": 197434},
                    {"name": "slice", "color": "hsl(288, 70%, 50%)", "loc": 121060},
                    {"name": "append", "color": "hsl(168, 70%, 50%)", "loc": 134520},
                    {"name": "prepend", "color": "hsl(232, 70%, 50%)", "loc": 143903},
                    {"name": "shuffle", "color": "hsl(79, 70%, 50%)", "loc": 89739},
                    {"name": "pick", "color": "hsl(307, 70%, 50%)", "loc": 7234},
                    {"name": "plouc", "color": "hsl(344, 70%, 50%)", "loc": 106944},
                ],
            },
            {
                "name": "text",
                "color": "hsl(69, 70%, 50%)",
                "children": [
                    {"name": "trim", "color": "hsl(69, 70%, 50%)", "loc": 9215},
                    {"name": "slugify", "color": "hsl(208, 70%, 50%)", "loc": 75094},
                    {"name": "snakeCase", "color": "hsl(253, 70%, 50%)", "loc": 154655},
                    {"name": "camelCase", "color": "hsl(191, 70%, 50%)", "loc": 190393},
                    {"name": "repeat", "color": "hsl(154, 70%, 50%)", "loc": 92902},
                    {"name": "padLeft", "color": "hsl(189, 70%, 50%)", "loc": 33739},
                    {"name": "padRight", "color": "hsl(314, 70%, 50%)", "loc": 184238},
                    {"name": "sanitize", "color": "hsl(227, 70%, 50%)", "loc": 73535},
                    {"name": "ploucify", "color": "hsl(42, 70%, 50%)", "loc": 47421},
                ],
            },
            {
                "name": "misc",
                "color": "hsl(139, 70%, 50%)",
                "children": [
                    {
                        "name": "greetings",
                        "color": "hsl(276, 70%, 50%)",
                        "children": [
                            {
                                "name": "hey",
                                "color": "hsl(282, 70%, 50%)",
                                "loc": 79358,
                            },
                            {
                                "name": "HOWDY",
                                "color": "hsl(216, 70%, 50%)",
                                "loc": 13068,
                            },
                            {
                                "name": "aloha",
                                "color": "hsl(0, 70%, 50%)",
                                "loc": 67560,
                            },
                            {
                                "name": "AHOY",
                                "color": "hsl(234, 70%, 50%)",
                                "loc": 5427,
                            },
                        ],
                    },
                    {"name": "other", "color": "hsl(156, 70%, 50%)", "loc": 195477},
                    {
                        "name": "path",
                        "color": "hsl(216, 70%, 50%)",
                        "children": [
                            {
                                "name": "pathA",
                                "color": "hsl(14, 70%, 50%)",
                                "loc": 109524,
                            },
                            {
                                "name": "pathB",
                                "color": "hsl(62, 70%, 50%)",
                                "children": [
                                    {
                                        "name": "pathB1",
                                        "color": "hsl(269, 70%, 50%)",
                                        "loc": 149425,
                                    },
                                    {
                                        "name": "pathB2",
                                        "color": "hsl(28, 70%, 50%)",
                                        "loc": 44445,
                                    },
                                    {
                                        "name": "pathB3",
                                        "color": "hsl(237, 70%, 50%)",
                                        "loc": 31332,
                                    },
                                    {
                                        "name": "pathB4",
                                        "color": "hsl(187, 70%, 50%)",
                                        "loc": 47117,
                                    },
                                ],
                            },
                            {
                                "name": "pathC",
                                "color": "hsl(309, 70%, 50%)",
                                "children": [
                                    {
                                        "name": "pathC1",
                                        "color": "hsl(63, 70%, 50%)",
                                        "loc": 169936,
                                    },
                                    {
                                        "name": "pathC2",
                                        "color": "hsl(179, 70%, 50%)",
                                        "loc": 89012,
                                    },
                                    {
                                        "name": "pathC3",
                                        "color": "hsl(20, 70%, 50%)",
                                        "loc": 66546,
                                    },
                                    {
                                        "name": "pathC4",
                                        "color": "hsl(124, 70%, 50%)",
                                        "loc": 88129,
                                    },
                                    {
                                        "name": "pathC5",
                                        "color": "hsl(125, 70%, 50%)",
                                        "loc": 142227,
                                    },
                                    {
                                        "name": "pathC6",
                                        "color": "hsl(256, 70%, 50%)",
                                        "loc": 130230,
                                    },
                                    {
                                        "name": "pathC7",
                                        "color": "hsl(153, 70%, 50%)",
                                        "loc": 12805,
                                    },
                                    {
                                        "name": "pathC8",
                                        "color": "hsl(158, 70%, 50%)",
                                        "loc": 143278,
                                    },
                                    {
                                        "name": "pathC9",
                                        "color": "hsl(239, 70%, 50%)",
                                        "loc": 57926,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
        ],
    }

    return rx.box(
        rx.el.div(
            sunburst_chart(
                data=data,
                id="name",
                value="loc",
                enable_arc_labels=True,
                border_width=1,
                corner_radius=45,
            ),
            height="400px",
            width="400px",
        ),
        class_name="size-full flex items-center justify-center align-center overflow-hidden",
    )
