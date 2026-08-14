import os


current_theme = "dark"



def load_theme(
    app,
    theme="dark"
):

    global current_theme

    current_theme = theme


    path = os.path.join(
        "ui",
        "styles",
        f"{theme}.qss"
    )


    if os.path.exists(path):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            app.setStyleSheet(
                file.read()
            )



def toggle_theme(
    app,
    button=None
):

    global current_theme


    if current_theme == "dark":

        load_theme(
            app,
            "light"
        )

        if button:

            button.setText(
                "☀️"
            )


    else:

        load_theme(
            app,
            "dark"
        )

        if button:

            button.setText(
                "🌙"
            )