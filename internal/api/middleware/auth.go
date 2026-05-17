package middleware

import (
	"strings"

	"github.com/gin-gonic/gin"

	"github.com/erfengyuzhangsun/temutools/internal/auth"
)

const (
	ContextKeyUserID   = "user_id"
	ContextKeyPlanType = "plan_type"
)

type PlanHierarchy struct {
	Basic      int
	Pro        int
	Enterprise int
	Lifetime   int
}

var PlanLevel = PlanHierarchy{
	Basic:      0,
	Pro:        1,
	Enterprise: 2,
	Lifetime:   3,
}

var PagePlans = map[string]string{
	"app":              "basic",
	"finance":          "basic",
	"risk_inspection":  "basic",
	"inventory":        "basic",
	"pricing_engine":   "basic",
	"dashboard":        "basic",
	"api_sync":         "pro",
	"api_guide":        "pro",
	"pricing":          "pro",
	"pricing_adj":      "pro",
	"risk_guard":       "pro",
	"analysis":         "pro",
	"scheduler":        "pro",
	"message":          "pro",
	"activity":         "pro",
	"review_monitor":   "pro",
	"shipping":         "pro",
	"factory_cost":     "enterprise",
	"supplier":         "enterprise",
	"batch_ops":        "enterprise",
	"product_research": "enterprise",
	"admin":            "lifetime",
}

var planLevelMap = map[string]int{
	"basic":      0,
	"pro":        1,
	"enterprise": 2,
	"lifetime":   3,
}

func HasPlanAccess(page, planType string) bool {
	required, ok := PagePlans[page]
	if !ok {
		return planLevelMap[planType] >= planLevelMap["pro"]
	}
	return planLevelMap[planType] >= planLevelMap[required]
}

func AuthMiddleware(authService *auth.AuthService) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(401, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "UNAUTHORIZED",
					"message": "缺少认证令牌",
				},
			})
			c.Abort()
			return
		}

		tokenStr := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenStr == authHeader {
			c.JSON(401, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "UNAUTHORIZED",
					"message": "认证格式无效，使用: Bearer <token>",
				},
			})
			c.Abort()
			return
		}

		claims, err := authService.ValidateToken(tokenStr)
		if err != nil {
			c.JSON(401, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "UNAUTHORIZED",
					"message": "令牌无效或已过期",
					"details": err.Error(),
				},
			})
			c.Abort()
			return
		}

		c.Set(ContextKeyUserID, claims.UserID)
		c.Set(ContextKeyPlanType, claims.PlanType)
		c.Next()
	}
}

func PlanGuardMiddleware(page string) gin.HandlerFunc {
	return func(c *gin.Context) {
		planType, _ := c.Get(ContextKeyPlanType)
		planStr, _ := planType.(string)

		if !HasPlanAccess(page, planStr) {
			requiredPlan := PagePlans[page]
			planNames := map[string]string{
				"basic":      "基础版",
				"pro":        "专业版",
				"enterprise": "企业版",
				"lifetime":   "终身版",
			}
			requiredName := planNames[requiredPlan]
			if requiredName == "" {
				requiredName = requiredPlan
			}

			c.JSON(403, gin.H{
				"success": false,
				"error": gin.H{
					"code":    "PLAN_ACCESS_DENIED",
					"message": "当前套餐无权访问此功能",
					"details": "需要 " + requiredName + " 或更高版本",
				},
			})
			c.Abort()
			return
		}
		c.Next()
	}
}

func GetUserID(c *gin.Context) int {
	userID, _ := c.Get(ContextKeyUserID)
	id, _ := userID.(int)
	return id
}

func GetPlanType(c *gin.Context) string {
	planType, _ := c.Get(ContextKeyPlanType)
	p, _ := planType.(string)
	return p
}
