// Prompt: .github/prompts/encoder_index_file_tc_test.go.prompt.md
// Model: Claude Sonnet 4.5

package codec

import "time"

var EncoderIndexFileNoErrTestCases = []*EncoderIndexTestCase{
	{
		Name:        "SingleCheckpoint",
		Description: "Single checkpoint at a small offset to verify basic index file creation and retrieval",
		IndexData: []*TestIndexData{
			{
				TargetOffset: 100,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC),
			},
		},
	},
	{
		Name:        "TwoCheckpoints",
		Description: "Two checkpoints with moderate spacing to test sequential index entries",
		IndexData: []*TestIndexData{
			{
				TargetOffset: 200,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 500,
				Timestamp:    time.Date(2024, 1, 15, 10, 1, 0, 0, time.UTC),
			},
		},
	},
	{
		Name:        "MultipleCheckpointsMinimalSpacing",
		Description: "Multiple checkpoints with minimum allowed spacing of 16 bytes to test boundary conditions",
		IndexData: []*TestIndexData{
			{
				TargetOffset: 20,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 36,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 1, 0, time.UTC),
			},
			{
				TargetOffset: 52,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 2, 0, time.UTC),
			},
			{
				TargetOffset: 68,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 3, 0, time.UTC),
			},
			{
				TargetOffset: 84,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 4, 0, time.UTC),
			},
		},
	},
	{
		Name:        "SparseCheckpoints",
		Description: "Checkpoints with large gaps between them to test sparse index file handling",
		IndexData: []*TestIndexData{
			{
				TargetOffset: 100,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 2000,
				Timestamp:    time.Date(2024, 1, 15, 10, 5, 0, 0, time.UTC),
			},
			{
				TargetOffset: 5000,
				Timestamp:    time.Date(2024, 1, 15, 10, 15, 0, 0, time.UTC),
			},
			{
				TargetOffset: 9000,
				Timestamp:    time.Date(2024, 1, 15, 10, 30, 0, 0, time.UTC),
			},
		},
	},
	{
		Name:        "DenseCheckpoints",
		Description: "Many checkpoints with moderate spacing to test high-frequency checkpoint scenarios",
		IndexData: []*TestIndexData{
			{
				TargetOffset: 100,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 200,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 10, 0, time.UTC),
			},
			{
				TargetOffset: 300,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 20, 0, time.UTC),
			},
			{
				TargetOffset: 400,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 30, 0, time.UTC),
			},
			{
				TargetOffset: 500,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 40, 0, time.UTC),
			},
			{
				TargetOffset: 600,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 50, 0, time.UTC),
			},
			{
				TargetOffset: 700,
				Timestamp:    time.Date(2024, 1, 15, 10, 1, 0, 0, time.UTC),
			},
			{
				TargetOffset: 800,
				Timestamp:    time.Date(2024, 1, 15, 10, 1, 10, 0, time.UTC),
			},
		},
	},
	{
		Name:        "LargeOffsets",
		Description: "Checkpoints near the upper bound of the offset range to test handling of large file positions",
		IndexData: []*TestIndexData{
			{
				TargetOffset: 8000,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 8500,
				Timestamp:    time.Date(2024, 1, 15, 10, 1, 0, 0, time.UTC),
			},
			{
				TargetOffset: 9000,
				Timestamp:    time.Date(2024, 1, 15, 10, 2, 0, 0, time.UTC),
			},
			{
				TargetOffset: 9500,
				Timestamp:    time.Date(2024, 1, 15, 10, 3, 0, 0, time.UTC),
			},
			{
				TargetOffset: 10000,
				Timestamp:    time.Date(2024, 1, 15, 10, 4, 0, 0, time.UTC),
			},
		},
	},
	{
		Name:        "VaryingSpacing",
		Description: "Checkpoints with irregular spacing patterns to test flexible index file generation",
		IndexData: []*TestIndexData{
			{
				TargetOffset: 50,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 150,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 5, 0, time.UTC),
			},
			{
				TargetOffset: 200,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 8, 0, time.UTC),
			},
			{
				TargetOffset: 1000,
				Timestamp:    time.Date(2024, 1, 15, 10, 1, 0, 0, time.UTC),
			},
			{
				TargetOffset: 1500,
				Timestamp:    time.Date(2024, 1, 15, 10, 1, 30, 0, time.UTC),
			},
			{
				TargetOffset: 5000,
				Timestamp:    time.Date(2024, 1, 15, 10, 5, 0, 0, time.UTC),
			},
		},
	},
	{
		Name:        "HourlyCheckpoints",
		Description: "Checkpoints at hourly intervals to simulate periodic checkpoint scenarios",
		IndexData: []*TestIndexData{
			{
				TargetOffset: 100,
				Timestamp:    time.Date(2024, 1, 15, 10, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 1000,
				Timestamp:    time.Date(2024, 1, 15, 11, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 2000,
				Timestamp:    time.Date(2024, 1, 15, 12, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 3000,
				Timestamp:    time.Date(2024, 1, 15, 13, 0, 0, 0, time.UTC),
			},
			{
				TargetOffset: 4000,
				Timestamp:    time.Date(2024, 1, 15, 14, 0, 0, 0, time.UTC),
			},
		},
	},
}
