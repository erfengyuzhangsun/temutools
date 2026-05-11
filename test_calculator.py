import pandas as pd
from calculator import ProfitCalculator

print("=" * 60)
print("🧪 Temu 利润计算器 - 单元测试")
print("=" * 60)

df = pd.read_csv('temu_orders_sample.csv')

print(f"\n✅ 成功加载 {len(df)} 条订单数据")
print(f"\n📋 数据列: {list(df.columns)}")

calculator = ProfitCalculator()

try:
    results_df, summary = calculator.process_csv(df)
    
    print("\n" + "=" * 60)
    print("📊 计算结果汇总")
    print("=" * 60)
    
    print(f"\n总订单数: {summary['total_orders']}")
    print(f"总收入: ¥{summary['total_revenue']:,.2f}")
    print(f"总成本: ¥{summary['total_cost']:,.2f}")
    print(f"总利润: ¥{summary['total_profit']:,.2f}")
    print(f"平均利润率: {summary['avg_profit_rate']:.2f}%")
    print(f"总扣费: ¥{summary['total_deduction']:,.2f} (占收入 {summary['deduction_rate']:.1f}%)")
    print(f"净利润率: {summary['net_margin']:.1f}%")
    print(f"预警订单数: {summary['warning_orders']} (利润率 < 5%)")
    print(f"亏损订单数: {summary['loss_orders']}")
    
    print("\n" + "=" * 60)
    print("📈 TOP 5 订单（按利润排序）")
    print("=" * 60)
    
    top5 = results_df.nlargest(5, '利润')[['订单号', 'SKU', '买家支付', '成本价', '利润', '利润率%', '是否预警']]
    for idx, row in top5.iterrows():
        status = "⚠️" if '预警' in row['是否预警'] else "✅"
        print(f"{status} {row['订单号']} | {row['SKU'][:10]} | 支付¥{row['买家支付']:.1f} | 成本¥{row['成本价']:.1f} | 利润¥{row['利润']:.2f} | 利润率{row['利润率%']:.1f}%")
    
    print("\n" + "=" * 60)
    print("⚠️ 预警订单详情")
    print("=" * 60)
    
    warning_orders = results_df[results_df['是否预警'] == '🔴 预警']
    if not warning_orders.empty:
        for idx, row in warning_orders.iterrows():
            print(f"\n🔴 {row['订单号']} | {row['商品名称'][:15]}...")
            print(f"   利润: ¥{row['利润']:.2f} | 利润率: {row['利润率%']:.1f}%")
            print(f"   ⚠️ {row['预警信息']}")
    else:
        print("✅ 无预警订单，所有订单状态良好！")
    
    print("\n" + "=" * 60)
    print("📦 SKU 维度汇总")
    print("=" * 60)
    
    sku_summary = calculator.get_sku_summary(results_df)
    print(f"\n共 {len(sku_summary)} 个 SKU\n")
    
    for idx, row in sku_summary.iterrows():
        status = row['状态']
        print(f"{status} {row['SKU'][:12]:12s} | 销量:{row['销量']:2d}单 | 销售额¥{row['销售额']:7.1f} | 总利润¥{row['总利润']:7.2f} | 利润率{row['利润率']:5.1f}%")
    
    print("\n" + "=" * 60)
    print("💰 费用构成分析")
    print("=" * 60)
    
    fee_breakdown = results_df[['基础佣金', '支付处理费', '绩效附加费', '退货损耗', '运费罚款']].sum()
    total_fees = fee_breakdown.sum()
    
    for fee_name, amount in fee_breakdown.items():
        percentage = (amount / summary['total_revenue']) * 100
        bar = "█" * int(percentage / 2) + "░" * (25 - int(percentage / 2))
        print(f"{fee_name:8s}: ¥{amount:8.2f} ({percentage:5.1f}%) {bar}")
    
    print(f"{'总计':8s}: ¥{total_fees:8.2f} ({(total_fees/summary['total_revenue']*100):5.1f}%)")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！所有功能正常运行")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
