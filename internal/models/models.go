package models

import "time"

type User struct {
	UserID         int        `gorm:"column:user_id;primaryKey;autoIncrement"`
	Email          string     `gorm:"column:email;type:varchar(255);not null;uniqueIndex"`
	PasswordHash   string     `gorm:"column:password_hash;type:varchar(255);not null"`
	WechatNickname string     `gorm:"column:wechat_nickname;type:varchar(100);not null;default:''"`
	PlanType       string     `gorm:"column:plan_type;type:varchar(20);not null;default:'basic'"`
	StartDate      *time.Time `gorm:"column:start_date;type:date"`
	ExpireDate     *time.Time `gorm:"column:expire_date;type:date"`
	IsActive         bool       `gorm:"column:is_active;default:true"`
	TermsAgreedAt    *time.Time `gorm:"column:terms_agreed_at"`
	PrivacyAgreedAt  *time.Time `gorm:"column:privacy_agreed_at"`
	PolicyVersion    string     `gorm:"column:policy_version;type:varchar(20);not null;default:''"`
	CreatedAt        time.Time  `gorm:"column:created_at"`
	UpdatedAt        time.Time  `gorm:"column:updated_at"`
}

func (User) TableName() string { return "temu_users" }

type Shop struct {
	ShopID        int       `gorm:"column:shop_id;primaryKey;autoIncrement"`
	UserID        int       `gorm:"column:user_id;not null"`
	ShopName      string    `gorm:"column:shop_name;type:varchar(100);not null"`
	MainCategory  string    `gorm:"column:main_category;type:varchar(50)"`
	CreatedAt     time.Time `gorm:"column:created_at"`
}

func (Shop) TableName() string { return "temu_shops" }

type ShopCredential struct {
	CredID                int    `gorm:"column:cred_id;primaryKey;autoIncrement"`
	ShopID                int    `gorm:"column:shop_id;not null"`
	EncryptedAPIKey       string `gorm:"column:encrypted_api_key;type:text"`
	EncryptedAPISecret    string `gorm:"column:encrypted_api_secret;type:text"`
	EncryptedAccessToken  string `gorm:"column:encrypted_access_token;type:text"`
	Region                string `gorm:"column:region;type:varchar(20);default:'us'"`
}

func (ShopCredential) TableName() string { return "temu_shop_credentials" }

type ProfitStat struct {
	StatID             int     `gorm:"column:stat_id;primaryKey;autoIncrement"`
	UserID             int     `gorm:"column:user_id;not null"`
	ShopID             int     `gorm:"column:shop_id;not null"`
	StatDate           string  `gorm:"column:stat_date;type:date"`
	TotalOrders        int     `gorm:"column:total_orders;default:0"`
	TotalRevenue       float64 `gorm:"column:total_revenue;type:decimal(10,2);default:0"`
	TotalCost          float64 `gorm:"column:total_cost;type:decimal(10,2);default:0"`
	TotalCommission    float64 `gorm:"column:total_commission;type:decimal(10,2);default:0"`
	TotalPaymentFee    float64 `gorm:"column:total_payment_fee;type:decimal(10,2);default:0"`
	TotalPerformanceFee float64 `gorm:"column:total_performance_fee;type:decimal(10,2);default:0"`
	TotalReturnLoss    float64 `gorm:"column:total_return_loss;type:decimal(10,2);default:0"`
	TotalShippingPenalty float64 `gorm:"column:total_shipping_penalty;type:decimal(10,2);default:0"`
	TotalProfit        float64 `gorm:"column:total_profit;type:decimal(10,2);default:0"`
	NetProfitRate      float64 `gorm:"column:net_profit_rate;type:decimal(5,2);default:0"`
}

func (ProfitStat) TableName() string { return "temu_profit_stats" }

type SkuProfit struct {
	SkuID        int     `gorm:"column:sku_id;primaryKey;autoIncrement"`
	UserID       int     `gorm:"column:user_id;not null"`
	ShopID       int     `gorm:"column:shop_id;not null"`
	SkuCode      string  `gorm:"column:sku_code;type:varchar(100);not null"`
	SkuName      string  `gorm:"column:sku_name;type:varchar(255);not null"`
	Category     string  `gorm:"column:category;type:varchar(50);not null"`
	CostPrice    float64 `gorm:"column:cost_price;type:decimal(10,2);not null"`
	TotalSales   int     `gorm:"column:total_sales;default:0"`
	TotalRevenue float64 `gorm:"column:total_revenue;type:decimal(10,2);default:0"`
	TotalProfit  float64 `gorm:"column:total_profit;type:decimal(10,2);default:0"`
	ProfitRate   float64 `gorm:"column:profit_rate;type:decimal(5,2);default:0"`
	IsLoss       bool    `gorm:"column:is_loss;default:false"`
	IsWarning    bool    `gorm:"column:is_warning;default:false"`
}

