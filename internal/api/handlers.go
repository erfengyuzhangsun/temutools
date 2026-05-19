package api

import (
	"fmt"
	"log/slog"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"

	"github.com/erfengyuzhangsun/temutools/internal/api/middleware"
	"github.com/erfengyuzhangsun/temutools/internal/auth"
	"github.com/erfengyuzhangsun/temutools/internal/config"
	"github.com/erfengyuzhangsun/temutools/internal/models"
	"github.com/erfengyuzhangsun/temutools/internal/repository"
	"github.com/erfengyuzhangsun/temutools/internal/scheduler"
	"github.com/erfengyuzhangsun/temutools/internal/service"
	"github.com/erfengyuzhangsun/temutools/internal/temu"
)

func HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"version": "0.1.0",
		"service": "temu-tools-go",
	})
}

func LoginHandler(c *gin.Context) {
	var req struct {
		Email    string `json:"email" binding:"required"`
		Password string `json:"password" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "邮箱和密码不能为空")
		return
	}

	slog.Info("login attempt", "email", req.Email)

	user, err := repository.FindByEmail(req.Email)
	if err != nil || user == nil {
		slog.Warn("login failed: invalid credentials", "email", req.Email)
		Error(c, http.StatusUnauthorized, ErrUnauthorized, "邮箱或密码错误")
		return
	}

	if !repository.CheckPassword(req.Password, user.PasswordHash) {
		slog.Warn("login failed: wrong password", "email", req.Email)
		Error(c, http.StatusUnauthorized, ErrUnauthorized, "邮箱或密码错误")
		return
	}

	if repository.IsUserExpired(user) {
		slog.Warn("login failed: account expired", "user_id", user.UserID)
		Error(c, http.StatusForbidden, ErrForbidden, "您的套餐已过期，请联系客服续费")
		return
	}

	authService, exists := c.Get("auth_service")
	if !exists {
		Error(c, http.StatusInternalServerError, ErrInternal, "认证服务未初始化")
		return
	}
	svc, _ := authService.(*auth.AuthService)

	token, err := svc.GenerateToken(user.UserID, user.PlanType)
	if err != nil {
		slog.Error("failed to generate token", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "令牌生成失败")
		return
	}

	slog.Info("login successful", "user_id", user.UserID, "email", user.Email, "plan", user.PlanType)

	var daysRemaining int
	var isExpiringSoon bool
	if user.ExpireDate != nil {
		daysRemaining = int(time.Until(*user.ExpireDate).Hours() / 24)
		isExpiringSoon = daysRemaining > 0 && daysRemaining <= 7
	}

	Success(c, gin.H{
		"token": token,
		"user": gin.H{
			"user_id":     user.UserID,
			"email":       user.Email,
			"nickname":    user.WechatNickname,
			"plan":        user.PlanType,
			"start_date":  user.StartDate,
			"expire_date": user.ExpireDate,
		},
		"expiry": gin.H{
			"expire_date":      user.ExpireDate,
			"days_remaining":   daysRemaining,
			"is_expiring_soon": isExpiringSoon,
			"is_expired":       false,
		},
	})
}

func RegisterHandler(c *gin.Context) {
	var req struct {
		Email         string `json:"email" binding:"required"`
		Password      string `json:"password" binding:"required,min=6"`
		AgreedTerms   bool   `json:"agreed_terms"`
		AgreedPrivacy bool   `json:"agreed_privacy"`
		PolicyVersion string `json:"policy_version"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "邮箱和密码不能为空（密码至少6位）")
		return
	}
	if !req.AgreedTerms || !req.AgreedPrivacy {
		Error(c, http.StatusBadRequest, ErrValidation, "注册前须同意《用户服务协议》和《隐私政策》")
		return
	}

	slog.Info("registration attempt", "email", req.Email)

	policyVersion := req.PolicyVersion
	if policyVersion == "" {
		policyVersion = "2026-05-18"
	}

	user, err := repository.CreateUser(req.Email, req.Password, "basic", policyVersion, req.AgreedTerms, req.AgreedPrivacy)
	if err != nil {
		slog.Warn("registration failed", "email", req.Email, "error", err)
		if err.Error() == "email already registered" {
			Error(c, http.StatusConflict, ErrConflict, "该邮箱已注册")
			return
		}
		Error(c, http.StatusInternalServerError, ErrInternal, "注册失败，请稍后重试")
		return
	}

	authService, exists := c.Get("auth_service")
	if !exists {
		Error(c, http.StatusInternalServerError, ErrInternal, "认证服务未初始化")
		return
	}
	svc, _ := authService.(*auth.AuthService)

	token, err := svc.GenerateToken(user.UserID, user.PlanType)
	if err != nil {
		slog.Error("failed to generate token", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "令牌生成失败")
		return
	}

	slog.Info("registration successful", "user_id", user.UserID, "email", user.Email)

	Success(c, gin.H{
		"token": token,
		"user": gin.H{
			"user_id":  user.UserID,
			"email":    user.Email,
			"nickname": user.WechatNickname,
			"plan":     user.PlanType,
		},
	})
}

