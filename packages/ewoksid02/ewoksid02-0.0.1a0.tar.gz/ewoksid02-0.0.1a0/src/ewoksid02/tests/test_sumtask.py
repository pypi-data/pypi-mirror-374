import pytest

from ewoksid02.tasks.sumtask import SumTask, SumTask1, SumTask2


@pytest.mark.parametrize("Task", [SumTask, SumTask1, SumTask2])
def test_sum_task(Task):
    task = Task(inputs={"a": 1, "b": 2})
    task.run()
    assert task.outputs.result == 3
