package scheduler

import (
	"fmt"
	"log/slog"
	"sync"
	"time"

	"github.com/robfig/cron/v3"

	"github.com/erfengyuzhangsun/temutools/internal/repository"
	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

type TaskStatus string

const (
	StatusRegistered TaskStatus = "registered"
	StatusRunning    TaskStatus = "running"
	StatusStopped    TaskStatus = "stopped"
	StatusCompleted  TaskStatus = "completed"
	StatusFailed     TaskStatus = "failed"
)

type TaskInfo struct {
	TaskID         string
	Name           string
	CronExpression string
	TimeoutSeconds int
	MaxRetries     int
	Enabled        bool
	Description    string
	LastRunAt      *time.Time
	NextRunAt      *time.Time
	RunCount       int
	FailCount      int
	Status         TaskStatus
}

type Scheduler struct {
	cron    *cron.Cron
	tasks   map[string]*TaskInfo
	mu      sync.RWMutex
	started bool
}

func New() *Scheduler {
	return &Scheduler{
		cron:  cron.New(cron.WithSeconds()),
		tasks: make(map[string]*TaskInfo),
	}
}

func (s *Scheduler) RegisterTask(taskID, name, cronExpr, description string, timeoutSeconds, maxRetries int, enabled bool, callback func()) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.tasks[taskID]; exists {
		slog.Warn("task already registered", "task_id", taskID)
		return false
	}

	info := &TaskInfo{
		TaskID:         taskID,
		Name:           name,
		CronExpression: cronExpr,
		TimeoutSeconds: timeoutSeconds,
		MaxRetries:     maxRetries,
		Enabled:        enabled,
		Description:    description,
		Status:         StatusRegistered,
	}

	if enabled {
		entryID, err := s.cron.AddFunc(cronExpr, func() {
			s.executeTask(taskID, callback)
		})
		if err != nil {
			slog.Warn("failed to schedule task", "task_id", taskID, "error", err)
			return false
		}
		_ = entryID
		info.Status = StatusRegistered
	}

	s.tasks[taskID] = info
	repository.SaveSchedulerTask(taskID, name, cronExpr, timeoutSeconds, maxRetries, enabled, description)
	slog.Info("task registered", "task_id", taskID, "cron", cronExpr)
	return true
}

func (s *Scheduler) UnregisterTask(taskID string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, exists := s.tasks[taskID]; !exists {
		return false
	}
	delete(s.tasks, taskID)
	slog.Info("task unregistered", "task_id", taskID)
	return true
}

func (s *Scheduler) Start() {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.started {
		return
	}
	s.cron.Start()
	s.started = true
	slog.Info("scheduler started")
}

func (s *Scheduler) Stop() {
	s.mu.Lock()
	defer s.mu.Unlock()

	if !s.started {
		return
	}
	ctx := s.cron.Stop()
	<-ctx.Done()
	s.started = false
	slog.Info("scheduler stopped")
}

func (s *Scheduler) IsRunning() bool {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.started
}

func (s *Scheduler) GetTaskInfo(taskID string) *TaskInfo {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.tasks[taskID]
}

func (s *Scheduler) GetAllTasks() []*TaskInfo {
	s.mu.RLock()
	defer s.mu.RUnlock()

	result := make([]*TaskInfo, 0, len(s.tasks))
	for _, t := range s.tasks {
		result = append(result, t)
	}
	return result
}

func (s *Scheduler) RunTaskNow(taskID string) {
	s.mu.RLock()
	_, exists := s.tasks[taskID]
	s.mu.RUnlock()

	if !exists {
		slog.Warn("task not found for manual run", "task_id", taskID)
		return
	}

	slog.Info("manual task run", "task_id", taskID)
	s.executeTask(taskID, func() {})
}

func (s *Scheduler) executeTask(taskID string, callback func()) {
	start := time.Now()
	slog.Info("task executing", "task_id", taskID)

	func() {
		defer func() {
			if r := recover(); r != nil {
				slog.Error("task panic", "task_id", taskID, "recover", r)
				duration := time.Since(start).Seconds()
				repository.SaveSchedulerLog(taskID, string(StatusFailed), start, duration, fmt.Sprintf("panic: %v", r), 0)
			}
		}()
		callback()
	}()

	duration := time.Since(start).Seconds()
	repository.SaveSchedulerLog(taskID, string(StatusCompleted), start, duration, "", 0)
	slog.Info("task completed", "task_id", taskID, "duration", duration)
}