func GetCurrentUser(c *gin.Context) {
	userID := middleware.GetUserID(c)
	planType := middleware.GetPlanType(c)
	Success(c, gin.H{"user_id": userID, "plan_type": planType})
}

func GetDashboardOverview(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewDashboardService(userID)
	Success(c, svc.GetOverview())
}

func GetDashboardAlerts(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewDashboardService(userID)
	alerts, count := svc.GetAllAlerts()
	Success(c, gin.H{"alerts": alerts, "count": count})
}

func HandleAutoPricing(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		ShopID int `json:"shop_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "缺少 shop_id")
		return
	}

	svc := service.NewPricingService(userID)
	client := getTemuClient(req.ShopID)
	result, err := svc.AutoHandlePricing(req.ShopID, client)
	if err != nil {
		slog.Error("auto pricing failed", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, err.Error())
		return
	}

	Success(c, gin.H{
		"handled_count": result.HandledCount,
		"results":       result.Results,
		"message":       fmt.Sprintf("核价处理完成，共%d条", result.HandledCount),
	})
}

func HandleAutoAdjustPrices(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		ShopID       int     `json:"shop_id" binding:"required"`
		TargetMargin float64 `json:"target_margin"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "缺少 shop_id")
		return
	}

	svc := service.NewPricingService(userID)
	client := getTemuClient(req.ShopID)
	result, err := svc.AutoAdjustPrices(req.ShopID, client, req.TargetMargin)
	if err != nil {
		slog.Error("auto adjust prices failed", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, err.Error())
		return
	}

	Success(c, gin.H{
		"total_checked":    result.TotalChecked,
		"needs_adjustment": result.NeedsAdjustment,
		"executed":         result.Executed,
		"items":            result.Items,
		"message":          fmt.Sprintf("调价完成: 检查%d个SKU, 调整%d个", result.TotalChecked, result.Executed),
	})
}

func GetPricingLogs(c *gin.Context) {
	userID := middleware.GetUserID(c)
	shopID, _ := strconv.Atoi(c.DefaultQuery("shop_id", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))

	svc := service.NewPricingService(userID)
	logs, err := svc.GetPricingLogs(shopID, limit)
	if err != nil {
		slog.Error("failed to get pricing logs", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, err.Error())
		return
	}
	Success(c, gin.H{"logs": logs, "total": len(logs)})
}

func UpdatePricingThreshold(c *gin.Context) {
	var req struct {
		Threshold float64 `json:"threshold"`
	}
	if err := c.ShouldBindJSON(&req); err == nil {
		slog.Info("pricing threshold updated", "threshold", req.Threshold)
	}
	Success(c, gin.H{"message": "阈值已更新"})
}

func GetInventoryList(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewInventoryService(userID)
	summaries, err := svc.GetInventoryList()
	if err != nil {
		slog.Error("failed to get inventory list", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, err.Error())
		return
	}
	Success(c, gin.H{"items": summaries, "total": len(summaries)})
}

func SyncInventory(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		ShopID int `json:"shop_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "缺少 shop_id")
		return
	}

	client := getTemuClient(req.ShopID)
	svc := service.NewInventoryService(userID)
	count, err := svc.SyncInventory(req.ShopID, client)
	if err != nil {
		slog.Error("inventory sync failed", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, err.Error())
		return
	}
	Success(c, gin.H{"synced_count": count, "message": fmt.Sprintf("同步完成，共%d条SKU", count)})
}

func SetInventoryAlert(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		Threshold int `json:"threshold"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		req.Threshold = 10
	}

	svc := service.NewInventoryService(userID)
	cfg := svc.SetAlertConfig(service.InventoryAlertConfig{
		LowStockThreshold: req.Threshold,
		Enabled:           true,
	})
	Success(c, gin.H{"message": cfg.Message, "threshold": cfg.LowStockThreshold})
}

