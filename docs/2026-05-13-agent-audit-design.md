# Agent Quality Audit Case Study — Design Spec

**Date:** 2026-05-13
**Goal:** 用 digital-marketing-pro 插件的智能体系统为跨境电商场景生成营销内容，再用其自带的幻觉检测/声明验证/结构校验工具反向审计产出质量，生成交互式仪表板，包装为求职portfolio项目。

## Overview

### Problem
LLM Agent在营销内容生产中会产生事实性幻觉（编造数据、虚构URL、不存在的竞品），大厂AI团队核心关注"AI可落地性"。需要一套系统化的审计方法来评估Agent输出质量。

### Approach
1. 用DM Pro的4个内容产出Agent为跨境电商品牌生成8份营销内容
2. 用DM Pro自带的 hallucination-detector + claim-verifier + output-validator 审计这些产出
3. 搭建自动化流水线串联全流程，生成交互式HTML仪表板
4. 通过GitHub Pages + QR码交付，面试可扫码查看

### Key Narrative
"建造者 + 审计者"双维度：Dify项目展示我能搭建Agent系统；本项目展示我能评价和改进Agent系统。

## Architecture

```
evaluate_pipeline.py (一键执行入口)
    │
    ├── Stage 1: Agent内容产出
    │   ├── content-creator → 2篇博客文章
    │   ├── email-specialist → 2封邮件
    │   ├── social-media-manager → 2条社媒帖子
    │   └── seo-specialist → 2份SEO策略
    │
    ├── Stage 2: 自动化审计
    │   ├── hallucination-detector → 幻觉检测（假数据/假URL/虚构实体）
    │   ├── claim-verifier → 声明真实性验证
    │   ├── output-validator → 结构schema校验
    │   └── composite scoring → 加权综合评分
    │
    └── Stage 3: 可视化仪表板
        └── index.html (Chart.js交互仪表板) → GitHub Pages → QR码
```

## Brand Setup

跨境电商智能家居氛围灯品牌：
- 品类：智能家居氛围灯（小众品类，易触发Agent幻觉）
- 模式：DTC独立站+Amazon
- 目标市场：美国、德国
- 月营收：$80K
- 竞品：Philips Hue, Govee, Nanoleaf
- 合规：GDPR + CCPA

## Agent Outputs (8 items)

| Agent | Output | Qty |
|-------|--------|-----|
| content-creator | 品类科普博客 + 选购指南 | 2 |
| email-specialist | 促销邮件 + 弃购挽回序列 | 2 |
| social-media-manager | Instagram帖子 + LinkedIn行业帖 | 2 |
| seo-specialist | 关键词策略 + 落地页SEO建议 | 2 |

## Audit Pipeline

对每份Agent产出依次执行：
1. **Hallucination Detection** — 检测虚构统计数字、假URL、不存在实体、编造研究引用
2. **Claim Verification** — 提取事实声明，与品牌profile数据交叉比对
3. **Output Validation** — 按内容类型schema检查结构完整性
4. **Composite Scoring** — 加权汇总，生成agent级别审计卡片

输出：`output/audit_results.json`

## Dashboard Design

单页HTML仪表板 (Chart.js, CDN引入, 无构建工具):

| Section | Content |
|---------|---------|
| Hero | 标题 + 总览数字（幻觉率/声明准确率/综合评分） |
| Agent Comparison | 雷达图 (4 agents × 6 dimensions) + 排名表 |
| Hallucination Details | 按类型统计 + 典型案例高亮引用 |
| Claim Accuracy | 柱状图 + 准确性分层 |
| Methodology | 检测流程说明 |
| Conclusion | 3-5 key findings + 改进建议 |

## Project Structure

```
agent-audit-case/
├── README.md                    # 项目说明 + QR码
├── case_study.md                # 完整案例研究报告
├── pipeline/
│   ├── evaluate.py              # 主入口
│   ├── auditor.py               # 检测脚本适配层
│   └── scorer.py                # 加权评分逻辑
├── output/
│   ├── agent_outputs/           # 8份Agent原始输出
│   ├── audit_results.json       # 结构化审计结果
│   └── screenshots/             # 面试展示截图
├── dashboard/
│   └── index.html               # 单文件交互仪表板
├── scripts/
│   └── qr_generate.py           # QR码生成
└── references/
    └── original_project.md      # 原项目说明
```

## Implementation Files (Core)

| File | Purpose |
|------|---------|
| `pipeline/evaluate.py` | 主入口，一键执行全流程 |
| `pipeline/auditor.py` | 调用DM Pro检测脚本的适配层 |
| `pipeline/scorer.py` | 加权综合评分 |
| `dashboard/index.html` | 交互式仪表板 |
| `case_study.md` | 完整案例研究报告 |

## Tech Stack

- Python 3.x (评估流水线)
- Chart.js (仪表板可视化)
- DM Pro Python scripts (hallucination-detector, claim-verifier, output-validator)
- GitHub Pages (部署)
- qrcode (Python库生成QR码)

## Key Deliverables

1. 可运行的 `evaluate.py` 一键审计流水线
2. 交互式HTML仪表板 (GitHub Pages)
3. 完整案例研究报告 (`case_study.md`)
4. QR码指向仪表板
5. Agent交互截图
