class BaseApp:
    def __init__(self):
        pass

    def __call__(self, text: str, verbose: bool):
        try:
            self._call_api(text)
            if verbose:
                print(f"successfully called {self} alarm")
        except Exception as e:
            if verbose:
                print(f"failed to call {self} alarm: {e}")

    def _call_api(self, text: str):
        raise NotImplementedError

    def __repr__(self):
        return "Base"
