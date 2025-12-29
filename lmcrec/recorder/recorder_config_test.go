// Prompt: .github/prompts/recorder_config_test.go.prompt.md
// Model: Claude Sonnet 4.5
package recorder

import (
	"testing"
	"time"

	"lmcrec/codec"
)

func TestLoadRecorderConfigDefaultOnly(t *testing.T) {
	var (
		Name        = "DefaultOnly"
		Description = "Load config with only default section, no recorders"
		yamlConfig  = `
default:
  scan_interval: 10s
  flush_interval: 10m
  checkpoint_interval: 2h
  rollover_interval: 12h
  midnight_rollover: false
  parse_error_threshold: 10
  url: "http://example.com:9090/data"
  security_key: "test-key"
  compressed_requests: "remote_only"
  request_timeout: 5s
  ignore_tls_verify: false
  tcp_conn_timeout: 3s
  record_files_dir: "/tmp/rec"
  buf_size: 8192
  compression_level: 6
recorders:
  - inst: "test-recorder"
`
	)

	config, _, err := loadLmcrecConfig("test.yaml", "test-recorder", []byte(yamlConfig))
	if err != nil {
		t.Fatalf("%s: %s: unexpected error: %v", Name, Description, err)
	}

	var want, got interface{}

	if config.ScanInterval == nil {
		t.Error("field ScanInterval should not be nil")
	} else if want, got = 10*time.Second, *config.ScanInterval; want != got {
		t.Errorf("field ScanInterval: want: %v, got: %v", want, got)
	}

	if config.FlushInterval == nil {
		t.Error("field FlushInterval should not be nil")
	} else if want, got = 10*time.Minute, *config.FlushInterval; want != got {
		t.Errorf("field FlushInterval: want: %v, got: %v", want, got)
	}

	if config.CheckpointInterval == nil {
		t.Error("field CheckpointInterval should not be nil")
	} else if want, got = 2*time.Hour, *config.CheckpointInterval; want != got {
		t.Errorf("field CheckpointInterval: want: %v, got: %v", want, got)
	}

	if config.RolloverInterval == nil {
		t.Error("field RolloverInterval should not be nil")
	} else if want, got = 12*time.Hour, *config.RolloverInterval; want != got {
		t.Errorf("field RolloverInterval: want: %v, got: %v", want, got)
	}

	if config.MidnightRollover == nil {
		t.Error("field MidnightRollover should not be nil")
	} else if want, got = false, *config.MidnightRollover; want != got {
		t.Errorf("field MidnightRollover: want: %v, got: %v", want, got)
	}

	if config.ParseErrorThreshold == nil {
		t.Error("field ParseErrorThreshold should not be nil")
	} else if want, got = 10, *config.ParseErrorThreshold; want != got {
		t.Errorf("field ParseErrorThreshold: want: %v, got: %v", want, got)
	}

	if config.URL == nil {
		t.Error("field URL should not be nil")
	} else if want, got = "http://example.com:9090/data", *config.URL; want != got {
		t.Errorf("field URL: want: %v, got: %v", want, got)
	}

	if config.SecurityKey == nil {
		t.Error("field SecurityKey should not be nil")
	} else if want, got = "test-key", *config.SecurityKey; want != got {
		t.Errorf("field SecurityKey: want: %v, got: %v", want, got)
	}

	if config.CompressedRequests == nil {
		t.Error("field CompressedRequests should not be nil")
	} else if want, got = "remote_only", *config.CompressedRequests; want != got {
		t.Errorf("field CompressedRequests: want: %v, got: %v", want, got)
	}

	if config.RequestTimeout == nil {
		t.Error("field RequestTimeout should not be nil")
	} else if want, got = 5*time.Second, *config.RequestTimeout; want != got {
		t.Errorf("field RequestTimeout: want: %v, got: %v", want, got)
	}

	if config.IgnoreTlsVerify == nil {
		t.Error("field IgnoreTlsVerify should not be nil")
	} else if want, got = false, *config.IgnoreTlsVerify; want != got {
		t.Errorf("field IgnoreTlsVerify: want: %v, got: %v", want, got)
	}

	if config.TcpConnTimeout == nil {
		t.Error("field TcpConnTimeout should not be nil")
	} else if want, got = 3*time.Second, *config.TcpConnTimeout; want != got {
		t.Errorf("field TcpConnTimeout: want: %v, got: %v", want, got)
	}

	if config.RecordFilesDir == nil {
		t.Error("field RecordFilesDir should not be nil")
	} else if want, got = "/tmp/rec", *config.RecordFilesDir; want != got {
		t.Errorf("field RecordFilesDir: want: %v, got: %v", want, got)
	}

	if config.BufSize == nil {
		t.Error("field BufSize should not be nil")
	} else if want, got = 8192, *config.BufSize; want != got {
		t.Errorf("field BufSize: want: %v, got: %v", want, got)
	}

	if config.CompressionLevel == nil {
		t.Error("field CompressionLevel should not be nil")
	} else if want, got = 6, *config.CompressionLevel; want != got {
		t.Errorf("field CompressionLevel: want: %v, got: %v", want, got)
	}
}