func forEachShop(fn func(shop repository.ShopWithCredentials)) {
	shops, err := repository.GetAllShopsWithCredentials()
	if err != nil {
		slog.Error("scheduler: failed to fetch shops", "error", err)
		return
	}
	for _, shop := range shops {
		fn(shop)
	}
}

func RegisterPresetTasks(s *Scheduler, userID int) {
	presets := []struct {
		id          string
		name        string
		cron        string
		desc        string
		callback    func()
	}{
		{
			id: "auto_sync_orders", name: "自动同步订单",
			cron: "0 0 */6 * * *", desc: "每6小时从 Temu API 同步所有店铺的最新订单数据",
			callback: func() {
				slog.Info("[定时任务] 开始自动同步订单")
				forEachShop(func(shop repository.ShopWithCredentials) {
					client := createClientForShop(shop, "")
					resp, err := client.GetOrders(1, 10, nil)
					if err != nil {
						slog.Warn("sync orders failed", "shop_id", shop.ShopID, "error", err)
						return
					}
					_ = resp
					slog.Info("shop orders synced", "shop_id", shop.ShopID, "shop", shop.ShopName)
					repository.SaveSyncRecord(shop.UserID, shop.ShopID, "order", 0, 0, 5*time.Second)
				})
			},
		},
		{
			id: "auto_process_pricing", name: "自动核价处理",
			cron: "0 0 */3 * * *", desc: "每3小时自动检查并处理所有店铺的核价通知",
			callback: func() {
				slog.Info("[定时任务] 开始自动核价处理")
				forEachShop(func(shop repository.ShopWithCredentials) {
					client := createClientForShop(shop, "")
					resp, err := client.GetPricingNotices(1, 20)
					if err != nil {
						slog.Warn("pricing check failed", "shop_id", shop.ShopID, "error", err)
						return
					}
					if resp.Success {
						slog.Info("pricing checked", "shop_id", shop.ShopID, "shop", shop.ShopName)
					}
				})
			},
		},
		{
			id: "auto_sync_inventory", name: "自动库存同步",
			cron: "0 0 */4 * * *", desc: "每4小时同步所有店铺的库存数据",
			callback: func() {
				slog.Info("[定时任务] 开始自动库存同步")
				forEachShop(func(shop repository.ShopWithCredentials) {
					client := createClientForShop(shop, "")
					resp, err := client.GetInventory(nil)
					if err != nil {
						slog.Warn("inventory sync failed", "shop_id", shop.ShopID, "error", err)
						return
					}
					_ = resp
					slog.Info("inventory synced", "shop_id", shop.ShopID, "shop", shop.ShopName)
					repository.SaveSyncRecord(shop.UserID, shop.ShopID, "inventory", 0, 0, 3*time.Second)
				})
			},
		},
		{
			id: "auto_risk_check", name: "自动风控体检",
			cron: "0 0 9 * * *", desc: "每天早上9点对所有店铺SKU进行风控合规检查",
			callback: func() {
				slog.Info("[定时任务] 开始自动风控体检")
				forEachShop(func(shop repository.ShopWithCredentials) {
					client := createClientForShop(shop, "")
					resp, err := client.GetComplianceGoodsList(1, 50)
					if err != nil {
						slog.Warn("risk check failed", "shop_id", shop.ShopID, "error", err)
						return
					}
					_ = resp
					slog.Info("risk check done", "shop_id", shop.ShopID, "shop", shop.ShopName)
				})
			},
		},
		{
			id: "auto_sync_reviews", name: "自动差评同步",
			cron: "0 0 */8 * * *", desc: "每8小时同步所有店铺的最新差评",
			callback: func() {
				slog.Info("[定时任务] 开始自动差评同步")
				forEachShop(func(shop repository.ShopWithCredentials) {
					client := createClientForShop(shop, "")
					resp, err := client.GetAftersalesList(1, 20)
					if err != nil {
						slog.Warn("reviews sync failed", "shop_id", shop.ShopID, "error", err)
						return
					}
					_ = resp
					slog.Info("reviews synced", "shop_id", shop.ShopID, "shop", shop.ShopName)
				})
			},
		},
	}

	for _, p := range presets {
		existing := s.GetTaskInfo(p.id)
		if existing != nil {
			continue
		}
		s.RegisterTask(p.id, p.name, p.cron, p.desc, 300, 2, true, p.callback)
	}
}

func createClientForShop(shop repository.ShopWithCredentials, apiKey string) temu.ApiClient {
	if shop.AccessToken == "" {
		return temu.NewMockClient(shop.ShopID)
	}
	region := shop.Region
	if region == "" {
		region = "us"
	}
	return temu.NewClient(shop.ShopID, apiKey, "", shop.AccessToken, region, "")
}
