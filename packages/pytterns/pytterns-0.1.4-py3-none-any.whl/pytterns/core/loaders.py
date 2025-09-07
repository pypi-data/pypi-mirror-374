import inspect
from pytterns.core.decorators import STRATEGIES, CHAINS, OBSERVERS, FACTORIES, COMMANDS
from pytterns.core.decorators import OBSERVERS

class StrategyLoader:
    """Lookup and apply registered strategies by group name.

    The loader exposes any method name as a filter via `__getattr__`. When a
    filter is called, each registered strategy instance will be checked: if the
    strategy exposes only one public method the loader calls it and returns its
    result directly; otherwise the loader will call the filter method and
    return the first strategy instance for which the filter returns truthy.
    """
    def __init__(self, name):
        self.name = name
        if name not in STRATEGIES:
            raise ValueError(f"No strategy found for strategy: {name}")

    def __getattr__(self, filter_method):
        """Allows you to call any method as a filter.

        Example:
            load.strategy('payment').check('credit_card')
        """
        def filter_strategy(*args, **kwargs):
            for strategy in STRATEGIES[self.name]:
                methods = [name for name, func in inspect.getmembers(strategy, predicate=inspect.ismethod)
                    if not name.startswith("__")]
                method = getattr(strategy, filter_method, None)
                if callable(method):
                    if len(methods) == 1:
                        return method(*args, **kwargs)
                    if method(*args, **kwargs):
                        return strategy
            raise ValueError(f"No strategy in '{self.name}' passed the '{filter_method}' filter")
        return filter_strategy

class ChainLoader:
    def __init__(self, name):
        """Load an ordered chain of handlers by name.

        Raises ValueError if the chain does not exist. The handlers are stored
        in the order defined by the decorators (the list is already sorted by
        `order` in the decorator).
        """
        self.name = name
        if name not in CHAINS:
            raise ValueError(f"No chain found for: {name}")
        # Gets the already ordered handlers
        self.handlers = [handler for _, handler in CHAINS[name]]

    def handle(self, *args, **kwargs):
        """Execute `handle` on every handler in the chain.

        Raises TypeError when a handler does not implement `handle`.
        """
        for handler in self.handlers:
            method = getattr(handler, "handle", None)
            if callable(method):
                method(*args, **kwargs)
            else:
                raise TypeError(f"Class '{handler.__class__.__name__}' does not have the 'handle' method.")


class ObserverLoader:
    def __init__(self, event):
        self.event = event
        if event not in OBSERVERS:
            raise ValueError(f"No observers registered for event: {event}")
        # store the callables/instances
        self.listeners = OBSERVERS[event]

    def notify(self, *args, **kwargs):
        """Call all listeners for the event. Collect results and exceptions.

        Returns a list of (success, result_or_exception) tuples where success is True
        when listener returned normally, False when it raised.
        """
        results = []
        for listener in self.listeners:
            try:
                # listener may be a callable or an object with update/notify
                if callable(listener):
                    res = listener(*args, **kwargs)
                else:
                    method = getattr(listener, "update", None) or getattr(listener, "notify", None)
                    if callable(method):
                        res = method(*args, **kwargs)
                    else:
                        raise TypeError(f"Observer '{listener.__class__.__name__}' has no 'update' or 'notify' method")
                results.append((True, res))
            except Exception as exc:
                results.append((False, exc))
        return results

    def unsubscribe(self, listener):
        """Remove a listener from the event's registry.

        Accepts the exact callable/instance to remove or a class to remove any
        instance of that class.
        """
        lst = OBSERVERS.get(self.event, [])
        if isinstance(listener, type):
            # remove instances of this class
            new = [l for l in lst if not (not callable(l) and isinstance(l, listener))]
        else:
            new = [l for l in lst if l is not listener]
        if new:
            OBSERVERS[self.event] = new
        else:
            # no listeners left: remove the event key
            OBSERVERS.pop(self.event, None)


class FactoryLoader:
    def __init__(self, name):
        self.name = name
        if name not in FACTORIES:
            raise ValueError(f"No factory found for: {name}")
        self.classes = FACTORIES[name]

    def create(self, *args, **kwargs):
        """Create and return a registered class instance.

        By default creates the first registered class. You can specify `index` to
        choose another registered class.
        """
        index = kwargs.pop('index', 0)
        if not (0 <= index < len(self.classes)):
            raise IndexError('factory index out of range')
        cls = self.classes[index]
        return cls(*args, **kwargs)


class CommandLoader:
    def __init__(self, name):
        self.name = name
        if name not in COMMANDS:
            raise ValueError(f"No command found for: {name}")
        self.handlers = COMMANDS[name]

    def execute(self, *args, **kwargs):
        """Execute all registered handlers for this command. Return list of (success, result)."""
        results = []
        for handler in self.handlers:
            try:
                if callable(handler):
                    res = handler(*args, **kwargs)
                else:
                    method = getattr(handler, 'execute', None) or getattr(handler, '__call__', None)
                    if callable(method):
                        res = method(*args, **kwargs)
                    else:
                        raise TypeError(f"Command handler '{handler.__class__.__name__}' has no executable method")
                results.append((True, res))
            except Exception as exc:
                results.append((False, exc))
        return results

    def unregister(self, handler):
        """Remove a handler from the command registry.

        Accepts the exact callable/instance to remove or a class to remove any instance of that class.
        """
        lst = COMMANDS.get(self.name, [])
        if isinstance(handler, type):
            COMMANDS[self.name] = [h for h in lst if not (not callable(h) and isinstance(h, handler))]
        else:
            COMMANDS[self.name] = [h for h in lst if h is not handler]
