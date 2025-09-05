import time

from ewokscore import Task


class SumTask(
    Task,
    input_names=["a"],
    optional_input_names=["b", "delay"],
    output_names=["result"],
):
    """Add two numbers"""

    def run(self):
        result = self.inputs.a + self.get_input_value("b", 0)
        time.sleep(self.get_input_value("delay", 0))
        self.outputs.result = result


class SumTask1(
    Task,
    input_names=["a"],
    optional_input_names=["b", "delay"],
    output_names=["result"],
):
    """Add two numbers"""

    def run(self):
        result = self.inputs.a + self.get_input_value("b", 0)
        time.sleep(self.get_input_value("delay", 0))
        self.outputs.result = result


class SumTask2(
    Task,
    input_names=["a"],
    optional_input_names=["b", "delay"],
    output_names=["result"],
):
    """Add two numbers"""

    def run(self):
        result = self.inputs.a + self.get_input_value("b", 0)
        time.sleep(self.get_input_value("delay", 0))
        self.outputs.result = result
