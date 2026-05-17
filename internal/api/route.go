package api

import (
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"

	"github.com/erfengyuzhangsun/temutools/internal/api/middleware"
	"github.com/erfengyuzhangsun/temutools/internal/auth"
	"github.com/erfengyuzhangsun/temutools/internal/scheduler"
)

func SetupRouter(authService *auth.AuthService) *gin.Engine {
	r := gin.Default()

	r.Use(gin.Recovery())
	r.Use(CORSMiddleware())

	sch := scheduler.New()
	r.Use(func(c *gin.Context) {
		c.Set("auth_service", authService)
		c.Set("scheduler", sch)
		c.Next()
	})

	apiGroup := r.Group("/api/v1")
	{
		apiGroup.POST("/auth/login", LoginHandler)
		apiGroup.POST("/auth/register", RegisterHandler)
		apiGroup.POST("/submit-order", SubmitOrder)

		protected := apiGroup.Group("")
		protected.Use(middleware.AuthMiddleware(authService))
		{
			protected.GET("/auth/me", GetCurrentUser)

			dashboard := protected.Group("/dashboard")
			dashboard.Use(middleware.PlanGuardMiddleware("dashboard"))
			dashboard.GET("/overview", GetDashboardOverview)
			dashboard.GET("/alerts", GetDashboardAlerts)

			pricing := protected.Group("/pricing")
			pricing.Use(middleware.PlanGuardMiddleware("pricing"))
			pricing.POST("/auto-handle", HandleAutoPricing)
			pricing.GET("/logs", GetPricingLogs)
			pricing.PUT("/threshold", UpdatePricingThreshold)

			inventory := protected.Group("/inventory")
			inventory.Use(middleware.PlanGuardMiddleware("inventory"))
			inventory.GET("/list", GetInventoryList)
			inventory.POST("/sync", SyncInventory)
			inventory.POST("/alert/config", SetInventoryAlert)

			analysis := protected.Group("/analysis")
			analysis.Use(middleware.PlanGuardMiddleware("analysis"))
			analysis.POST("/collect", CollectMetrics)
			analysis.GET("/alerts", GetAnalysisAlerts)
			analysis.GET("/report", GetAnalysisReport)

			finance := protected.Group("/finance")
			finance.Use(middleware.PlanGuardMiddleware("finance"))
			finance.POST("/sync", SyncSettlement)
			finance.GET("/monthly", GetMonthlySummary)
			finance.GET("/forecast", GetForecast)

			apiSync := protected.Group("/api-sync")
			apiSync.Use(middleware.PlanGuardMiddleware("api_sync"))
			apiSync.POST("/sync-orders", SyncOrders)
			apiSync.POST("/bind-shop", BindShop)
			apiSync.GET("/shops", GetShops)
			apiSync.DELETE("/shops/:id", DeleteShop)

			scheduler := protected.Group("/scheduler")
			scheduler.Use(middleware.PlanGuardMiddleware("scheduler"))
			scheduler.GET("/tasks", GetTasks)
			scheduler.POST("/tasks", CreateTask)
			scheduler.PUT("/tasks/:id", UpdateTask)
			scheduler.DELETE("/tasks/:id", DeleteTask)
			scheduler.POST("/tasks/:id/run", RunTaskNow)

			message := protected.Group("/message")
			message.Use(middleware.PlanGuardMiddleware("message"))
			message.GET("/list", GetMessages)
			message.POST("/reply", ReplyMessage)

			shipping := protected.Group("/shipping")
			shipping.Use(middleware.PlanGuardMiddleware("shipping"))
			shipping.GET("/orders", GetShippingOrders)
			shipping.POST("/label", GenerateLabel)

			activity := protected.Group("/activity")
			activity.Use(middleware.PlanGuardMiddleware("activity"))
			activity.GET("/list", GetActivities)
			activity.POST("/signup", SignupActivity)

			riskInspection := protected.Group("/risk-inspection")
			riskInspection.Use(middleware.PlanGuardMiddleware("risk_inspection"))
			riskInspection.GET("/report", GetRiskReport)
			riskInspection.POST("/check", RunRiskCheck)

			batchOps := protected.Group("/batch-ops")
			batchOps.Use(middleware.PlanGuardMiddleware("batch_ops"))
			batchOps.POST("/execute", ExecuteBatchOp)

			reviewMonitor := protected.Group("/review-monitor")
			reviewMonitor.Use(middleware.PlanGuardMiddleware("review_monitor"))
			reviewMonitor.GET("/reviews", GetReviews)
			reviewMonitor.POST("/reply", ReplyReview)

			productResearch := protected.Group("/product-research")
			productResearch.Use(middleware.PlanGuardMiddleware("product_research"))
			productResearch.GET("/products", GetResearchProducts)

			supplier := protected.Group("/supplier")
			supplier.Use(middleware.PlanGuardMiddleware("supplier"))
			supplier.GET("/list", GetSuppliers)
			supplier.POST("/add", AddSupplier)

			factoryCost := protected.Group("/factory-cost")
			factoryCost.Use(middleware.PlanGuardMiddleware("factory_cost"))
			factoryCost.POST("/product", CreateProduct)
			factoryCost.GET("/products", GetFactoryProducts)
			factoryCost.GET("/analysis", GetCostAnalysis)

			pricingEngine := protected.Group("/pricing-engine")
			pricingEngine.Use(middleware.PlanGuardMiddleware("pricing_engine"))
			pricingEngine.POST("/calculate", CalculatePrice)
			pricingEngine.POST("/batch", BatchCalculate)

			riskGuard := protected.Group("/risk-guard")
			riskGuard.Use(middleware.PlanGuardMiddleware("risk_guard"))
			riskGuard.POST("/check", RunRiskGuardCheck)
			riskGuard.GET("/logs", GetRiskGuardLogs)

			apiGuide := protected.Group("/api-guide")
			apiGuide.Use(middleware.PlanGuardMiddleware("api_guide"))
			apiGuide.GET("/guide", GetAPIGuide)
			apiGuide.POST("/test", TestAPIConnection)

			admin := protected.Group("/admin")
			admin.Use(middleware.PlanGuardMiddleware("admin"))
			admin.GET("/users", AdminListUsers)
			admin.POST("/upgrade-plan", AdminUpgradePlan)
			admin.POST("/users/renew", AdminRenewUser)
			admin.POST("/users/toggle", AdminToggleUser)
			admin.GET("/orders", AdminListOrders)
			admin.POST("/orders/complete", AdminCompleteOrder)
			admin.POST("/orders/delete", AdminDeleteOrder)
			admin.GET("/monitor", AdminMonitor)
		}
	}
}

	r.GET("/health", HealthCheck)

	staticDir := filepath.Join(".", "web", "dist")
	r.Static("/assets", filepath.Join(staticDir, "assets"))
	r.Static("/payment", filepath.Join(staticDir, "payment"))
	r.StaticFile("/vite.svg", filepath.Join(staticDir, "vite.svg"))
	r.GET("/login", func(c *gin.Context) {
		c.File(filepath.Join(staticDir, "index.html"))
	})
	r.NoRoute(func(c *gin.Context) {
		path := c.Request.URL.Path
		if strings.HasPrefix(path, "/api/") {
			c.JSON(404, gin.H{
				"success": false,
				"error":   gin.H{"code": "NOT_FOUND", "message": "接口不存在"},
			})
			return
		}
		c.File(filepath.Join(staticDir, "index.html"))
	})

	return r
}

func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE, PATCH")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}