func TestLoadRecorderConfigMatchByInst(t *testing.T) {
	var (
		Name        = "MatchByInst"
		Description = "Load config matching recorder by inst field"
		yamlConfig  = `
default:
  scan_interval: 5s
  flush_interval: 5m
recorders:
  - inst: "recorder-one"
    url: "http://host1.com/api"
    request_timeout: 10s
  - inst: "recorder-two"
    url: "http://host2.com/api"
    request_timeout: 15s
`
	)

	config, _, err := loadLmcrecConfig("test.yaml", "recorder-two", []byte(yamlConfig))
	if err != nil {
		t.Fatalf("%s: %s: unexpected error: %v", Name, Description, err)
	}

	var want, got interface{}

	if config.Inst == nil {
		t.Error("field Inst should not be nil")
	} else if want, got = "recorder-two", *config.Inst; want != got {
		t.Errorf("field Inst: want: %v, got: %v", want, got)
	}

	if config.URL == nil {
		t.Error("field URL should not be nil")
	} else if want, got = "http://host2.com/api", *config.URL; want != got {
		t.Errorf("field URL: want: %v, got: %v", want, got)
	}

	if config.RequestTimeout == nil {
		t.Error("field RequestTimeout should not be nil")
	} else if want, got = 15*time.Second, *config.RequestTimeout; want != got {
		t.Errorf("field RequestTimeout: want: %v, got: %v", want, got)
	}

	// Check default values are applied
	if config.ScanInterval == nil {
		t.Error("field ScanInterval should not be nil")
	} else if want, got = 5*time.Second, *config.ScanInterval; want != got {
		t.Errorf("field ScanInterval: want: %v, got: %v", want, got)
	}

	if config.FlushInterval == nil {
		t.Error("field FlushInterval should not be nil")
	} else if want, got = 5*time.Minute, *config.FlushInterval; want != got {
		t.Errorf("field FlushInterval: want: %v, got: %v", want, got)
	}
}

