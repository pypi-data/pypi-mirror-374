from dataclasses import dataclass
from functools import partial
import re


PATTERN = re.compile(r'\{\{\s*([^}]+)\s*\}\}')


@dataclass
class Template:

    template: str

    def render(self, data):
        """Render the template with the provided data."""
        resolver = partial(self._resolve, data=data)
        return PATTERN.sub(resolver, self.template)

    def _resolve(self, match, *, data):
        """Resolve a single name/path from the template."""
        path = match.group(1).strip()
        # Try an expression first, then data
        if False:
            pass
        else:
            parts = path.split('.')
            current = data
            for part in parts:
                current = current[part]
            return current
