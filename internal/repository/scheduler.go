package repository

import (
	"log/slog"
	"time"

	"github.com/erfengyuzhangsun/temutools/internal/models"
)

func SaveSchedulerTask(taskID, name, cronExpr string, timeoutSeconds, maxRetries int, enabled bool, description string) {
	db := GetDB()
	if db == nil {
		return
	}

	task := models.SchedulerTask{
		TaskID:         taskID,
		Name:           name,
		CronExpression: cronExpr,
		TimeoutSeconds: timeoutSeconds,
		MaxRetries:     maxRetries,
		Enabled:        enabled,
		Description:    description,
	}

	if err := db.Where("task_id = ?", taskID).Assign(task).FirstOrCreate(&task).Error; err != nil {
		slog.Warn("failed to save scheduler task", "error", err)
	}
}

func SaveSchedulerLog(taskID, status string, startedAt time.Time, durationSeconds float64, errorMsg string, retryCount int) {
	db := GetDB()
	if db == nil {
		return
	}

	finishedAt := startedAt.Add(time.Duration(durationSeconds * float64(time.Second)))
	log := models.SchedulerLog{
		TaskID:          taskID,
		Status:          status,
		StartedAt:       startedAt,
		FinishedAt:      &finishedAt,
		DurationSeconds: durationSeconds,
		ErrorMessage:    errorMsg,
		RetryCount:      retryCount,
	}

	if err := db.Create(&log).Error; err != nil {
		slog.Warn("failed to save scheduler log", "error", err)
	}
}

func QuerySchedulerTasks() ([]models.SchedulerTask, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	var tasks []models.SchedulerTask
	if err := db.Order("created_at DESC").Find(&tasks).Error; err != nil {
		return nil, err
	}
	return tasks, nil
}

func QuerySchedulerLogs(taskID string, limit int) ([]models.SchedulerLog, error) {
	db := GetDB()
	if db == nil {
		return nil, nil
	}

	var logs []models.SchedulerLog
	query := db.Order("started_at DESC").Limit(limit)
	if taskID != "" {
		query = query.Where("task_id = ?", taskID)
	}
	if err := query.Find(&logs).Error; err != nil {
		return nil, err
	}
	return logs, nil
}
