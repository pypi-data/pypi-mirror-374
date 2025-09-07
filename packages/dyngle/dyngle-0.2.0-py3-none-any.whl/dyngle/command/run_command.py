import shlex
import subprocess
from wizlib.parser import WizParser

from dyngle.command import DyngleCommand


class RunCommand(DyngleCommand):
    """Run a workflow defined in the configuration"""

    name = 'run'

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('flow', help='Operation name to run')

    def handle_vals(self):
        super().handle_vals()
        if not self.provided('flow'):
            self.flow = self.app.ui.get_input('Enter flow name: ')

    def _validate_flow_exists(self, operations):
        """Validate that the requested flow exists in configuration"""
        if not operations:
            raise RuntimeError('No operations configured')

        if self.flow not in operations:
            available_operations = ', '.join(operations.keys())
            raise RuntimeError(
                f'Operation "{self.flow}" not found. " + \
                    f"Available operations: {available_operations}')

    def _execute_task(self, task_str):
        """Execute a single task and handle errors"""
        task_parts = shlex.split(task_str)
        result = subprocess.run(task_parts)

        if result.returncode != 0:
            raise RuntimeError(
                f'Task failed with code {result.returncode}: {task_str}')

    @DyngleCommand.wrap
    def execute(self):
        operations = self.app.config.get('dyngle-operations')
        self._validate_flow_exists(operations)

        tasks = operations[self.flow]
        for task_str in tasks:
            self._execute_task(task_str)

        return f'Operation "{self.flow}" completed successfully'
