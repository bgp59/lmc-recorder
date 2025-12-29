// Generate record file out of samples created by scripts/snap-samples.sh

package recorder

import (
	"bufio"
	"fmt"
	"lmcrec/codec"
	"net/http"
	"os"
	"path"
	"sort"
	"strings"
	"sync"
	"time"
)

const (
	SAMPLE_RESPONSE_BODY_FILE_PREFIX    = "response-body"
	SAMPLE_RESPONSE_HEADERS_FILE_PREFIX = "response-headers"
	SAMPLE_RECORDER_FILE                = "samples.lmcrec"
	SAMPLE_RECORDER_INSTANCE            = "sampleLmcrec"
)

type SampleHttpClientDoer struct {
	response *http.Response
}

type SampleInfo struct {
	bodyFile    string
	headersFile string
	timestamp   time.Time
}

type SampleInfoSorter struct {
	infoList []*SampleInfo
}

func (s *SampleInfoSorter) Len() int {
	return len(s.infoList)
}

func (s *SampleInfoSorter) Swap(i, j int) {
	s.infoList[i], s.infoList[j] = s.infoList[j], s.infoList[i]
}

func (s *SampleInfoSorter) Less(i, j int) bool {
	return s.infoList[i].timestamp.Before(s.infoList[j].timestamp)
}

func sampleHttpClientDoer(sampleInfo *SampleInfo) (*SampleHttpClientDoer, error) {
	response := &http.Response{}
	header := http.Header{}

	file, err := os.Open(sampleInfo.headersFile)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	scanner, firstLine := bufio.NewScanner(file), true
	for scanner.Scan() {
		line := scanner.Text()
		if firstLine {
			proto, statusCode, status := "", -1, ""
			n, err := fmt.Sscanf(line, "%s %d %s", &proto, &statusCode, &status)
			if err != nil {
				return nil, err
			} else if n != 3 {
				return nil, fmt.Errorf("%s: not matching proto statusCode status", line)
			}
			response.Proto = proto
			response.StatusCode = statusCode
			response.Status = status
			firstLine = false
		} else {
			hdrVal := strings.SplitN(line, " ", 2)
			if len(hdrVal) == 2 {
				key, value := strings.TrimSpace(hdrVal[0]), strings.TrimSpace(hdrVal[1])
				key = strings.TrimSuffix(key, ":")
				header.Add(key, value)
			}
		}
	}
	if err = scanner.Err(); err != nil {
		return nil, err
	}

	response.Header = header
	response.Body, err = os.Open(sampleInfo.bodyFile)
	if err != nil {
		return nil, err
	}

	return &SampleHttpClientDoer{response}, nil
}

func (s *SampleHttpClientDoer) Do(req *http.Request) (*http.Response, error) {
	return s.response, nil
}

func buildSampleInfoList(sampleDir string, startSampleNum, endSampleNum int) ([]*SampleInfo, int, int, error) {
	dirEntries, err := os.ReadDir(sampleDir)
	if err != nil {
		return nil, 0, 0, err
	}

	sampleInfoList := make([]*SampleInfo, 0)
	minSampleNum, maxSampleNum := -1, -1
	wantRange := startSampleNum > 1 || endSampleNum > 0
	for _, dirEntry := range dirEntries {
		name := dirEntry.Name()
		if strings.HasPrefix(name, SAMPLE_RESPONSE_BODY_FILE_PREFIX) {
			keep := true
			if wantRange {
				index := strings.LastIndex(name, ".")
				if index >= 0 {
					sampleNum := -1
					if n, err := fmt.Sscanf(name[index+1:], "%d", &sampleNum); n == 1 && err == nil {
						keep = startSampleNum <= sampleNum && (endSampleNum <= 0 || sampleNum <= endSampleNum)
						if keep {
							if minSampleNum < 0 || sampleNum < minSampleNum {
								minSampleNum = sampleNum
							}
							if maxSampleNum < 0 || maxSampleNum < sampleNum {
								maxSampleNum = sampleNum
							}
						}
					}
				}
			}
			if !keep {
				continue
			}
			info, err := dirEntry.Info()
			if err != nil {
				return nil, 0, 0, err
			}
			headersFile := strings.Replace(
				name,
				SAMPLE_RESPONSE_BODY_FILE_PREFIX,
				SAMPLE_RESPONSE_HEADERS_FILE_PREFIX,
				1,
			)
			sampleInfoList = append(
				sampleInfoList,
				&SampleInfo{
					bodyFile:    path.Join(sampleDir, name),
					headersFile: path.Join(sampleDir, headersFile),
					timestamp:   info.ModTime(),
				},
			)
		}
	}

	sampleInfoListSorter := &SampleInfoSorter{sampleInfoList}
	sort.Sort(sampleInfoListSorter)
	return sampleInfoListSorter.infoList, minSampleNum, maxSampleNum, nil
}

