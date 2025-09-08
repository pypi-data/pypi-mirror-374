
class Enum:
    def __init__(self, **kwargs):
        # mark init mode
        object.__setattr__(self, "_locked", False)

        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

        # lock after init
        object.__setattr__(self, "_locked", True)

    def __setattr__(self, key, value):
        if getattr(self, "_locked", False):
            raise AttributeError(f"Cannot modify attribute '{key}' of Enum once created")
        object.__setattr__(self, key, value)

    def __delattr__(self, key):
        if getattr(self, "_locked", False):
            raise AttributeError(f"Cannot delete attribute '{key}' of Enum once created")
        object.__delattr__(self, key)
