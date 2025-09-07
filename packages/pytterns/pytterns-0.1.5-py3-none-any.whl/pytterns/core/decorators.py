STRATEGIES = {}
CHAINS = {}
OBSERVERS = {}
FACTORIES = {}
COMMANDS = {}

def strategy(grouper):
    """Decorator to register a class instance under a strategy group.

    The decorated class is instantiated and appended to `STRATEGIES[grouper]`.
    Loaders can then lookup the registered strategy instances by group name.

    Example:
        @strategy('payment')
        class Credit:
            def check(...):
                ...
    """
    def decorator(cls):
        if grouper not in STRATEGIES:
            STRATEGIES[grouper] = []
        STRATEGIES[grouper].append(cls())
        return cls
    return decorator

def chain(grouper, order):
    """Decorator to register a handler class in an ordered chain.

    The decorator instantiates the provided class and stores a tuple
    `(order, instance)` under `CHAINS[grouper]`. The list is kept sorted by
    `order` so chain execution can iterate handlers in the defined order.

    Example:
        @chain('auth', order=1)
        class Authenticator:
            def handle(self, req):
                ...
    """
    def decorator(cls):
        if grouper not in CHAINS:
            CHAINS[grouper] = []
        CHAINS[grouper].append((order, cls()))
        CHAINS[grouper].sort(key=lambda x: x[0])
        return cls
    return decorator


def observer(event):
    """Decorator to register functions or classes as observers for an event name.

    Usage:
        @observer('my_event')
        def listener(payload):
            ...

        @observer('my_event')
        class Listener:
            def update(self, payload):
                ...
    """
    def decorator(callable_or_cls):
        if event not in OBSERVERS:
            OBSERVERS[event] = []
        # If it's a class, instantiate it; otherwise register the callable directly
        if isinstance(callable_or_cls, type):
            OBSERVERS[event].append(callable_or_cls())
        else:
            OBSERVERS[event].append(callable_or_cls)
        return callable_or_cls
    return decorator


def factory(name):
    """Decorator to register a class under a factory name.

    The decorated class is stored (not instantiated). Use `FactoryLoader(name).create(...)`
    to create instances.
    """
    def decorator(cls):
        if name not in FACTORIES:
            FACTORIES[name] = []
        FACTORIES[name].append(cls)
        return cls
    return decorator


def command(name):
    """Decorator to register a command handler under a name.

    A handler can be a function (callable) or a class (which will be instantiated).
    Use `CommandLoader(name).execute(...)` to run the handler.
    """
    def decorator(callable_or_cls):
        if name not in COMMANDS:
            COMMANDS[name] = []
        if isinstance(callable_or_cls, type):
            COMMANDS[name].append(callable_or_cls())
        else:
            COMMANDS[name].append(callable_or_cls)
        return callable_or_cls
    return decorator