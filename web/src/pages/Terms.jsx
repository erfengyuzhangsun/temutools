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
            最后更新日期：2026 年 05 月 18 日 · 版本 2026-05-18-v2
          </p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            1. 协议主体与适用范围
          </h2>
          <p>1.1 本协议由您（以下简称「用户」或「订阅方」）与鲸云策运营者（以下简称「我们」）订立。运营者为在 Temu Partner Platform 注册开发者账号的个人开发者，以自研应用「鲸云策」向 Temu 卖家提供店铺数据分析与运营管理辅助工具（以下简称「本服务」）。</p>
          <p>1.2 本服务通过 https://www.jinpuhuang.com 提供。您注册、登录、绑定店铺或使用任一功能，即表示已阅读并同意本协议及《隐私政策》的全部条款。</p>
          <p>1.3 本服务为<strong>软件工具服务</strong>，不构成投资顾问、代运营、报关、物流代理或 Temu 官方服务；我们不代表 Temu 或任何第三方作出任何明示或暗示的承诺、保证或担保。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            2. 账号、套餐与付费
          </h2>
          <p>2.1 您应使用真实、有效的邮箱注册，妥善保管账号密码，不得转借、出租、出售账号。因账号密码泄露造成的损失由您自行承担。</p>
          <p>2.2 套餐权限以系统实时展示为准；到期后未续费的功能将受限，数据保留规则详见《隐私政策》。我们保留随时修改套餐定价、功能范围的单方权利，重大变更将提前在网站公示。</p>
          <p>2.3 付费通过线下/微信等方式协商，我们可在确认收款后为您开通或续期套餐。付款后原则上不退款，但因我方原因导致服务连续中断超过 72 小时的，可按中断天数比例折算补偿。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            3. Temu 店铺授权与数据处理（核心）
          </h2>
          <p>3.1 <strong>双重授权</strong>：您使用本服务须同时满足：（a）同意本协议及《隐私政策》；（b）在 Temu 卖家中心对应用「鲸云策」完成官方授权，或按平台规则向我们提供有效的 Access Token。</p>
          <p>3.2 <strong>权属声明</strong>：您声明并保证，您是该店铺有权操作的主体（店主、主账号或经店主书面授权的运营人员），绑定行为不侵犯任何第三方权利。如因您的权属瑕疵导致第三方索赔或 Temu 平台处罚，您应全额赔偿我们因此遭受的全部损失（包括但不限于律师费、诉讼费、仲裁费、赔偿金及平台罚款）。</p>
          <p>3.3 我们仅按您的操作指令、在《隐私政策》载明的范围内，通过 Temu 官方 API 处理店铺经营数据，用于核价辅助、订单同步、库存分析等已开通功能。</p>
          <p>3.4 您可随时在 Temu 卖家中心撤销授权，或在本服务中删除店铺绑定；撤销后我们将停止调用该店铺 API（法律另有要求除外）。</p>
          <p>3.5 您不得利用本服务从事违反 Temu 平台规则、进出口监管或中国/所在地法律的行为，否则我们有权立即暂停或终止您的账号，且不退还任何已付款项。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            4. 与 Temu 平台的关系
          </h2>
          <p>4.1 我们与 Temu 为独立的开发者合作关系；Temu 不对本服务的质量、收益或数据准确性作任何担保。</p>
          <p>4.2 您使用 Temu 卖家账号、API 的权利与义务，同时受 Temu Partner Platform 条款及卖家中心规则约束。您应自行确保您的使用方式符合 Temu 平台规则。</p>
          <p>4.3 若 Temu 要求下架应用、限制 API 或终止合作，我们可能暂停或终止相关功能，并将尽力提前通知已付费用户。因 Temu 平台原因导致的服务变更，我们不承担任何责任。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            5. 服务调整与变更
          </h2>
          <p>5.1 我们保留随时修改、暂停、终止本服务任何功能（全部或部分）的单方权利，无需征得您的事先同意。</p>
          <p>5.2 对已付费用户，如我们主动永久下线其已付费的核心功能，将按剩余服务期比例退还已付费用。因 Temu 平台政策变更、接口调整、法律法规变化等不可归责于我们的原因导致的调整，不适用退款条款。</p>
          <p>5.3 我们可能通过网站公告、系统通知等方式更新本协议，更新后的协议自发布之日起生效。若您继续使用本服务即视为接受更新后的协议。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            6. 知识产权与禁止行为
          </h2>
          <p>6.1 本服务软件、界面、文档、算法、品牌名称的知识产权归我们或合法权利人所有；您获得的是有限、不可转让、不可再许可的使用许可。</p>
          <p>6.2 禁止反向工程、反编译、批量爬取、攻击系统、传播恶意程序、冒用他人店铺、干扰其他用户或从事任何损害我们利益的行为。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            7. 数据准确性免责
          </h2>
          <p>7.1 本服务展示的订单数据、库存数据、核价信息、财务数据等均来源于 Temu 官方 API，我们以「按原样」（AS IS）方式提供，不对数据的完整性、准确性、实时性作任何明示或暗示的保证。</p>
          <p>7.2 自动化核价处理、调价建议、利润分析等功能仅为辅助决策参考，不构成任何经营建议。您应对所有经营决策进行独立判断和人工复核，因依赖本服务数据或建议造成的损失，我们不承担责任。</p>
          <p>7.3 Temu API 可能存在延迟、限流、临时中断或数据错误，您知悉并同意该等风险由您自行承担。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            8. 免责声明与责任限制
          </h2>
          <p>8.1 本服务按「现状」及「可用」基础提供，我们不作任何明示或暗示的保证（包括但不限于适销性、特定用途适用性、不侵权）。</p>
          <p>8.2 因 Temu API 变更、审核、限流、网络故障、不可抗力或第三方原因导致的服务中断或数据丢失，我们在法律允许的最大范围内不承担责任。</p>
          <p>8.3 在法律允许的最大范围内，我们对您的任何间接损失、附带损失、利润损失、商誉损失、数据丢失不承担赔偿责任。</p>
          <p>8.4 <strong>责任上限</strong>：我们的累计赔偿责任总额不超过人民币 100 元 或您在过去 12 个月内已支付的服务费用（以较低者为准）。即使本协议约定的救济措施未能实现其根本目的，本责任限制条款仍然有效。双方确认该责任上限经充分协商，是合理且公平的。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            9. 用户赔偿（Indemnification）
          </h2>
          <p>9.1 您同意赔偿、辩护并使我们（包括我们的关联方、员工、代理人）免受因以下事由引起的任何索赔、诉讼、责任、损失、损害、判决、罚款、成本及费用（包括合理的律师费、仲裁费）的损害：</p>
          <p>（a）您违反本协议任何条款的行为；</p>
          <p>（b）您违反 Temu 平台规则或其他适用法律法规的行为；</p>
          <p>（c）您对店铺权属的陈述不实，或您的绑定行为侵犯第三方权利；</p>
          <p>（d）您利用本服务从事的任何违法违规行为。</p>
          <p>9.2 如因上述事由导致我们被 Temu 平台处罚、冻结 API 权限、扣除保证金或遭受其他损失，您应予以全额赔偿。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            10. 争议解决（仲裁条款）
          </h2>
          <p>10.1 本协议的订立、效力、解释、履行及争议解决，适用中华人民共和国法律（不含冲突法规则）。</p>
          <p>10.2 <strong>仲裁</strong>：因本协议引起的或与本协议有关的任何争议，双方应首先友好协商解决；协商不成的，任何一方均有权将争议提交杭州仲裁委员会（Hangzhou Arbitration Commission）按照其届时有效的仲裁规则进行仲裁。仲裁裁决是终局的，对双方均有约束力。</p>
          <p>10.3 仲裁地为杭州市，仲裁语言为中文。仲裁费用由败诉方承担，除非仲裁庭另有裁决。</p>
          <p>10.4 <strong>仲裁保密性</strong>：仲裁程序、仲裁裁决及相关材料均为保密信息，未经双方书面同意，任何一方不得向第三方披露，但法律另有规定的除外。</p>
          <p>10.5 尽管有上述约定，我们有权在任何有管辖权的法院申请禁令救济或临时保全措施，以保护我们的知识产权或机密信息。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            11. 通知与送达
          </h2>
          <p>11.1 <strong>网站公告</strong>：我们在 https://www.jinpuhuang.com 上发布的公告（包括但不限于协议更新、功能变更、服务调整通知等），自发布之日起即视为已有效送达所有用户。</p>
          <p>11.2 我们也可通过您注册时提供的邮箱或联系微信向您发送通知，该等通知自发送之时视为送达。</p>
          <p>11.3 您应确保提供的联系方式真实有效；因联系方式不准确或不及时更新导致未能收到通知的，我们不承担任何责任。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            12. 可分割性
          </h2>
          <p>12.1 如本协议的任何条款被有管辖权的仲裁庭或法院认定为无效或不可执行，该条款应在必要的最小范围内被限制或删除，其余条款仍然完全有效。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            13. 联系方式
          </h2>
          <p>13.1 联系微信：<strong>returnHuangMuNing</strong>；邮箱：<strong>484478363@qq.com</strong>。</p>

          <hr style={{ margin: '20px 0', border: 'none', borderTop: '1px solid #eee' }} />

          <p style={{ textAlign: 'center', color: '#666' }}>
            注册或使用本服务即表示您已阅读、理解并同意本协议及《隐私政策》的全部条款。
          </p>
        </div>
      </div>
    </div>
  );
}
