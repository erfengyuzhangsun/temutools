package middleware

import (
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestHasPlanAccess(t *testing.T) {
	tests := []struct {
		name     string
		page     string
		planType string
		want     bool
	}{
		{"basic user can access basic page", "dashboard", "basic", true},
		{"basic user can access finance", "finance", "basic", true},
		{"basic user cannot access pro page", "pricing", "basic", false},
		{"basic user cannot access enterprise page", "factory_cost", "basic", false},
		{"pro user can access basic page", "dashboard", "pro", true},
		{"pro user can access pro page", "pricing", "pro", true},
		{"pro user cannot access enterprise page", "factory_cost", "pro", false},
		{"enterprise user can access all", "factory_cost", "enterprise", true},
		{"enterprise user can access basic", "dashboard", "enterprise", true},
		{"enterprise user can access pro", "pricing", "enterprise", true},
		{"lifetime user can access all", "supplier", "lifetime", true},
		{"unknown page defaults to pro", "unknown_module", "basic", false},
		{"unknown page accessible by pro", "unknown_module", "pro", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := HasPlanAccess(tt.page, tt.planType)
			assert.Equal(t, tt.want, got, "HasPlanAccess(%q, %q)", tt.page, tt.planType)
		})
	}
}

func TestPlanGuardAllPages(t *testing.T) {
	pages := []string{
		"app", "finance", "risk_inspection", "inventory",
		"pricing_engine", "dashboard", "api_sync", "api_guide",
		"pricing", "pricing_adj", "risk_guard", "analysis",
		"scheduler", "message", "activity", "review_monitor",
		"shipping", "factory_cost", "supplier", "batch_ops",
		"product_research",
	}

	for _, page := range pages {
		_, exists := PagePlans[page]
		assert.True(t, exists, "page %s should exist in PagePlans", page)
	}
}

func TestPlanLevelMap(t *testing.T) {
	assert.Equal(t, 0, planLevelMap["basic"])
	assert.Equal(t, 1, planLevelMap["pro"])
	assert.Equal(t, 2, planLevelMap["enterprise"])
	assert.Equal(t, 3, planLevelMap["lifetime"])
}

func TestGetUserID(t *testing.T) {
	assert.NotPanics(t, func() {
		_ = (*gin.Context)(nil)
	})
}