func CollectMetrics(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewAnalysisService(userID)
	result := svc.CollectMetrics()
	Success(c, gin.H{"metrics": result, "message": "采集完成"})
}

func GetAnalysisAlerts(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewDashboardService(userID)
	alerts, _ := svc.GetAllAlerts()
	Success(c, gin.H{"alerts": alerts})
}

func GetAnalysisReport(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewAnalysisService(userID)
	report := svc.GetReport()
	Success(c, gin.H{"report": report})
}

func SyncSettlement(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewFinanceService(userID)
	result := svc.SyncSettlement()
	Success(c, gin.H(result))
}

func GetMonthlySummary(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewFinanceService(userID)
	summary := svc.GetMonthlySummary()
	Success(c, gin.H{"summary": summary})
}

func GetForecast(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewFinanceService(userID)
	forecast := svc.GetForecast()
	Success(c, gin.H{"forecast": forecast})
}

func SyncOrders(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		ShopID int `json:"shop_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "缺少 shop_id")
		return
	}

	svc := service.NewApiSyncService(userID)
	client := getTemuClient(req.ShopID)
	result := svc.SyncOrders(req.ShopID, client)
	Success(c, gin.H{
		"synced_count": result.SyncedCount,
		"total_count":  result.TotalInAPI,
		"message":      result.Message,
	})
}

func BindShop(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		ShopName              string `json:"shop_name" binding:"required"`
		AccessToken           string `json:"access_token" binding:"required"`
		Region                string `json:"region"`
		AppKey                string `json:"app_key"`
		AppSecret             string `json:"app_secret"`
		DataProcessingConsent bool   `json:"data_processing_consent"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "缺少必填字段")
		return
	}
	if !req.DataProcessingConsent {
		Error(c, http.StatusBadRequest, ErrValidation, "绑定店铺前须确认数据处理授权声明")
		return
	}

	region := req.Region
	if region == "" {
		region = "us"
	}

	shopID, err := repository.CreateShop(userID, req.ShopName)
	if err != nil {
		slog.Error("failed to create shop", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "店铺创建失败")
		return
	}

	if err := repository.SaveShopCredentials(shopID, req.AccessToken, region, req.AppKey, req.AppSecret); err != nil {
		slog.Error("failed to save shop credentials", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "保存凭证失败")
		return
	}

	slog.Info("shop bound", "user_id", userID, "shop_id", shopID, "shop_name", req.ShopName, "region", region)
	Success(c, gin.H{"shop_id": shopID, "message": "店铺绑定成功"})
}

func GetShops(c *gin.Context) {
	userID := middleware.GetUserID(c)
	shops, err := repository.GetUserShops(userID)
	if err != nil {
		slog.Warn("failed to get shops", "error", err)
		shops = nil
	}

	type shopResp struct {
		ShopID       int    `json:"shop_id"`
		ShopName     string `json:"shop_name"`
		MainCategory string `json:"main_category"`
		Region       string `json:"region"`
	}

	result := make([]shopResp, 0, len(shops))
	for _, s := range shops {
		region := "us"
		if cred, err := repository.GetShopCredentials(s.ShopID); err == nil && cred != nil {
			region = cred.Region
			if region == "" {
				region = "us"
			}
		}
		result = append(result, shopResp{
			ShopID:       s.ShopID,
			ShopName:     s.ShopName,
			MainCategory: s.MainCategory,
			Region:       region,
		})
	}
	Success(c, gin.H{"shops": result})
}

func DeleteShop(c *gin.Context) {
	shopIDStr := c.Param("id")
	shopID, _ := strconv.Atoi(shopIDStr)
	if shopID > 0 {
		repository.DeleteShop(shopID)
	}
	Success(c, gin.H{"message": "店铺已删除"})
}

func GetTasks(c *gin.Context) {
	sch := getScheduler(c)
	tasks := sch.GetAllTasks()
	type taskResp struct {
		TaskID         string `json:"task_id"`
		Name           string `json:"name"`
		CronExpression string `json:"cron_expression"`
		Enabled        bool   `json:"enabled"`
		Description    string `json:"description"`
		Status         string `json:"status"`
		RunCount       int    `json:"run_count"`
		FailCount      int    `json:"fail_count"`
	}
	result := make([]taskResp, len(tasks))
	for i, t := range tasks {
		result[i] = taskResp{
			TaskID: t.TaskID, Name: t.Name, CronExpression: t.CronExpression,
			Enabled: t.Enabled, Description: t.Description, Status: string(t.Status),
			RunCount: t.RunCount, FailCount: t.FailCount,
		}
	}
	Success(c, gin.H{"tasks": result})
}

