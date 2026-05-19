package service

import (
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"math"
	"net/http"
	"sync"
	"time"
)

type cachedRates struct {
	rates     map[string]float64
	updatedAt time.Time
	base      string
}

type ExchangeService struct {
	client    *http.Client
	cache     map[string]*cachedRates
	mu        sync.RWMutex
	cacheTTL  time.Duration
}

type RateItem struct {
	Code  string  `json:"code"`
	Rate  float64 `json:"rate"`
	Name  string  `json:"name"`
}

type ConvertResult struct {
	From   string  `json:"from"`
	To     string  `json:"to"`
	Amount float64 `json:"amount"`
	Result float64 `json:"result"`
	Rate   float64 `json:"rate"`
}

var currencyNames = map[string]string{
	"USD": "美元", "CNY": "人民币", "EUR": "欧元", "GBP": "英镑",
	"JPY": "日元", "KRW": "韩元", "HKD": "港币", "TWD": "台币",
	"AUD": "澳元", "CAD": "加元", "SGD": "新加坡元", "THB": "泰铢",
	"VND": "越南盾", "MYR": "林吉特", "PHP": "菲律宾比索", "IDR": "印尼盾",
	"INR": "印度卢比", "RUB": "卢布", "BRL": "巴西雷亚尔", "MXN": "墨西哥比索",
	"CHF": "瑞士法郎", "SEK": "瑞典克朗", "NOK": "挪威克朗", "DKK": "丹麦克朗",
	"NZD": "新西兰元", "TRY": "土耳其里拉", "ZAR": "南非兰特", "PLN": "波兰兹罗提",
	"ILS": "以色列新谢克尔", "AED": "阿联酋迪拉姆", "SAR": "沙特里亚尔",
}

func NewExchangeService() *ExchangeService {
	return &ExchangeService{
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
		cache:    make(map[string]*cachedRates),
		cacheTTL: 1 * time.Hour,
	}
}

func (s *ExchangeService) fetchRates(base string) (*cachedRates, error) {
	url := fmt.Sprintf("https://open.er-api.com/v6/latest/%s", base)

	resp, err := s.client.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch exchange rates: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("exchange rate API returned status %d: %s", resp.StatusCode, string(body))
	}

	var payload struct {
		Result       string             `json:"result"`
		BaseCode     string             `json:"base_code"`
		ConversionRates map[string]float64 `json:"rates"`
	}

	if err := json.Unmarshal(body, &payload); err != nil {
		return nil, fmt.Errorf("failed to parse exchange rate response: %w", err)
	}

	if payload.Result != "success" || payload.ConversionRates == nil {
		var altPayload struct {
			Result       string             `json:"result"`
			BaseCode     string             `json:"base_code"`
			ConversionRates map[string]float64 `json:"conversion_rates"`
		}
		if err := json.Unmarshal(body, &altPayload); err != nil {
			return nil, fmt.Errorf("failed to parse exchange rate response: %w", err)
		}
		payload.ConversionRates = altPayload.ConversionRates
		payload.BaseCode = altPayload.BaseCode
		payload.Result = altPayload.Result
	}

	if payload.Result != "success" {
		return nil, fmt.Errorf("exchange rate API returned error: %s", string(body))
	}

	if payload.ConversionRates == nil {
		return nil, fmt.Errorf("no rates in response")
	}

	payload.ConversionRates[payload.BaseCode] = 1.0

	return &cachedRates{
		rates:     payload.ConversionRates,
		updatedAt: time.Now(),
		base:      payload.BaseCode,
	}, nil
}

func (s *ExchangeService) getRates(base string) (*cachedRates, error) {
	if base == "" {
		base = "USD"
	}
	base = s.normalizeCurrency(base)

	s.mu.RLock()
	cached, ok := s.cache[base]
	s.mu.RUnlock()

	if ok && time.Since(cached.updatedAt) < s.cacheTTL {
		return cached, nil
	}

	rates, err := s.fetchRates(base)
	if err != nil {
		if ok {
			slog.Warn("failed to refresh exchange rates, using stale cache", "base", base, "error", err)
			return cached, nil
		}
		return nil, err
	}

	s.mu.Lock()
	s.cache[base] = rates
	s.mu.Unlock()

	return rates, nil
}

func (s *ExchangeService) normalizeCurrency(code string) string {
	switch code {
	case "RMB":
		return "CNY"
	case "NTD":
		return "TWD"
	default:
		return code
	}
}

func (s *ExchangeService) GetRate(from, to string) (float64, error) {
	from = s.normalizeCurrency(from)
	to = s.normalizeCurrency(to)

	cached, err := s.getRates(from)
	if err != nil {
		return 0, err
	}

	rate, ok := cached.rates[to]
	if !ok {
		return 0, fmt.Errorf("currency %s not supported", to)
	}

	return rate, nil
}

func (s *ExchangeService) Convert(from, to string, amount float64) (*ConvertResult, error) {
	rate, err := s.GetRate(from, to)
	if err != nil {
		return nil, err
	}

	result := math.Round(amount*rate*100) / 100

	return &ConvertResult{
		From:   from,
		To:     to,
		Amount: amount,
		Result: result,
		Rate:   math.Round(rate*10000) / 10000,
	}, nil
}

func (s *ExchangeService) GetAllRates(base string) ([]RateItem, error) {
	cached, err := s.getRates(base)
	if err != nil {
		return nil, err
	}

	items := make([]RateItem, 0, len(cached.rates))
	for code, rate := range cached.rates {
		name := currencyNames[code]
		if name == "" {
			name = code
		}
		items = append(items, RateItem{
			Code: code,
			Rate: math.Round(rate*10000) / 10000,
			Name: name,
		})
	}

	return items, nil
}

func (s *ExchangeService) GetSupportedCurrencies() []string {
	codes := make([]string, 0, len(currencyNames))
	for code := range currencyNames {
		codes = append(codes, code)
	}
	return codes
}
