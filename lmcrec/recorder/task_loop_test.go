package recorder

import (
	"fmt"
	"testing"
	"time"
)

type TaskLoopTestTask struct {
	Interval time.Duration
	NumRuns  int
	crtRun   int
}

func (t *TaskLoopTestTask) task() bool {
	t.crtRun++
	return t.NumRuns <= 0 || t.crtRun < t.NumRuns
}

type TaskLoopTestCase struct {
	Name        string
	Description string
	Tasks       []*TaskLoopTestTask
}

func testTaskLoop(t *testing.T, tc *TaskLoopTestCase) {
	const SYNC_WAIT = 50 * time.Millisecond

	if tc.Description != "" {
		t.Log(tc.Description)
	}

	taskLoop := NewTaskLoop()

	// Start the tasks and set the wait. If all tasks will complete by
	// themselves then wait = max((NumRuns - 1) * Interval) otherwise wait
	// max(Interval) for tasks w/ NumRuns != 1.
	var doneWait, waitBeforeShutdown time.Duration
	doShutdown := false
	for i, tt := range tc.Tasks {
		tt.crtRun = 0
		err := taskLoop.Start(fmt.Sprintf("task#%d", i), tt.task, tt.Interval)
		if err != nil {
			t.Error(err)
		}
		if tt.NumRuns != 1 {
			waitBeforeShutdown = max(waitBeforeShutdown, tt.Interval)
		}
		if tt.NumRuns > 1 {
			doneWait = max(doneWait, time.Duration((tt.NumRuns-1))*tt.Interval)
		}
		if tt.NumRuns <= 0 {
			doShutdown = true
		}
	}

	if doShutdown {
		t.Logf("Call shutdown after %s", waitBeforeShutdown)
		time.Sleep(waitBeforeShutdown)
		err := taskLoop.ShutdownMaxWait(SYNC_WAIT)
		if err != nil {
			t.Error(err)
		}
	} else {
		doneWait += SYNC_WAIT
		t.Logf("Expect AllDone after %s", doneWait)

		timer := time.NewTimer(doneWait)
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
			t.Errorf("Shutdown did not complete after %s", doneWait)
		case <-taskLoop.AllDone:
			// Verify that all tasks ran to completion:
			for i, tt := range tc.Tasks {
				if tt.NumRuns != tt.crtRun {
					t.Errorf("task# %d crtRun: want: %d, got: %d", i, tt.NumRuns, tt.crtRun)
				}
			}
		}
	}
}

func TestTaskLoopNoErr(t *testing.T) {
	for _, tc := range TaskLoopNoErrTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testTaskLoop(t, tc) },
		)
	}
}

func TestTaskLoopDuplicate(t *testing.T) {
	const (
		TASK_ID  = "duplicate task"
		MAX_WAIT = 50 * time.Millisecond
	)

	task := func() bool { return true }
	taskLoop := NewTaskLoop()
	err := taskLoop.Start(TASK_ID, task, 1*time.Second)
	if err != nil {
		t.Errorf("Unexpected error %v", err)
	}
	err = taskLoop.Start(TASK_ID, task, 1*time.Second)
	if err == nil {
		t.Errorf("Expected error, got %v", err)
	} else {
		t.Log(err)
	}
	err = taskLoop.ShutdownMaxWait(MAX_WAIT)
	if err != nil {
		t.Errorf("Unexpected error %v", err)
	}
}
