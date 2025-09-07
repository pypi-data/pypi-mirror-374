import shlex
import subprocess
from wizlib.parser import WizParser
from yaml import safe_load

from dyngle.command import DyngleCommand
from dyngle.template import Template
from dyngle import DyngleError


class RunCommand(DyngleCommand):
    """Run a workflow defined in the configuration"""

    name = 'run'

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('operation', help='Operation name to run')

    def handle_vals(self):
        super().handle_vals()

    def _validate_operation_exists(self, operations):
        """Validate that the requested operation exists in configuration"""
        if self.operation not in operations:
            available_operations = ', '.join(operations.keys())
            raise DyngleError(
                f'Operation "{self.operation}" not found. " + \
                    f"Available operations: {available_operations}')

    @DyngleCommand.wrap
    def execute(self):
        operations = self.app.config.get('dyngle-operations')
        self._validate_operation_exists(operations)
        steps = operations[self.operation]
        data_string = self.app.stream.text
        data = safe_load(data_string)
        for step_template in steps:
            step = Template(step_template).render(data)
            parts = shlex.split(step)
            result = subprocess.run(parts)
            if result.returncode != 0:
                raise DyngleError(
                    f'Task failed with code {result.returncode}: {step}')

        return f'Operation "{self.operation}" completed successfully'