func RecordSampleFiles(sampleDir string, startSampleNum, endSampleNum int) (string, error) {
	if startSampleNum > 0 && endSampleNum > 0 && endSampleNum < startSampleNum {
		return "", fmt.Errorf("startSampleNum: %d > %d endSampleNum", startSampleNum, endSampleNum)
	}

	sampleInfoList, minSampleNum, maxSampleNum, err := buildSampleInfoList(sampleDir, startSampleNum, endSampleNum)
	if err != nil {
		return "", err
	}

	sampleRecorderFile := path.Join(sampleDir, SAMPLE_RECORDER_FILE)
	if minSampleNum > 0 {
		sampleRecorderFile += fmt.Sprintf(".%d", minSampleNum)
	}
	if maxSampleNum > 0 && maxSampleNum > minSampleNum {
		sampleRecorderFile += fmt.Sprintf("-%d", maxSampleNum)
	}

	recorder := &Lmcrec{
		Inst:                SAMPLE_RECORDER_INSTANCE,
		flushInterval:       -1,    // no flush
		checkpointInterval:  0,     // disabled
		rolloverInterval:    0,     // disabled
		midnightRollover:    false, // disabled
		parseErrorThreshold: 1,     // to exit on 1st error
		recordFilesDir:      sampleDir,
		bufSize:             codec.USE_DEFAULT_BUFIO_SIZE,
		compressionLevel:    codec.DEFAULT_COMPRESSION_LEVEL,
		recordableParser:    NewRecordableLmcParser(),
		logger:              recorderLogger.WithField("inst", SAMPLE_RECORDER_INSTANCE),
		lck:                 &sync.Mutex{},
		newLmcrecFileEncoderFunc: func(fileName string, bufSize int, compressionLvl int, useCheckpoint bool, prevFileName string, version string) (codec.LmcrecFileEncoder, error) {
			// Override timestamp based filename:
			return codec.NewCodecLmcrecFileEncoder(
				sampleRecorderFile, bufSize, compressionLvl, useCheckpoint, prevFileName, version,
			)
		},
	}

	checkpointSampleIndx := -1
	if n := len(sampleInfoList); n >= 5 {
		checkpointSampleIndx = n / 2
	}
	for i, sampleInfo := range sampleInfoList {
		//recorder.logger.Infof("Processing %s", sampleInfo.bodyFile)
		if recorder.httpClient, err = sampleHttpClientDoer(sampleInfo); err != nil {
			return "", err
		}
		recorder.timeNowFunc = func() time.Time { return sampleInfo.timestamp }

		if i == checkpointSampleIndx {
			recorder.logger.Infof("Force checkpoint at sample# %d, file %s", i+1, sampleInfo.bodyFile)
			recorder.checkpointInterval = 1 * time.Second
			recorder.lastCheckpointTs = sampleInfo.timestamp.Add(-2 * recorder.checkpointInterval)
		} else {
			recorder.checkpointInterval = 0
		}

		if !recorder.Scan() {
			return "", fmt.Errorf("failed scan")
		}
	}

	encoder := recorder.encoder
	if encoder == nil {
		return "", fmt.Errorf("unexpected nil encoder")
	}
	if err = encoder.Close(); err != nil {
		return "", err
	}
	return encoder.GetFileName(), nil
}
