import pandas as pd
import sys
from io import BytesIO

def test_export_functionality():
    print("=" * 70)
    print("🧪 功能验证：Excel/CSV 导出功能")
    print("=" * 70)
    
    try:
        df = pd.read_csv('temu_orders_sample.csv')
        print(f"\n✅ 成功加载测试数据: {len(df)} 条记录")
        
        from calculator import ProfitCalculator
        calculator = ProfitCalculator()
        results_df, summary = calculator.process_csv(df)
        
        print(f"✅ 利润计算完成，结果包含 {len(results_df)} 条记录")
        
        csv_data = results_df.to_csv(index=False).encode('utf-8-sig')
        print(f"✅ CSV 导出成功，大小: {len(csv_data)/1024:.1f} KB")
        
        try:
            import openpyxl
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                results_df.to_excel(writer, sheet_name='利润明细', index=False)
                summary_df = pd.DataFrame([summary])
                summary_df.to_excel(writer, sheet_name='汇总数据', index=False)
                
                from risk_monitor import RiskMonitor
                monitor = RiskMonitor()
                monitor.calculate_risk_from_csv(df)
                risk_report = monitor.generate_risk_report()
                
                if risk_report:
                    indicators_df = pd.DataFrame(risk_report['详细指标'])
                    indicators_df.to_excel(writer, sheet_name='风险指标', index=False)
                    print(f"✅ Excel 包含3个工作表: 利润明细、汇总数据、风险指标")
            
            output.seek(0)
            excel_size = len(output.getvalue())
            print(f"✅ Excel 导出成功，大小: {excel_size/1024:.1f} KB")
            
        except ImportError:
            print("⚠️ openpyxl 未安装，跳过 Excel 测试")
        except Exception as e:
            print(f"❌ Excel 导出失败: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_export_functionality()
    print("\n" + "=" * 70)
    if success:
        print("✅ 导出功能验证通过！")
    else:
        print("❌ 导出功能存在问题！")
    print("=" * 70)