func TestLoadRecorderConfigMatchByURL(t *testing.T) {
	var (
		Name        = "MatchByURL"
		Description = "Load config matching recorder by URL when inst not specified"
		yamlConfig  = `
default:
  scan_interval: 7s
recorders:
  - url: "http://host1.com/api"
    flush_interval: 8m
  - url: "http://host2.com/api"
    flush_interval: 12m
`
	)

	config, _, err := loadLmcrecConfig("test.yaml", "http://host2.com/api", []byte(yamlConfig))
	if err != nil {
		t.Fatalf("%s: %s: unexpected error: %v", Name, Description, err)
	}

	var want, got interface{}

	if config.URL == nil {
		t.Error("field URL should not be nil")
	} else if want, got = "http://host2.com/api", *config.URL; want != got {
		t.Errorf("field URL: want: %v, got: %v", want, got)
	}

	if config.FlushInterval == nil {
		t.Error("field FlushInterval should not be nil")
	} else if want, got = 12*time.Minute, *config.FlushInterval; want != got {
		t.Errorf("field FlushInterval: want: %v, got: %v", want, got)
	}

	if config.ScanInterval == nil {
		t.Error("field ScanInterval should not be nil")
	} else if want, got = 7*time.Second, *config.ScanInterval; want != got {
		t.Errorf("field ScanInterval: want: %v, got: %v", want, got)
	}
}

func TestLoadRecorderConfigNoMatch(t *testing.T) {
	var (
		Name        = "NoMatch"
		Description = "Error when no recorder matches the requested instance"
		yamlConfig  = `
recorders:
  - inst: "recorder-one"
    url: "http://host1.com/api"
`
	)

	_, _, err := loadLmcrecConfig("test.yaml", "non-existent", []byte(yamlConfig))
	if err == nil {
		t.Fatalf("%s: %s: expected error but got none", Name, Description)
	}
}

func TestLoadRecorderConfigOverrideDefaults(t *testing.T) {
	var (
		Name        = "OverrideDefaults"
		Description = "Recorder-specific config overrides default values while preserving non-overridden defaults"
		yamlConfig  = `
default:
  scan_interval: 5s
  flush_interval: 5m
  checkpoint_interval: 30m
  rollover_interval: 6h
  midnight_rollover: true
  parse_error_threshold: 5
  url: "http://default.com"
  security_key: "default-key"
  compressed_requests: "remote_only"
  request_timeout: 2s
  ignore_tls_verify: false
  tcp_conn_timeout: 1s
  record_files_dir: "$LMCREC_RUNTIME/rec/<INST>"
  buf_size: 4096
  compression_level: 5
recorders:
  - inst: "custom-recorder"
    scan_interval: 15s
    url: "http://custom.com"
    parse_error_threshold: 20
`
	)

	config, _, err := loadLmcrecConfig("test.yaml", "custom-recorder", []byte(yamlConfig))
	if err != nil {
		t.Fatalf("%s: %s: unexpected error: %v", Name, Description, err)
	}

	var want, got interface{}

	// Overridden values
	if config.ScanInterval == nil {
		t.Error("field ScanInterval should not be nil")
	} else if want, got = 15*time.Second, *config.ScanInterval; want != got {
		t.Errorf("field ScanInterval: want: %v, got: %v", want, got)
	}

	if config.URL == nil {
		t.Error("field URL should not be nil")
	} else if want, got = "http://custom.com", *config.URL; want != got {
		t.Errorf("field URL: want: %v, got: %v", want, got)
	}

	if config.ParseErrorThreshold == nil {
		t.Error("field ParseErrorThreshold should not be nil")
	} else if want, got = 20, *config.ParseErrorThreshold; want != got {
		t.Errorf("field ParseErrorThreshold: want: %v, got: %v", want, got)
	}

	// Default values preserved
	if config.FlushInterval == nil {
		t.Error("field FlushInterval should not be nil")
	} else if want, got = 5*time.Minute, *config.FlushInterval; want != got {
		t.Errorf("field FlushInterval: want: %v, got: %v", want, got)
	}

	if config.CheckpointInterval == nil {
		t.Error("field CheckpointInterval should not be nil")
	} else if want, got = 30*time.Minute, *config.CheckpointInterval; want != got {
		t.Errorf("field CheckpointInterval: want: %v, got: %v", want, got)
	}

	if config.RolloverInterval == nil {
		t.Error("field RolloverInterval should not be nil")
	} else if want, got = 6*time.Hour, *config.RolloverInterval; want != got {
		t.Errorf("field RolloverInterval: want: %v, got: %v", want, got)
	}

	if config.MidnightRollover == nil {
		t.Error("field MidnightRollover should not be nil")
	} else if want, got = true, *config.MidnightRollover; want != got {
		t.Errorf("field MidnightRollover: want: %v, got: %v", want, got)
	}

	if config.SecurityKey == nil {
		t.Error("field SecurityKey should not be nil")
	} else if want, got = "default-key", *config.SecurityKey; want != got {
		t.Errorf("field SecurityKey: want: %v, got: %v", want, got)
	}

	if config.CompressedRequests == nil {
		t.Error("field CompressedRequests should not be nil")
	} else if want, got = "remote_only", *config.CompressedRequests; want != got {
		t.Errorf("field CompressedRequests: want: %v, got: %v", want, got)
	}

	if config.RequestTimeout == nil {
		t.Error("field RequestTimeout should not be nil")
	} else if want, got = 2*time.Second, *config.RequestTimeout; want != got {
		t.Errorf("field RequestTimeout: want: %v, got: %v", want, got)
	}

	if config.IgnoreTlsVerify == nil {
		t.Error("field IgnoreTlsVerify should not be nil")
	} else if want, got = false, *config.IgnoreTlsVerify; want != got {
		t.Errorf("field IgnoreTlsVerify: want: %v, got: %v", want, got)
	}

	if config.TcpConnTimeout == nil {
		t.Error("field TcpConnTimeout should not be nil")
	} else if want, got = 1*time.Second, *config.TcpConnTimeout; want != got {
		t.Errorf("field TcpConnTimeout: want: %v, got: %v", want, got)
	}

	if config.RecordFilesDir == nil {
		t.Error("field RecordFilesDir should not be nil")
	} else if want, got = "$LMCREC_RUNTIME/rec/<INST>", *config.RecordFilesDir; want != got {
		t.Errorf("field RecordFilesDir: want: %v, got: %v", want, got)
	}

	if config.BufSize == nil {
		t.Error("field BufSize should not be nil")
	} else if want, got = 4096, *config.BufSize; want != got {
		t.Errorf("field BufSize: want: %v, got: %v", want, got)
	}

	if config.CompressionLevel == nil {
		t.Error("field CompressionLevel should not be nil")
	} else if want, got = 5, *config.CompressionLevel; want != got {
		t.Errorf("field CompressionLevel: want: %v, got: %v", want, got)
	}
}

