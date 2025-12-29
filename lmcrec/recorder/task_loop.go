package recorder

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// A task is represented by a function that should be invoked periodically. The
// function returns a boolean indicating if the task can be rescheduled (true)
// or not (false). Tasks can be started but not stopped, they continue until
// either they run into a non-recoverable condition and return false or the
// whole loop is cancelled.

// The main event loop polls, via select, for terminating signals, in which case
// it cancels the loop and all its tasks, or for the condition where all loop
// tasks were self-terminated due to some error.

// Typical event loop:

// func main() {
// 	taskLoop := NewTaskLoop()
// 	taskLoop.Start("task1", task1, interval1)
// 	sigChan := make(chan os.Signal, 1)
// 	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
// 	for run := true; run; {
// 		select {
// 		case sig := <-sigChan:
// 			switch sig {
// 			case os.Interrupt, syscall.SIGTERM:
// 				taskLoop.Shutdown()
// 				run = false
// 			}
// 		case <-taskLoop.AllDone:
// 			run = false
// 		}
// 	}
// }

type TaskLoop struct {
	// A channel to be polled by the main event loop to check if all tasks self
	// terminated. When the latter occurs the channel will be closed so the
	// `case <- AllDone' will match the select clause.
	AllDone chan any

	// The context used to cancel the loop; all tasks are supposed to use it as
	// a cancel context.
	Ctx context.Context

	// The cancel function:
	cancelFunc context.CancelFunc

	// Whether AllDone watcher is active or not:
	activeWatcher bool

	// The wait group used for task completion:
	wg *sync.WaitGroup

	// Running tasks map keyed by taskId, used to avoid duplicate invocation:
	tasks map[string]bool

	// Atomic operations lock:
	lck *sync.Mutex
}

func NewTaskLoop() *TaskLoop {
	tl := &TaskLoop{
		AllDone: make(chan any),
		wg:      &sync.WaitGroup{},
		tasks:   make(map[string]bool),
		lck:     &sync.Mutex{},
	}
	tl.Ctx, tl.cancelFunc = context.WithCancel(context.Background())
	return tl
}

func (tl *TaskLoop) Start(id string, task func() bool, interval time.Duration) error {
	tl.lck.Lock()
	defer tl.lck.Unlock()

	if tl.tasks[id] {
		return fmt.Errorf("task %q already running", id)
	}

	if !tl.activeWatcher {
		go func() {
			tl.wg.Wait()
			close(tl.AllDone)
		}()
		tl.activeWatcher = true
	}

	tl.tasks[id] = true
	tl.wg.Add(1)

	go func() {
		nextTs := time.Now()
		timer := time.NewTimer(0)
		defer func() {
			if !timer.Stop() {
				select {
				case <-timer.C:
				default:
				}
			}
		}()

		for run := true; run; {
			select {
			case <-tl.Ctx.Done():
				run = false
			case <-timer.C:
				nextTs = nextTs.Add(interval)
				timer.Reset(max(time.Until(nextTs), 0))
				run = task()
			}
		}
		tl.wg.Done()
	}()

	return nil
}

func (tl *TaskLoop) Shutdown() {
	tl.cancelFunc()
	tl.wg.Wait()
}

func (tl *TaskLoop) ShutdownMaxWait(wait time.Duration) error {
	done := make(chan any)
	go func() {
		tl.Shutdown()
		close(done)
	}()
	timer := time.NewTimer(wait)
	defer func() {
		if !timer.Stop() {
			select {
			case <-timer.C:
			default:
			}
		}
	}()
	select {
	case <-timer.C:
		return fmt.Errorf("shutdown timeout after %s", wait)
	case <-done:
		return nil
	}
}