func (SkuProfit) TableName() string { return "temu_sku_profit" }

type PricingLog struct {
	LogID        int       `gorm:"column:log_id;primaryKey;autoIncrement"`
	UserID       int       `gorm:"column:user_id;not null"`
	ShopID       int       `gorm:"column:shop_id;not null"`
	NoticeID     string    `gorm:"column:notice_id;type:varchar(100)"`
	Sku          string    `gorm:"column:sku;type:varchar(100)"`
	Action       string    `gorm:"column:action;type:varchar(20)"`
	SupplyPrice  float64   `gorm:"column:supply_price;type:decimal(10,2)"`
	CostPrice    float64   `gorm:"column:cost_price;type:decimal(10,2)"`
	GrossMargin  float64   `gorm:"column:gross_margin;type:decimal(5,2)"`
	Reason       string    `gorm:"column:reason;type:text"`
	IsActivity   bool      `gorm:"column:is_activity;default:false"`
	HandledAt    time.Time `gorm:"column:handled_at"`
}

func (PricingLog) TableName() string { return "temu_pricing_logs" }

type SyncRecord struct {
	SyncID        int       `gorm:"column:sync_id;primaryKey;autoIncrement"`
	UserID        int       `gorm:"column:user_id;not null"`
	ShopID        int       `gorm:"column:shop_id;not null"`
	SyncType      string    `gorm:"column:sync_type;type:varchar(20)"`
	Status        string    `gorm:"column:status;type:varchar(20)"`
	SyncedCount   int       `gorm:"column:synced_count;default:0"`
	TotalCount    int       `gorm:"column:total_count;default:0"`
	DurationMs    int       `gorm:"column:duration_ms;default:0"`
	ErrorMessage  string    `gorm:"column:error_message;type:text"`
	StartedAt     time.Time `gorm:"column:started_at"`
	CreatedAt     time.Time `gorm:"column:created_at"`
}

func (SyncRecord) TableName() string { return "temu_sync_records" }

type TaskDefinition struct {
	TaskID         string `gorm:"column:task_id;primaryKey;type:varchar(100)"`
	Name           string `gorm:"column:name;type:varchar(200);not null"`
	CronExpression string `gorm:"column:cron_expression;type:varchar(100)"`
	ModuleName     string `gorm:"column:module_name;type:varchar(50)"`
	TimeoutSeconds int    `gorm:"column:timeout_seconds;default:300"`
	MaxRetries     int    `gorm:"column:max_retries;default:3"`
	Enabled        bool   `gorm:"column:enabled;default:true"`
	Description    string `gorm:"column:description;type:text"`
}

func (TaskDefinition) TableName() string { return "temu_task_definitions" }

type SchedulerTask struct {
	TaskID        string     `gorm:"column:task_id;primaryKey;type:varchar(100)"`
	Name          string     `gorm:"column:name;type:varchar(255);not null"`
	CronExpression string    `gorm:"column:cron_expression;type:varchar(50);not null"`
	TimeoutSeconds int       `gorm:"column:timeout_seconds;default:300"`
	MaxRetries    int        `gorm:"column:max_retries;default:3"`
	Enabled       bool       `gorm:"column:enabled;default:true"`
	Description   string     `gorm:"column:description;type:text"`
	LastRunAt     *time.Time `gorm:"column:last_run_at"`
	NextRunAt     *time.Time `gorm:"column:next_run_at"`
	RunCount      int        `gorm:"column:run_count;default:0"`
	FailCount     int        `gorm:"column:fail_count;default:0"`
	CreatedAt     time.Time  `gorm:"column:created_at"`
	UpdatedAt     time.Time  `gorm:"column:updated_at"`
}

func (SchedulerTask) TableName() string { return "temu_scheduler_tasks" }

type SchedulerLog struct {
	LogID          int        `gorm:"column:log_id;primaryKey;autoIncrement"`
	TaskID         string     `gorm:"column:task_id;type:varchar(100);not null"`
	Status         string     `gorm:"column:status;type:varchar(20);not null"`
	StartedAt      time.Time  `gorm:"column:started_at"`
	FinishedAt     *time.Time `gorm:"column:finished_at"`
	DurationSeconds float64   `gorm:"column:duration_seconds;type:decimal(10,2);default:0"`
	ErrorMessage   string     `gorm:"column:error_message;type:text"`
	RetryCount     int        `gorm:"column:retry_count;default:0"`
}