func TestLoadRecorderConfigNoDefaultSection(t *testing.T) {
	var (
		Name        = "NoDefaultSection"
		Description = "Apply hardcoded defaults when no default section is provided"
		yamlConfig  = `
recorders:
  - inst: "minimal-recorder"
    url: "http://minimal.com"
`
	)

	config, _, err := loadLmcrecConfig("test.yaml", "minimal-recorder", []byte(yamlConfig))
	if err != nil {
		t.Fatalf("%s: %s: unexpected error: %v", Name, Description, err)
	}

	var want, got interface{}

	if config.ScanInterval == nil {
		t.Error("field ScanInterval should not be nil")
	} else if want, got = RECORDER_CONFIG_SCAN_INTERVAL_DEFAULT, *config.ScanInterval; want != got {
		t.Errorf("field ScanInterval: want: %v, got: %v", want, got)
	}

	if config.FlushInterval == nil {
		t.Error("field FlushInterval should not be nil")
	} else if want, got = RECORDER_CONFIG_FLUSH_INTERVAL_DEFAULT, *config.FlushInterval; want != got {
		t.Errorf("field FlushInterval: want: %v, got: %v", want, got)
	}

	if config.CheckpointInterval == nil {
		t.Error("field CheckpointInterval should not be nil")
	} else if want, got = RECORDER_CONFIG_CHECKPOINT_INTERVAL_DEFAULT, *config.CheckpointInterval; want != got {
		t.Errorf("field CheckpointInterval: want: %v, got: %v", want, got)
	}

	if config.RolloverInterval == nil {
		t.Error("field RolloverInterval should not be nil")
	} else if want, got = RECORDER_CONFIG_ROLLOVER_INTERVAL_DEFAULT, *config.RolloverInterval; want != got {
		t.Errorf("field RolloverInterval: want: %v, got: %v", want, got)
	}

	if config.MidnightRollover == nil {
		t.Error("field MidnightRollover should not be nil")
	} else if want, got = RECORDER_CONFIG_MIDNIGHT_ROLLOVER_DEFAULT, *config.MidnightRollover; want != got {
		t.Errorf("field MidnightRollover: want: %v, got: %v", want, got)
	}

	if config.ParseErrorThreshold == nil {
		t.Error("field ParseErrorThreshold should not be nil")
	} else if want, got = RECORDER_CONFIG_PARSE_ERROR_THRESHOLD_DEFAULT, *config.ParseErrorThreshold; want != got {
		t.Errorf("field ParseErrorThreshold: want: %v, got: %v", want, got)
	}

	if config.SecurityKey == nil {
		t.Error("field SecurityKey should not be nil")
	} else if want, got = RECORDER_CONFIG_SECURITY_KEY_DEFAULT, *config.SecurityKey; want != got {
		t.Errorf("field SecurityKey: want: %v, got: %v", want, got)
	}

	if config.CompressedRequests == nil {
		t.Error("field CompressedRequests should not be nil")
	} else if want, got = RECORDER_CONFIG_COMPRESSED_REQUESTS_DEFAULT, *config.CompressedRequests; want != got {
		t.Errorf("field CompressedRequests: want: %v, got: %v", want, got)
	}

	if config.RequestTimeout == nil {
		t.Error("field RequestTimeout should not be nil")
	} else if want, got = RECORDER_CONFIG_REQUEST_TIMEOUT_DEFAULT, *config.RequestTimeout; want != got {
		t.Errorf("field RequestTimeout: want: %v, got: %v", want, got)
	}

	if config.IgnoreTlsVerify == nil {
		t.Error("field IgnoreTlsVerify should not be nil")
	} else if want, got = RECORDER_CONFIG_IGNORE_TLS_VERIFY_DEFAULT, *config.IgnoreTlsVerify; want != got {
		t.Errorf("field IgnoreTlsVerify: want: %v, got: %v", want, got)
	}

	if config.TcpConnTimeout == nil {
		t.Error("field TcpConnTimeout should not be nil")
	} else if want, got = RECORDER_CONFIG_TCP_CONNECTION_TIMEOUT_DEFAULT, *config.TcpConnTimeout; want != got {
		t.Errorf("field TcpConnTimeout: want: %v, got: %v", want, got)
	}

	if config.RecordFilesDir == nil {
		t.Error("field RecordFilesDir should not be nil")
	} else if want, got = RECORDER_CONFIG_RECORD_FILES_DIR_DEFAULT, *config.RecordFilesDir; want != got {
		t.Errorf("field RecordFilesDir: want: %v, got: %v", want, got)
	}

	if config.BufSize == nil {
		t.Error("field BufSize should not be nil")
	} else if want, got = RECORDER_CONFIG_RECORD_BUFSIZE_DEFAULT, *config.BufSize; want != got {
		t.Errorf("field BufSize: want: %v, got: %v", want, got)
	}

	if config.CompressionLevel == nil {
		t.Error("field CompressionLevel should not be nil")
	} else if want, got = RECORDER_CONFIG_COMPRESSION_LEVEL_DEFAULT, *config.CompressionLevel; want != got {
		t.Errorf("field CompressionLevel: want: %v, got: %v", want, got)
	}
}

