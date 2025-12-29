// Prompt: .github/prompts/task_loop_no_err_tc_test.go.prompt.md
// Model: Claude Sonnet 4.5
package recorder

import "time"

var TaskLoopNoErrTestCases = []*TaskLoopTestCase{
	{
		Name:        "SingleTaskRunOnce",
		Description: "Single task that runs once and completes",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 50 * time.Millisecond,
				NumRuns:  1,
			},
		},
	},
	{
		Name:        "SingleTaskMultipleRuns",
		Description: "Single task that runs 5 times before completing",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 50 * time.Millisecond,
				NumRuns:  5,
			},
		},
	},
	{
		Name:        "MultipleTasksSameInterval",
		Description: "Three tasks with the same interval, each running 3 times",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 75 * time.Millisecond,
				NumRuns:  3,
			},
			{
				Interval: 75 * time.Millisecond,
				NumRuns:  3,
			},
			{
				Interval: 75 * time.Millisecond,
				NumRuns:  3,
			},
		},
	},
	{
		Name:        "MultipleTasksDifferentIntervals",
		Description: "Three tasks with different intervals and run counts",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 50 * time.Millisecond,
				NumRuns:  2,
			},
			{
				Interval: 100 * time.Millisecond,
				NumRuns:  3,
			},
			{
				Interval: 150 * time.Millisecond,
				NumRuns:  4,
			},
		},
	},
	{
		Name:        "MixedRunOnceTasks",
		Description: "Mix of tasks where some run once and others multiple times",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 50 * time.Millisecond,
				NumRuns:  1,
			},
			{
				Interval: 100 * time.Millisecond,
				NumRuns:  4,
			},
			{
				Interval: 75 * time.Millisecond,
				NumRuns:  1,
			},
		},
	},
	{
		Name:        "TaskWithInfiniteRunsRequiresShutdown",
		Description: "Task with NumRuns <= 0 runs indefinitely until shutdown",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 50 * time.Millisecond,
				NumRuns:  0,
			},
		},
	},
	{
		Name:        "MixedFiniteAndInfiniteTasksRequiresShutdown",
		Description: "Mix of finite and infinite tasks, requires manual shutdown",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 60 * time.Millisecond,
				NumRuns:  2,
			},
			{
				Interval: 80 * time.Millisecond,
				NumRuns:  0,
			},
			{
				Interval: 100 * time.Millisecond,
				NumRuns:  3,
			},
		},
	},
	{
		Name:        "HighFrequencyTask",
		Description: "Task running at minimum interval (50ms) for 10 iterations",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 50 * time.Millisecond,
				NumRuns:  10,
			},
		},
	},
	{
		Name:        "LowFrequencyTask",
		Description: "Task running at longer interval (500ms) for 3 iterations",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 500 * time.Millisecond,
				NumRuns:  3,
			},
		},
	},
	{
		Name:        "ManyTasksDifferentPatterns",
		Description: "Five tasks with varying intervals and run counts to test concurrent execution",
		Tasks: []*TaskLoopTestTask{
			{
				Interval: 50 * time.Millisecond,
				NumRuns:  5,
			},
			{
				Interval: 75 * time.Millisecond,
				NumRuns:  3,
			},
			{
				Interval: 100 * time.Millisecond,
				NumRuns:  2,
			},
			{
				Interval: 125 * time.Millisecond,
				NumRuns:  4,
			},
			{
				Interval: 150 * time.Millisecond,
				NumRuns:  2,
			},
		},
	},
}
