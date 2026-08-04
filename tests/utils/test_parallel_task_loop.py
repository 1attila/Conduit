import time
from mconduit.utils.parallel_task_loop import ParallelTaskLoop


def test_parallel_task_loop_execution():

    loop = ParallelTaskLoop(interval=0.1)
    
    execution_count = 0
    def dummy_task(amount):
        nonlocal execution_count
        execution_count += amount

    loop.add_task(dummy_task, 2)
    
    assert loop.tasks == ["dummy_task"]
    
    loop.start()
    time.sleep(0.35)
    loop.stop()
    
    # Needs to have ticked at least 3 times
    assert execution_count >= 6
    

def test_parallel_task_loop_exception_handling(capsys):

    loop = ParallelTaskLoop(interval=0.1)
    
    def failing_task():
        raise ValueError("Test error")
        
    loop.add_task(failing_task)
    loop.start()
    time.sleep(0.2)
    loop.stop()
    
    captured = capsys.readouterr()
    assert "ValueError: Test error" in captured.err


def test_parallel_task_loop_immediate_stop():
    
    loop = ParallelTaskLoop(interval=10.0) # Notice long interval
    
    def dummy():
        pass
        
    loop.add_task(dummy)
    loop.start()
    
    start_time = time.time()
    loop.stop()
    end_time = time.time()
    
    # Verification that the Thread Event fixes the sleep issue and breaks bounds under 1 sec
    assert end_time - start_time < 1.0