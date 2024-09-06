import reflex as rx
from .nav import navbar

def base_page(child: rx.Component, *args, **kwargs) -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.box(
            child,
            padding="1em",
            width="100%",    
        ),
        padding="10em",
        
    )