import reflex as rx

from buridan_ui.wrappers.base.main import base


def text_wrapper(title: str, description: str):
    return rx.el.div(
        rx.el.label(title, class_name="text-md font-bold"),
        rx.el.label(
            description,
            class_name="text-[13px] font-regular",
            color=rx.color("slate", 11),
        ),
        class_name="flex flex-col gap-y-2",
    )


@base("/getting-started/who-is-buridan/", "Who Is Buridan?")
def buridan():
    return [
        rx.box(
            rx.vstack(
                text_wrapper(
                    "Who is Buridan?",
                    "Jean Buridan was a 14th-century French philosopher and logician, widely regarded for his contributions to the study of free will, determinism, and ethics. While his works span various domains of thought, one of his most well-known contributions is the famous `Buridan's Ass` paradox—a thought experiment that delves into the complexities of decision-making in the face of equal options.",
                ),
                text_wrapper(
                    "",
                    "In this paradox, Buridan imagines a donkey caught between two equally enticing bales of hay. Unable to choose between them, the donkey, despite being hungry, ends up starving because of its inability to make a decision. This paradox is often used to highlight the difficulties we face when confronted with equally viable options, and the resulting inaction that can occur when there's no clear reason to choose one over the other.",
                ),
                text_wrapper(
                    "",
                    "While Buridan's Ass symbolizes indecision, it also points to the importance of making choices even when they seem equally valid. The paradox serves as a timeless reminder that decision-making isn't always as straightforward as it seems—especially when there are multiple possibilities that each seem appealing in their own way. Just like the donkey, developers, designers, and creators often face such dilemmas when making choices between different approaches or technologies.",
                ),
                text_wrapper(
                    "Why Buridan?",
                    "I chose the name 'Buridan UI' to evoke the spirit of thoughtful decision-making in design. Just as Buridan's donkey faced a dilemma between two equally appealing bales of hay, developers often grapple with choices in component design and user experience. This site aims to provide a clear path through those choices by offering beautifully crafted, reusable components that simplify the decision-making process.",
                ),
                text_wrapper(
                    "",
                    "The goal is to help you avoid the proverbial 'indecision' by offering pre-made components that are visually appealing, functionally robust, and easy to integrate. The burden of choice should not overwhelm you—it should be an opportunity for creativity and ease of implementation.",
                ),
                text_wrapper(
                    "Explore and Create",
                    "Dive into our collection of components and see how they can elevate your projects. Whether you’re building a new app or enhancing an existing one, Buridan UI is here to help you navigate the vast landscape of design choices with ease.",
                ),
                # max_width="40em",
                width="100%",
                spacing="6",
            ),
            width="100%",
            display="flex",
            justify_content="start",
            class_name="p-4",
        )
    ]
