package service

import (
	"encoding/json"
	"fmt"
)

func parseJSON(data json.RawMessage, target interface{}) error {
	if len(data) == 0 {
		return fmt.Errorf("empty json data")
	}
	return json.Unmarshal(data, target)
}
