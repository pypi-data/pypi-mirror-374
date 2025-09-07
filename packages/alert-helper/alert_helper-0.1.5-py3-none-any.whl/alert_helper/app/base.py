class BaseApp:
    def __init__(self, verbose: bool):
        self.verbose = verbose

    def __call__(self, text: str):
        try:
            self._alert(text)
            if self.verbose:
                print(f"successfully called {self} alarm")
        except Exception as e:
            if self.verbose:
                print(f"failed to call {self} alarm: {e}")

    def _alert(self, text: str):
        raise NotImplementedError

    def __repr__(self):
        return "Base"