func TestLoadRecorderConfigAllFieldTypes(t *testing.T) {
	var (
		Name        = "AllFieldTypes"
		Description = "Verify all field types are correctly parsed and applied"
		yamlConfig  = `
recorders:
  - inst: "full-config"
    scan_interval: 20s
    flush_interval: 15m
    checkpoint_interval: 45m
    rollover_interval: 8h
    midnight_rollover: false
    parse_error_threshold: 15
    url: "https://secure.example.com:8443/api"
    security_key: "env:MY_SECRET_KEY"
    compressed_requests: "true"
    request_timeout: 30s
    ignore_tls_verify: true
    tcp_conn_timeout: 5s
    tcp_keep_alive: 60s
    record_files_dir: "/custom/path/recordings"
    buf_size: 16384
    compression_level: 9
`
	)

	config, _, err := loadLmcrecConfig("test.yaml", "full-config", []byte(yamlConfig))
	if err != nil {
		t.Fatalf("%s: %s: unexpected error: %v", Name, Description, err)
	}

	var want, got interface{}

	if config.Inst == nil {
		t.Error("field Inst should not be nil")
	} else if want, got = "full-config", *config.Inst; want != got {
		t.Errorf("field Inst: want: %v, got: %v", want, got)
	}

	if config.ScanInterval == nil {
		t.Error("field ScanInterval should not be nil")
	} else if want, got = 20*time.Second, *config.ScanInterval; want != got {
		t.Errorf("field ScanInterval: want: %v, got: %v", want, got)
	}

	if config.FlushInterval == nil {
		t.Error("field FlushInterval should not be nil")
	} else if want, got = 15*time.Minute, *config.FlushInterval; want != got {
		t.Errorf("field FlushInterval: want: %v, got: %v", want, got)
	}

	if config.CheckpointInterval == nil {
		t.Error("field CheckpointInterval should not be nil")
	} else if want, got = 45*time.Minute, *config.CheckpointInterval; want != got {
		t.Errorf("field CheckpointInterval: want: %v, got: %v", want, got)
	}

	if config.RolloverInterval == nil {
		t.Error("field RolloverInterval should not be nil")
	} else if want, got = 8*time.Hour, *config.RolloverInterval; want != got {
		t.Errorf("field RolloverInterval: want: %v, got: %v", want, got)
	}

	if config.MidnightRollover == nil {
		t.Error("field MidnightRollover should not be nil")
	} else if want, got = false, *config.MidnightRollover; want != got {
		t.Errorf("field MidnightRollover: want: %v, got: %v", want, got)
	}

	if config.ParseErrorThreshold == nil {
		t.Error("field ParseErrorThreshold should not be nil")
	} else if want, got = 15, *config.ParseErrorThreshold; want != got {
		t.Errorf("field ParseErrorThreshold: want: %v, got: %v", want, got)
	}

	if config.URL == nil {
		t.Error("field URL should not be nil")
	} else if want, got = "https://secure.example.com:8443/api", *config.URL; want != got {
		t.Errorf("field URL: want: %v, got: %v", want, got)
	}

	if config.SecurityKey == nil {
		t.Error("field SecurityKey should not be nil")
	} else if want, got = "env:MY_SECRET_KEY", *config.SecurityKey; want != got {
		t.Errorf("field SecurityKey: want: %v, got: %v", want, got)
	}

	if config.CompressedRequests == nil {
		t.Error("field CompressedRequests should not be nil")
	} else if want, got = "true", *config.CompressedRequests; want != got {
		t.Errorf("field CompressedRequests: want: %v, got: %v", want, got)
	}

	if config.RequestTimeout == nil {
		t.Error("field RequestTimeout should not be nil")
	} else if want, got = 30*time.Second, *config.RequestTimeout; want != got {
		t.Errorf("field RequestTimeout: want: %v, got: %v", want, got)
	}

	if config.IgnoreTlsVerify == nil {
		t.Error("field IgnoreTlsVerify should not be nil")
	} else if want, got = true, *config.IgnoreTlsVerify; want != got {
		t.Errorf("field IgnoreTlsVerify: want: %v, got: %v", want, got)
	}

	if config.TcpConnTimeout == nil {
		t.Error("field TcpConnTimeout should not be nil")
	} else if want, got = 5*time.Second, *config.TcpConnTimeout; want != got {
		t.Errorf("field TcpConnTimeout: want: %v, got: %v", want, got)
	}

	if config.TcpKeepAlive == nil {
		t.Error("field TcpKeepAlive should not be nil")
	} else if want, got = 60*time.Second, *config.TcpKeepAlive; want != got {
		t.Errorf("field TcpKeepAlive: want: %v, got: %v", want, got)
	}

	if config.RecordFilesDir == nil {
		t.Error("field RecordFilesDir should not be nil")
	} else if want, got = "/custom/path/recordings", *config.RecordFilesDir; want != got {
		t.Errorf("field RecordFilesDir: want: %v, got: %v", want, got)
	}

	if config.BufSize == nil {
		t.Error("field BufSize should not be nil")
	} else if want, got = 16384, *config.BufSize; want != got {
		t.Errorf("field BufSize: want: %v, got: %v", want, got)
	}

	if config.CompressionLevel == nil {
		t.Error("field CompressionLevel should not be nil")
	} else if want, got = 9, *config.CompressionLevel; want != got {
		t.Errorf("field CompressionLevel: want: %v, got: %v", want, got)
	}
}