func (SchedulerLog) TableName() string { return "temu_scheduler_logs" }

type FactoryProduct struct {
	ProductID            int       `gorm:"column:product_id;primaryKey;autoIncrement"`
	UserID               int       `gorm:"column:user_id;not null"`
	ProductName          string    `gorm:"column:product_name;type:varchar(255);not null"`
	SkuCode              string    `gorm:"column:sku_code;type:varchar(100);not null"`
	CategoryName         string    `gorm:"column:category_name;type:varchar(100);default:''"`
	MaterialCost         float64   `gorm:"column:material_cost;type:decimal(10,2);default:0"`
	LaborCost            float64   `gorm:"column:labor_cost;type:decimal(10,2);default:0"`
	PackagingCost        float64   `gorm:"column:packaging_cost;type:decimal(10,2);default:0"`
	ShippingCost         float64   `gorm:"column:shipping_cost;type:decimal(10,2);default:0"`
	OtherCost            float64   `gorm:"column:other_cost;type:decimal(10,2);default:0"`
	TotalCost            float64   `gorm:"column:total_cost;type:decimal(10,2);default:0"`
	ExpectedProfitMargin float64   `gorm:"column:expected_profit_margin;type:decimal(5,2);default:20"`
	SuggestedSupplyPrice float64   `gorm:"column:suggested_supply_price;type:decimal(10,2);default:0"`
	IsFullCommission     bool      `gorm:"column:is_full_commission;default:true"`
	CreatedAt            time.Time `gorm:"column:created_at"`
	UpdatedAt            time.Time `gorm:"column:updated_at"`
}

func (FactoryProduct) TableName() string { return "temu_factory_products" }

type Supplier struct {
	SupplierID   int       `gorm:"column:supplier_id;primaryKey;autoIncrement"`
	UserID       int       `gorm:"column:user_id;not null"`
	Name         string    `gorm:"column:name;type:varchar(200);not null"`
	Contact      string    `gorm:"column:contact;type:varchar(100)"`
	Phone        string    `gorm:"column:phone;type:varchar(50)"`
	MainCategory string    `gorm:"column:main_category;type:varchar(50)"`
	Rating       float64   `gorm:"column:rating;type:decimal(3,1);default:5.0"`
	Status       string    `gorm:"column:status;type:varchar(20);default:'active'"`
	CreatedAt    time.Time `gorm:"column:created_at"`
}

func (Supplier) TableName() string { return "temu_suppliers" }

type Order struct {
	OrderID     int       `gorm:"column:order_id;primaryKey;autoIncrement" json:"order_id"`
	ContactName string    `gorm:"column:contact_name;type:varchar(255);not null" json:"contact_name"`
	Phone       string    `gorm:"column:phone;type:varchar(255);not null" json:"phone"`
	Wechat      string    `gorm:"column:wechat;type:varchar(255);default:''" json:"wechat"`
	PlanName    string    `gorm:"column:plan_name;type:varchar(100);not null" json:"plan_name"`
	Amount      float64   `gorm:"column:amount;type:decimal(10,2);default:0" json:"amount"`
	Notes       string    `gorm:"column:notes;type:text" json:"notes"`
	Status      string    `gorm:"column:status;type:varchar(20);default:'pending'" json:"status"`
	CreatedAt   time.Time `gorm:"column:created_at" json:"created_at"`
}

func (Order) TableName() string { return "temu_orders" }

type SettlementRecord struct {
	SettlementID     int       `gorm:"column:settlement_id;primaryKey;autoIncrement" json:"settlement_id"`
	UserID           int       `gorm:"column:user_id;not null" json:"user_id"`
	ShopID           int       `gorm:"column:shop_id;not null" json:"shop_id"`
	OrderSn          string    `gorm:"column:order_sn;type:varchar(100);not null" json:"order_sn"`
	TotalAmount      float64   `gorm:"column:total_amount;type:decimal(12,2);default:0" json:"total_amount"`
	PlatformFee      float64   `gorm:"column:platform_fee;type:decimal(10,2);default:0" json:"platform_fee"`
	SettlementAmount float64   `gorm:"column:settlement_amount;type:decimal(12,2);default:0" json:"settlement_amount"`
	CostPrice        float64   `gorm:"column:cost_price;type:decimal(10,2);default:0" json:"cost_price"`
	Profit           float64   `gorm:"column:profit;type:decimal(10,2);default:0" json:"profit"`
	StatDate         string    `gorm:"column:stat_date;type:date" json:"stat_date"`
	CreatedAt        time.Time `gorm:"column:created_at" json:"created_at"`
}

func (SettlementRecord) TableName() string { return "temu_settlement_records" }