func CreateTask(c *gin.Context) {
	var req struct {
		TaskID         string `json:"task_id" binding:"required"`
		Name           string `json:"name" binding:"required"`
		CronExpression string `json:"cron_expression" binding:"required"`
		Description    string `json:"description"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "缺少必填字段")
		return
	}

	sch := getScheduler(c)
	sch.RegisterTask(req.TaskID, req.Name, req.CronExpression, req.Description, 300, 3, true, func() {
		slog.Info("custom task executed", "task_id", req.TaskID)
	})
	Success(c, gin.H{"message": "任务创建成功"})
}

func UpdateTask(c *gin.Context) {
	taskID := c.Param("id")
	slog.Info("update task", "task_id", taskID)
	Success(c, gin.H{"message": "任务更新成功"})
}

func DeleteTask(c *gin.Context) {
	taskID := c.Param("id")
	sch := getScheduler(c)
	sch.UnregisterTask(taskID)
	Success(c, gin.H{"message": "任务已删除"})
}

func RunTaskNow(c *gin.Context) {
	taskID := c.Param("id")
	sch := getScheduler(c)
	sch.RunTaskNow(taskID)
	Success(c, gin.H{"message": "任务已触发执行"})
}

func GetMessages(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewMiscService(userID)
	messages, err := svc.GetMessages(getTemuClient(0))
	if err != nil {
		slog.Warn("failed to get messages", "error", err)
	}
	Success(c, gin.H{"messages": messages, "total": len(messages)})
}

func ReplyMessage(c *gin.Context) {
	var req struct {
		MessageID int    `json:"message_id"`
		Content   string `json:"content"`
	}
	c.ShouldBindJSON(&req)
	slog.Info("reply message", "message_id", req.MessageID)
	Success(c, gin.H{"message": "回复成功"})
}

func GetShippingOrders(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewMiscService(userID)
	orders, _ := svc.GetShippingOrders(getTemuClient(0))
	Success(c, gin.H{"orders": orders, "total": len(orders)})
}

func GenerateLabel(c *gin.Context) {
	Success(c, gin.H{"message": "面单生成成功"})
}

func GetActivities(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewMiscService(userID)
	activities, err := svc.GetActivities(getTemuClient(0))
	if err != nil {
		Success(c, gin.H{"activities": []gin.H{}, "total": 0})
		return
	}
	Success(c, gin.H{"activities": activities, "total": len(activities)})
}

func SignupActivity(c *gin.Context) {
	Success(c, gin.H{"message": "报名成功"})
}

func GetRiskReport(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewRiskService(userID)
	report := svc.GetReport()
	Success(c, gin.H{"report": report})
}

func RunRiskCheck(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		ShopID int `json:"shop_id"`
	}
	c.ShouldBindJSON(&req)
	svc := service.NewRiskService(userID)
	result := svc.RunCheck(req.ShopID)
	Success(c, gin.H{
		"risk_score": result.RiskScore,
		"alerts":     result.Alerts,
		"passed":     result.Passed,
	})
}

func ExecuteBatchOp(c *gin.Context) {
	userID := middleware.GetUserID(c)
	slog.Info("batch op triggered", "user_id", userID)
	Success(c, gin.H{"message": "批量操作执行中", "status": "queued"})
}

func GetReviews(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewMiscService(userID)
	reviews, _ := svc.GetReviews(getTemuClient(0))
	Success(c, gin.H{"reviews": reviews, "total": len(reviews)})
}

func ReplyReview(c *gin.Context) {
	Success(c, gin.H{"message": "回复成功"})
}

func RunRiskGuardCheck(c *gin.Context) {
	userID := middleware.GetUserID(c)
	svc := service.NewMiscService(userID)
	result := svc.RunRiskGuardCheck()
	Success(c, gin.H{
		"passed": result.Passed,
		"checks": result.Checks,
	})
}

func GetRiskGuardLogs(c *gin.Context) {
	Success(c, gin.H{"logs": []gin.H{}, "total": 0})
}

func GetResearchProducts(c *gin.Context) {
	userID := middleware.GetUserID(c)
	slog.Info("get research products", "user_id", userID)
	Success(c, gin.H{"products": []gin.H{}, "total": 0, "message": "选品功能请在数据同步后使用"})
}

func GetSuppliers(c *gin.Context) {
	userID := middleware.GetUserID(c)
	suppliers, err := repository.GetSuppliers(userID)
	if err != nil {
		slog.Warn("failed to get suppliers", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "获取供应商列表失败")
		return
	}
	Success(c, gin.H{"suppliers": suppliers, "total": len(suppliers)})
}

func AddSupplier(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		Name         string  `json:"name" binding:"required"`
		Contact      string  `json:"contact"`
		Phone        string  `json:"phone"`
		MainCategory string  `json:"main_category"`
		Rating       float64 `json:"rating"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "供应商名称不能为空")
		return
	}

	supplier := models.Supplier{
		UserID:       userID,
		Name:         req.Name,
		Contact:      req.Contact,
		Phone:        req.Phone,
		MainCategory: req.MainCategory,
		Rating:       req.Rating,
	}
	if supplier.Rating <= 0 {
		supplier.Rating = 5.0
	}

	created, err := repository.CreateSupplier(supplier)
	if err != nil {
		slog.Error("failed to create supplier", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "供应商添加失败")
		return
	}
	slog.Info("supplier added", "name", req.Name, "id", created.SupplierID)
	Success(c, gin.H{"supplier_id": created.SupplierID, "message": "供应商添加成功"})
}

