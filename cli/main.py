from textual.app import App


class PrismCLI(App):
    def on_mount(self) -> None:
        self.screen.styles.background = "black"


if __name__ == "__main__":
    app: PrismCLI = PrismCLI()
    app.run()
