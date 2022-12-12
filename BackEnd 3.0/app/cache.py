import time


class Cache:
    def __init__(self, default_timeout=60):
        self.cache = {}
        self.default_timeout = default_timeout
        self.last_checked = 0

    def __contains__(self, item):
        return item in self.cache

    def set(self, key, value, timeout=None):
        if time.time() - self.last_checked > 600:
            self.clean()

        if timeout is None:
            timeout = self.default_timeout

        self.cache[key] = {"value": value, "expire_by": time.time() + timeout}

    def get(self, key):
        if time.time() - self.last_checked > 600:
            self.clean()

        if key in self.cache:
            entry = self.cache[key]

            if time.time() > entry["expire_by"]:
                self.cache.pop(key)
            else:
                return entry["value"]
        return None

    def clean(self):
        self.cache = {i: j for i, j in self.cache.items() if j["expire_by"] > time.time()}
        self.last_checked = time.time()