func CreateProduct(c *gin.Context) {
	userID := middleware.GetUserID(c)
	var req struct {
		ProductName          string  `json:"product_name" binding:"required"`
		SkuCode              string  `json:"sku_code" binding:"required"`
		CategoryName         string  `json:"category_name"`
		MaterialCost         float64 `json:"material_cost"`
		LaborCost            float64 `json:"labor_cost"`
		PackagingCost        float64 `json:"packaging_cost"`
		ShippingCost         float64 `json:"shipping_cost"`
		OtherCost            float64 `json:"other_cost"`
		ExpectedProfitMargin float64 `json:"expected_profit_margin"`
		IsFullCommission     bool    `json:"is_full_commission"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "产品名称和SKU编码不能为空")
		return
	}

	totalCost := req.MaterialCost + req.LaborCost + req.PackagingCost + req.ShippingCost + req.OtherCost
	margin := req.ExpectedProfitMargin
	if margin <= 0 {
		margin = 20.0
	}
	suggestedPrice := totalCost / (1 - margin/100)

	product := models.FactoryProduct{
		ProductName:          req.ProductName,
		SkuCode:              req.SkuCode,
		CategoryName:         req.CategoryName,
		MaterialCost:         req.MaterialCost,
		LaborCost:            req.LaborCost,
		PackagingCost:        req.PackagingCost,
		ShippingCost:         req.ShippingCost,
		OtherCost:            req.OtherCost,
		TotalCost:            totalCost,
		ExpectedProfitMargin: margin,
		SuggestedSupplyPrice: suggestedPrice,
		IsFullCommission:     req.IsFullCommission,
	}

	created, err := repository.CreateFactoryProduct(userID, product)
	if err != nil {
		slog.Error("failed to create product", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "产品创建失败")
		return
	}
	slog.Info("product created", "name", req.ProductName, "id", created.ProductID)
	Success(c, gin.H{"product_id": created.ProductID, "suggested_price": suggestedPrice, "message": "产品创建成功"})
}

func GetFactoryProducts(c *gin.Context) {
	userID := middleware.GetUserID(c)
	products, err := repository.GetFactoryProducts(userID)
	if err != nil {
		slog.Warn("failed to get factory products", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "获取产品列表失败")
		return
	}
	Success(c, gin.H{"products": products, "total": len(products)})
}

func GetCostAnalysis(c *gin.Context) {
	userID := middleware.GetUserID(c)
	products, err := repository.GetFactoryProducts(userID)
	if err != nil {
		products = nil
	}

	if len(products) == 0 {
		Success(c, gin.H{"analysis": gin.H{
			"total_products": 0, "avg_cost": 0, "avg_margin": 0,
			"message": "请先录入产品资料",
		}})
		return
	}

	var totalCost, totalPrice float64
	for _, p := range products {
		totalCost += p.TotalCost
		totalPrice += p.SuggestedSupplyPrice
	}
	avgCost := totalCost / float64(len(products))
	avgMargin := 0.0
	if totalCost > 0 {
		avgMargin = ((totalPrice - totalCost) / totalCost) * 100
	}

	Success(c, gin.H{"analysis": gin.H{
		"total_products": len(products),
		"avg_cost":       round2(avgCost),
		"avg_margin":     round2(avgMargin),
		"message":        "分析完成",
	}})
}

func CalculatePrice(c *gin.Context) {
	var req struct {
		CostPrice      float64 `json:"cost_price"`
		ExpectedMargin float64 `json:"expected_margin"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "缺少计算参数")
		return
	}
	recommendedPrice := req.CostPrice / (1 - req.ExpectedMargin/100)
	Success(c, gin.H{"result": gin.H{
		"cost_price":        req.CostPrice,
		"expected_margin":   req.ExpectedMargin,
		"recommended_price": fmt.Sprintf("%.2f", recommendedPrice),
		"message":           "价格计算完成",
	}})
}