func TestLoadRecorderConfigInstPriorityOverURL(t *testing.T) {
	var (
		Name        = "InstPriorityOverURL"
		Description = "Instance match takes priority over URL match"
		yamlConfig  = `
recorders:
  - url: "http://example.com/api"
    scan_interval: 10s
  - inst: "http://example.com/api"
    url: "http://different.com/api"
    scan_interval: 20s
`
	)

	config, _, err := loadLmcrecConfig("test.yaml", "http://example.com/api", []byte(yamlConfig))
	if err != nil {
		t.Fatalf("%s: %s: unexpected error: %v", Name, Description, err)
	}

	var want, got interface{}

	if config.Inst == nil {
		t.Error("field Inst should not be nil")
	} else if want, got = "http://example.com/api", *config.Inst; want != got {
		t.Errorf("field Inst: want: %v, got: %v", want, got)
	}

	if config.URL == nil {
		t.Error("field URL should not be nil")
	} else if want, got = "http://different.com/api", *config.URL; want != got {
		t.Errorf("field URL: want: %v, got: %v", want, got)
	}

	if config.ScanInterval == nil {
		t.Error("field ScanInterval should not be nil")
	} else if want, got = 20*time.Second, *config.ScanInterval; want != got {
		t.Errorf("field ScanInterval: want: %v, got: %v", want, got)
	}
}

func TestLoadRecorderConfigCodecDefaults(t *testing.T) {
	var (
		Name        = "CodecDefaults"
		Description = "Verify codec-related defaults (BufSize, CompressionLevel) match expected values"
		yamlConfig  = `
recorders:
  - inst: "codec-test"
    url: "http://codec.com"
`
	)

	config, _, err := loadLmcrecConfig("test.yaml", "codec-test", []byte(yamlConfig))
	if err != nil {
		t.Fatalf("%s: %s: unexpected error: %v", Name, Description, err)
	}

	var want, got interface{}

	if config.BufSize == nil {
		t.Error("field BufSize should not be nil")
	} else if want, got = codec.USE_DEFAULT_BUFIO_SIZE, *config.BufSize; want != got {
		t.Errorf("field BufSize: want: %v, got: %v", want, got)
	}

	if config.CompressionLevel == nil {
		t.Error("field CompressionLevel should not be nil")
	} else if want, got = codec.DEFAULT_COMPRESSION_LEVEL, *config.CompressionLevel; want != got {
		t.Errorf("field CompressionLevel: want: %v, got: %v", want, got)
	}
}
