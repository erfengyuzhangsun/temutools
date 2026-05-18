import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';

const { Title } = Typography;

export default function PrivacyPage() {
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
          <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>隐私政策</Title>
          <p style={{ textAlign: 'center', color: '#999', marginBottom: 24, fontSize: 13 }}>
            最后更新日期：2026 年 05 月 18 日
          </p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            1. 总则
          </h2>
          <p>1.1 感谢您使用鲸云策（以下简称「本工具」）。运营者为在 Temu Partner Platform 注册的个人开发者（当前未登记为公司主体）。我们严格遵循合法、正当、必要、诚信原则，保护您的个人信息与店铺数据安全。</p>
          <p>1.2 本隐私政策旨在清晰告知您，我们如何收集、使用、存储、保护、传输您的相关信息，以及您依法享有的权利、行使权利的方式，同时界定双方在数据处理过程中的责任边界。</p>
          <p>1.3 本隐私政策仅适用于本工具的全部功能及服务，不适用于第三方平台（包括但不限于 Temu 开放平台、DigitalOcean 云服务提供商等）的服务及隐私政策。</p>
          <p>1.4 您在使用本工具前，应仔细阅读并充分理解本隐私政策的全部条款；您点击"同意"、继续使用本工具，即视为您已阅读、理解并完全同意本隐私政策的全部内容；若您不同意本政策，应立即停止使用本工具。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            2. 定义
          </h2>
          <p><strong>个人信息</strong>：指以电子或者其他方式记录的与已识别或者可识别的自然人有关的各种信息，不包括匿名化处理后的信息。</p>
          <p><strong>敏感个人信息</strong>：指一旦泄露或者非法使用，容易导致自然人的人格尊严受到侵害或者人身、财产安全受到危害的个人信息，本工具中主要指您的 Temu API Key、API Secret（以下统称"API 信息"）。</p>
          <p><strong>非个人信息</strong>：指不涉及自然人个人身份、无法识别具体自然人的信息，包括但不限于 Temu 店铺订单数据、库存数据、结算数据、核价数据（该类数据仅与店铺经营相关）、工具使用日志（脱敏后）等。</p>
          <p><strong>数据处理</strong>：指收集、存储、使用、加工、传输、提供、删除、匿名化等与信息相关的全部行为。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            3. 我们收集的信息
          </h2>
          <p><strong>3.1 您主动提供的信息</strong></p>
          <p><strong>敏感个人信息</strong>：Temu API Key、API Secret，您主动提供该类信息，系授权我们通过 Temu 开放平台官方 API 接口获取您的店铺相关经营数据，仅用于接口调用，不用于任何其他用途。</p>
          <p><strong>基础信息</strong>：店铺名称、店铺类目，用于实现多店铺统一管理、数据隔离。</p>
          <p><strong>登录信息</strong>：访问密码（加密存储），用于您登录本工具的身份验证。</p>
          <p><strong>联系方式</strong>：您自愿提供的微信（用于接收通知、响应您的咨询及权利行使请求）。</p>
          <p><strong>3.2 我们自动获取的信息</strong></p>
          <p><strong>店铺经营数据</strong>：通过您授权的 Temu 官方 API 接口，自动获取您的 Temu 店铺相关数据，包括但不限于订单编号、订单金额、商品信息、SKU、库存数量、结算金额、回款记录、核价信息、报价等，仅用于实现利润计算、订单统计、库存管理等核心功能。</p>
          <p><strong>工具使用日志</strong>：自动记录您使用本工具的相关操作日志，包括登录时间、操作模块、使用时长，仅用于工具运营维护、故障排查、功能优化，日志中不记录完整的 API 信息、密码等敏感数据。</p>
          <p><strong>设备基础信息</strong>：自动获取您用于访问本工具的设备基础信息（包括设备型号、浏览器类型、IP 地址），仅用于识别异常登录、防范账号被盗及网络安全风险。</p>
          <p><strong>3.3 收集信息的合法性依据</strong></p>
          <p>我们收集您的信息，均基于以下合法情形：</p>
          <p>您的明确同意（尤其是敏感个人信息的收集，需您单独确认同意后才会收集）</p>
          <p>履行本工具服务协议、实现工具核心功能所必需</p>
          <p>遵守法律法规、响应国家机关依法开展的调查取证要求</p>
          <p>保护您的合法权益、防范网络安全风险所必需</p>
          <p><strong>3.4 禁止收集的信息</strong></p>
          <p>我们绝对不会收集与本工具功能无关的任何信息，包括但不限于：您的身份证号、银行卡号、家庭住址、通讯记录、相册、通讯录等个人隐私信息；Temu 平台未开放的非公开接口数据、其他用户的店铺数据及个人信息。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            4. 我们如何使用您的信息
          </h2>
          <p><strong>4.1 信息使用范围</strong></p>
          <p><strong>核心功能实现</strong>：使用您的 API 信息调用 Temu 官方 API，获取店铺经营数据，为您提供利润计算、订单统计、库存管理与预警、数据分析与报表生成、核价通知自动判断与处理（仅当您主动开启该功能时）、多店铺统一管理等服务。</p>
          <p><strong>账号安全保障</strong>：使用您的登录信息、设备基础信息、使用日志，识别异常登录行为，防范账号被盗、未授权访问等风险。</p>
          <p><strong>工具优化与维护</strong>：使用脱敏后的工具使用日志，分析工具使用情况，优化功能体验、修复故障。</p>
          <p><strong>响应您的请求</strong>：使用您的联系方式，响应您的咨询、投诉、权利行使请求，向您推送必要的工具更新通知、数据安全提醒。</p>
          <p><strong>遵守法律法规</strong>：按照法律法规、国家机关调查取证要求，使用、提供相关信息。</p>
          <p><strong>4.2 信息使用限制</strong></p>
          <p>仅使用实现工具功能所必需的信息，不超出您授权的范围使用信息</p>
          <p>绝对不会将您的信息出售、出租、出借、转让给任何第三方</p>
          <p>不会将您的信息用于未经您授权的任何目的</p>
          <p>对店铺经营数据进行匿名化处理后，可用于工具优化、行业数据分析</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            5. 数据存储与保护
          </h2>
          <p><strong>5.1 存储方式</strong></p>
          <p>您的所有信息均存储于 DigitalOcean 新加坡节点服务器，服务器由 DigitalOcean 提供安全保障。</p>
          <p><strong>5.2 安全保护措施</strong></p>
          <p><strong>加密保护</strong>：您的 API 信息、访问密码，采用 AES-256 加密算法进行加密后存储；所有数据传输过程均通过 TLS 1.2+ 加密通道进行</p>
          <p><strong>数据隔离</strong>：采用用户 ID 严格隔离机制，每个用户的信息、店铺数据单独存储</p>
          <p><strong>访问控制</strong>：仅授权的技术、运营人员（签订保密协议）可访问相关数据，日志记录所有访问行为</p>
          <p><strong>日志脱敏</strong>：系统日志中不记录完整的 API 信息、访问密码等敏感数据</p>
          <p><strong>安全防护</strong>：服务器部署防火墙、入侵检测系统，定期进行安全检测、漏洞修复</p>
          <p><strong>5.3 数据存储期限</strong></p>
          <p>我们仅在您使用本工具期间，为实现工具功能所必需的期限内保留您的信息</p>
          <p>您主动要求删除全部数据的，我们将在收到您的有效申请后 15 个工作日内完成删除</p>
          <p>若您连续 6 个月未登录本工具，视为停止使用，我们将在 15 个工作日内主动删除您的全部数据</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            6. 您的权利
          </h2>
          <p>根据《个人信息保护法》等相关法律法规，您依法享有以下权利：</p>
          <p><strong>知情权</strong>：了解我们收集、使用、存储、保护您信息的全部情况</p>
          <p><strong>删除权</strong>：随时要求我们删除您的全部信息，我们将在收到申请后 15 个工作日内完成</p>
          <p><strong>撤回同意权</strong>：随时撤回对本工具收集、使用您信息的同意，撤回后我们将立即停止收集并使用您的信息</p>
          <p><strong>数据可携带权</strong>：要求我们向您提供您的信息副本</p>
          <p><strong>更正权</strong>：要求我们更正您的信息（如店铺名称、联系方式等）</p>
          <p><strong>投诉举报权</strong>：向我们投诉，或向国家网信部门等相关主管部门举报</p>
          <p>如需行使以上权利，请联系微信：<strong>returnHuangMuNing</strong>。</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            7. 跨境传输与第三方服务
          </h2>
          <p><strong>跨境传输说明</strong>：您的账号信息、店铺凭证及经营数据可能存储于 DigitalOcean 新加坡节点。我们采取加密与访问控制措施；您注册并绑定店铺即表示知悉并同意该跨境存储与处理，法律要求单独同意的从其规定。</p>
          <p><strong>Temu 开放平台</strong>：我们通过 Temu 官方 API 接口获取数据，数据使用受 Temu《开发者协议》约束</p>
          <p><strong>DigitalOcean 云服务提供商</strong>：我们使用 DigitalOcean 新加坡节点服务器存储您的信息，服务器安全保障由 DigitalOcean 负责</p>
          <p>我们不会将您的信息委托给任何其他第三方处理</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            8. 隐私政策的更新
          </h2>
          <p>我们可能会不时更新本隐私政策，更新后的版本将在工具中显著提示</p>
          <p>若发生重大变更，我们将通过您绑定的微信发送变更通知</p>
          <p>若您不同意更新后的隐私政策，应立即停止使用本工具</p>

          <h2 style={{ fontSize: '1.15rem', marginTop: 20, marginBottom: 8, color: '#1a1a2e', borderBottom: '1px solid #eee', paddingBottom: 4 }}>
            9. 免责条款
          </h2>
          <p>因不可抗力（自然灾害、战争、政策调整、网络中断、服务器故障等）导致的信息泄露等，我们不承担法律责任，但将尽力采取补救措施</p>
          <p>因您自身原因（泄露密码、转借账号、使用不安全网络等）导致的信息泄露，由您自行承担</p>
          <p>因 Temu 开放平台 API 接口故障、数据错误、政策调整等原因导致的问题，我们不承担责任</p>
          <p>因 DigitalOcean 服务器故障、安全漏洞等原因导致的问题，我们不承担直接责任，但将协助您追责</p>
          <p>因网络安全技术的局限性、黑客攻击等不可防范的原因导致的问题，且我们无过错的，我们不承担责任</p>
          <p>您因违反本隐私政策、法律法规、Temu 平台规则导致损失的，由您自行承担</p>

          <hr style={{ margin: '20px 0', border: 'none', borderTop: '1px solid #eee' }} />

          <p style={{ textAlign: 'center', color: '#666' }}>
            使用本工具即表示您已阅读、理解并同意本隐私政策的全部条款。
          </p>
        </div>
      </div>
    </div>
  );
}