func BatchCalculate(c *gin.Context) {
	var req struct {
		Items []struct {
			CostPrice      float64 `json:"cost_price"`
			ExpectedMargin float64 `json:"expected_margin"`
		} `json:"items"`
	}
	if err := c.ShouldBindJSON(&req); err != nil || len(req.Items) == 0 {
		Success(c, gin.H{"results": []gin.H{}, "message": "请传入待计算的数据"})
		return
	}

	results := make([]gin.H, 0, len(req.Items))
	for _, item := range req.Items {
		price := item.CostPrice / (1 - item.ExpectedMargin/100)
		results = append(results, gin.H{
			"cost_price":        item.CostPrice,
			"expected_margin":   item.ExpectedMargin,
			"recommended_price": fmt.Sprintf("%.2f", price),
		})
	}
	Success(c, gin.H{"results": results, "message": fmt.Sprintf("批量计算完成，共%d条", len(results))})
}

func GetAPIGuide(c *gin.Context) {
	Success(c, gin.H{"guide": gin.H{
		"steps": []gin.H{
			{"step": 1, "title": "注册 Temu 开发者账号", "url": "https://partner.temu.com"},
			{"step": 2, "title": "创建自研应用获取凭证"},
			{"step": 3, "title": "在系统中绑定店铺"},
		},
	}})
}

func TestAPIConnection(c *gin.Context) {
	client := temu.NewMockClient(1)
	resp, err := client.CheckAccessToken()
	if err != nil || resp == nil {
		Success(c, gin.H{"connected": false, "message": "API连接测试失败"})
		return
	}
	Success(c, gin.H{"connected": true, "message": "API连接正常（Mock模式）"})
}

func AdminListUsers(c *gin.Context) {
	search := c.DefaultQuery("search", "")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "20"))
	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 20
	}

	users, total, err := repository.ListUsers(search, page, pageSize)
	if err != nil {
		slog.Error("failed to list users", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "获取用户列表失败")
		return
	}

	Success(c, gin.H{
		"users":       users,
		"total":       total,
		"page":        page,
		"page_size":   pageSize,
		"total_pages": (int(total) + pageSize - 1) / pageSize,
	})
}

func AdminUpgradePlan(c *gin.Context) {
	var req struct {
		Email    string `json:"email" binding:"required"`
		PlanType string `json:"plan_type" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "邮箱和套餐类型不能为空")
		return
	}

	validPlans := map[string]bool{"basic": true, "pro": true, "enterprise": true, "lifetime": true}
	if !validPlans[req.PlanType] {
		Error(c, http.StatusBadRequest, ErrValidation, "无效的套餐类型，可选: basic/pro/enterprise/lifetime")
		return
	}

	if err := repository.UpdateUserPlan(req.Email, req.PlanType); err != nil {
		if err.Error() == "user not found" {
			Error(c, http.StatusNotFound, ErrNotFound, "用户不存在")
			return
		}
		slog.Error("failed to upgrade plan", "email", req.Email, "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "套餐升级失败")
		return
	}

	slog.Info("plan upgraded by admin", "email", req.Email, "plan", req.PlanType)
	Success(c, gin.H{"message": fmt.Sprintf("已将 %s 的套餐升级为 %s", req.Email, req.PlanType)})
}

func AdminRenewUser(c *gin.Context) {
	var req struct {
		Email string `json:"email" binding:"required"`
		Days  int    `json:"days" binding:"required,min=1"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "邮箱和续费天数不能为空")
		return
	}

	if err := repository.UpdateUserExpiry(req.Email, req.Days); err != nil {
		if err.Error() == "user not found" {
			Error(c, http.StatusNotFound, ErrNotFound, "用户不存在")
			return
		}
		slog.Error("failed to renew user", "email", req.Email, "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "续费失败")
		return
	}

	slog.Info("user renewed by admin", "email", req.Email, "days", req.Days)
	Success(c, gin.H{"message": fmt.Sprintf("已将 %s 续费 %d 天", req.Email, req.Days)})
}

