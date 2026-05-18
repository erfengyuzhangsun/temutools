import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

const { Title } = Typography;

export default function TermsPage() {
  const navigate = useNavigate();

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: 24 }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/login')}
          style={{ marginBottom: 16 }}
        >
          返回登录
        </Button>

        <div style={{
          background: '#fff',
          padding: '32px 40px',
          borderRadius: 12,
          boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
          lineHeight: 1.8,
          fontSize: 14,
          color: '#333',
        }}>
          <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>用户服务协议</Title>
          <p style={{ textAlign: 'center', color: '#999', marginBottom: 24, fontSize: 13 }}>
            最后更新日期：2026 年 05 月 18 日 · 版本 2026-05-18
          </p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            1. 协议主体与适用范围
          </h2>
          <p>1.1 本协议由您（以下简称「用户」或「订阅方」）与鲸云策运营者（以下简称「我们」）订立。运营者为在 Temu Partner Platform 注册开发者账号的个人开发者，以自研应用「鲸云策」向 Temu 卖家提供店铺数据分析与运营管理辅助工具（以下简称「本服务」）。</p>
          <p>1.2 本服务通过 https://www.jinpuhuang.com 提供。您注册、登录、绑定店铺或使用任一功能，即表示已阅读并同意本协议及《隐私政策》。</p>
          <p>1.3 本服务为<strong>软件工具服务</strong>，不构成投资顾问、代运营、报关、物流代理或 Temu 官方服务；我们不代表 Temu 或任何第三方作出承诺。</p>
          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            2. 账号、套餐与付费
          </h2>
          <p>2.1 您应使用真实、有效的邮箱注册，妥善保管账号密码，不得转借、出租账号。</p>
          <p>2.2 套餐权限以系统展示为准；到期后未续费的功能将受限，数据保留与删除规则见《隐私政策》。</p>
          <p>2.3 付费通过线下/微信等方式协商，我们可在确认收款后为您开通或续期套餐。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            3. Temu 店铺授权与数据处理（核心）
          </h2>
          <p>3.1 <strong>双重授权</strong>：您使用本服务须同时满足：（a）同意本协议及《隐私政策》；（b）在 Temu 卖家中心对应用「鲸云策」完成官方授权，或按平台规则向我们提供有效的 Access Token。</p>
          <p>3.2 您声明：您是该店铺有权操作的主体（店主、主账号或经店主书面授权的运营人员），绑定行为未侵犯任何第三方权利。</p>
          <p>3.3 我们仅按您的操作指令、在《隐私政策》载明的范围内，通过 Temu 官方 API 处理店铺经营数据，用于核价辅助、订单同步、库存分析等已开通功能。</p>
          <p>3.4 您可随时在 Temu 卖家中心撤销授权，或在本服务中删除店铺绑定；撤销后我们将停止调用该店铺 API（法律另有要求除外）。</p>
          <p>3.5 您不得利用本服务从事违反 Temu 平台规则、进出口监管或中国/所在地法律的行为。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            4. 与 Temu 平台的关系
          </h2>
          <p>4.1 我们与 Temu 为独立的开发者合作关系；Temu 不对本服务的质量、收益或数据准确性作担保。</p>
          <p>4.2 您使用 Temu 卖家账号、API 的权利与义务，同时受 Temu Partner Platform 条款及卖家中心规则约束。</p>
          <p>4.3 若 Temu 要求下架应用、限制 API 或终止合作，我们可能暂停相关功能，并将尽力提前通知已付费用户。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            5. 知识产权与禁止行为
          </h2>
          <p>5.1 本服务软件、界面、文档的知识产权归我们或合法权利人所有；您获得的是有限、不可转让的使用许可。</p>
          <p>5.2 禁止反向工程、批量爬取、攻击系统、传播恶意程序、冒用他人店铺或干扰其他用户。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            6. 免责声明与责任限制
          </h2>
          <p>6.1 本服务按「现状」提供；自动化规则、API 返回数据可能存在延迟或误差，您应结合人工复核重要经营决策。</p>
          <p>6.2 因 Temu API 变更、审核、限流、网络或不可抗力导致的服务中断，我们在法律允许范围内不承担责任。</p>
          <p>6.3 在法律允许的最大范围内，我们对您的间接损失、利润损失不承担赔偿责任；我们的累计赔偿责任不超过您就争议功能在过去 12 个月内已支付的服务费用（如有）。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            7. 协议变更与终止
          </h2>
          <p>7.1 我们可能更新本协议，重大变更将在网站公示；若您继续使用即视为接受。</p>
          <p>7.2 您可随时停止使用并申请删除数据；我们可在您严重违约时暂停或终止账号。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            8. 争议解决与联系方式
          </h2>
          <p>8.1 本协议适用中华人民共和国法律（不含冲突法规则）。</p>
          <p>8.2 争议应友好协商；协商不成的，提交运营者所在地有管辖权的人民法院诉讼解决。</p>
          <p>8.3 联系微信：<strong>returnHuangMuNing</strong>；邮箱：<strong>484478363@qq.com</strong>。</p>

          <hr style={{ margin: '20px 0', border: 'none', borderTop: '1px solid #eee' }} />

          <p style={{ textAlign: 'center', color: '#666' }}>
            注册或使用本服务即表示您已阅读、理解并同意本协议及《隐私政策》的全部条款。
          </p>
        </div>
      </div>
    </div>
  );
}