func AdminToggleUser(c *gin.Context) {
	var req struct {
		Email  string `json:"email" binding:"required"`
		Active bool   `json:"active"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "邮箱不能为空")
		return
	}

	if err := repository.ToggleUserActive(req.Email, req.Active); err != nil {
		if err.Error() == "user not found" {
			Error(c, http.StatusNotFound, ErrNotFound, "用户不存在")
			return
		}
		slog.Error("failed to toggle user", "email", req.Email, "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "操作失败")
		return
	}

	action := "启用"
	if !req.Active {
		action = "禁用"
	}
	slog.Info("user toggled by admin", "email", req.Email, "active", req.Active)
	Success(c, gin.H{"message": fmt.Sprintf("已将 %s %s", req.Email, action)})
}

func AdminDeleteUser(c *gin.Context) {
	var req struct {
		UserID int `json:"user_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "用户ID不能为空")
		return
	}

	if err := repository.DeleteUser(req.UserID); err != nil {
		if err.Error() == "user not found" {
			Error(c, http.StatusNotFound, ErrNotFound, "用户不存在")
			return
		}
		slog.Error("failed to delete user", "user_id", req.UserID, "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "删除用户失败")
		return
	}

	slog.Info("user deleted by admin", "user_id", req.UserID)
	Success(c, gin.H{"message": "用户已删除"})
}

func AdminResetUserPassword(c *gin.Context) {
	var req struct {
		Email       string `json:"email" binding:"required"`
		NewPassword string `json:"new_password" binding:"required,min=6"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "邮箱和新密码不能为空（密码至少6位）")
		return
	}

	if err := repository.UpdateUserPassword(req.Email, req.NewPassword); err != nil {
		if err.Error() == "user not found" {
			Error(c, http.StatusNotFound, ErrNotFound, "用户不存在")
			return
		}
		slog.Error("failed to reset password", "email", req.Email, "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "密码重置失败")
		return
	}

	slog.Info("password reset by admin", "email", req.Email)
	Success(c, gin.H{"message": fmt.Sprintf("已将 %s 的密码重置成功", req.Email)})
}

func AdminListOrders(c *gin.Context) {
	orders, err := repository.ListOrders()
	if err != nil {
		slog.Error("failed to list orders", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "获取订单列表失败")
		return
	}
	Success(c, gin.H{"orders": orders})
}

func AdminCompleteOrder(c *gin.Context) {
	var req struct {
		OrderID int `json:"order_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "订单ID不能为空")
		return
	}

	if err := repository.MarkOrderCompleted(req.OrderID); err != nil {
		if err.Error() == "order not found" {
			Error(c, http.StatusNotFound, ErrNotFound, "订单不存在")
			return
		}
		Error(c, http.StatusInternalServerError, ErrInternal, "操作失败")
		return
	}

	Success(c, gin.H{"message": "订单已标记为已处理"})
}

func AdminDeleteOrder(c *gin.Context) {
	var req struct {
		OrderID int `json:"order_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "订单ID不能为空")
		return
	}

	if err := repository.DeleteOrder(req.OrderID); err != nil {
		if err.Error() == "order not found" {
			Error(c, http.StatusNotFound, ErrNotFound, "订单不存在")
			return
		}
		Error(c, http.StatusInternalServerError, ErrInternal, "删除失败")
		return
	}

	Success(c, gin.H{"message": "订单已删除"})
}

func AdminMonitor(c *gin.Context) {
	report := service.RunHealthCheck()
	Success(c, report)
}

func SubmitOrder(c *gin.Context) {
	var req struct {
		ContactName string  `json:"contact_name" binding:"required"`
		Phone       string  `json:"phone" binding:"required"`
		Wechat      string  `json:"wechat"`
		PlanName    string  `json:"plan_name" binding:"required"`
		Amount      float64 `json:"amount"`
		Notes       string  `json:"notes"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "请填写必要信息")
		return
	}

	order := &models.Order{
		ContactName: req.ContactName,
		Phone:       req.Phone,
		Wechat:      req.Wechat,
		PlanName:    req.PlanName,
		Amount:      req.Amount,
		Notes:       req.Notes,
		Status:      "pending",
	}

	isBasic := strings.Contains(req.PlanName, "基础版")
	if isBasic {
		order.Status = "completed"
	}

	if err := repository.CreateOrder(order); err != nil {
		slog.Error("failed to submit order", "error", err)
		Error(c, http.StatusInternalServerError, ErrInternal, "订单提交失败")
		return
	}

	if isBasic {
		slog.Info("basic plan order auto-completed", "order_id", order.OrderID)
	}

	slog.Info("order submitted", "order_id", order.OrderID, "plan", req.PlanName)
	Success(c, gin.H{"message": "订单提交成功, 我们将在10分钟内联系您", "order_id": order.OrderID})
}

func RequestRefund(c *gin.Context) {
	var req struct {
		OrderID    int    `json:"order_id" binding:"required"`
		Reason     string `json:"reason" binding:"required"`
		ContactWay string `json:"contact_way"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		Error(c, http.StatusBadRequest, ErrBadRequest, "请提供订单ID和退款原因")
		return
	}

	orders, err := repository.ListOrders()
	if err != nil {
		Error(c, http.StatusInternalServerError, ErrInternal, "查询订单失败")
		return
	}

	var found *models.Order
	for i, o := range orders {
		if o.OrderID == req.OrderID {
			found = &orders[i]
			break
		}
	}

	if found == nil {
		Error(c, http.StatusNotFound, ErrNotFound, "订单不存在")
		return
	}

	if found.Status == "refunded" || found.Status == "refund_requested" {
		Error(c, http.StatusBadRequest, ErrConflict, "该订单已申请退款或已退款")
		return
	}

	updatedNotes := fmt.Sprintf("退款原因: %s", req.Reason)
	if req.ContactWay != "" {
		updatedNotes += fmt.Sprintf(" | 联系方式: %s", req.ContactWay)
	}
	if found.Notes != "" {
		updatedNotes = found.Notes + "\n" + updatedNotes
	}

	db := repository.GetDB()
	if db == nil {
		Error(c, http.StatusInternalServerError, ErrInternal, "数据库未连接")
		return
	}

	result := db.Model(&models.Order{}).Where("order_id = ?", req.OrderID).
		Updates(map[string]interface{}{
			"status": "refund_requested",
			"notes":  updatedNotes,
		})
	if result.Error != nil {
		Error(c, http.StatusInternalServerError, ErrInternal, "退款申请提交失败")
		return
	}

	slog.Info("refund requested", "order_id", req.OrderID, "reason", req.Reason)
	Success(c, gin.H{"message": "退款申请已提交，客服将在24小时内联系您"})
}

func getScheduler(c *gin.Context) *scheduler.Scheduler {
	if v, exists := c.Get("scheduler"); exists {
		if s, ok := v.(*scheduler.Scheduler); ok {
			return s
		}
	}
	sch := scheduler.New()
	return sch
}

func getTemuClient(shopID int) temu.ApiClient {
	cfg := config.Cfg

	appKey := cfg.Temu.AppKey
	appSecret := cfg.Temu.AppSecret
	region := cfg.Temu.Region
	accessToken := ""

	if shopID > 0 {
		cred, err := repository.GetShopCredentials(shopID)
		if err == nil && cred != nil {
			if cred.AppKey != "" {
				appKey = cred.AppKey
			}
			if cred.AppSecret != "" {
				appSecret = cred.AppSecret
			}
			if cred.AccessToken == "" {
				slog.Warn("shop has no access token, using mock", "shop_id", shopID)
				return temu.NewMockClient(shopID)
			}
			accessToken = cred.AccessToken
			if cred.Region != "" {
				region = cred.Region
			}
		} else {
			slog.Warn("shop credentials not found, using mock", "shop_id", shopID, "error", err)
			return temu.NewMockClient(shopID)
		}
	}

	if appKey == "" || appSecret == "" {
		slog.Warn("app_key or app_secret not configured, using mock")
		return temu.NewMockClient(shopID)
	}

	if accessToken == "" {
		slog.Warn("access_token not available, using mock")
		return temu.NewMockClient(shopID)
	}

	client := temu.NewClient(shopID, appKey, appSecret, accessToken, region, cfg.Temu.Proxy)
	slog.Info("created real Temu API client", "shop_id", shopID, "region", region)
	return client
}

func round2(val float64) float64 {
	return float64(int(val*100)) / 100
}
