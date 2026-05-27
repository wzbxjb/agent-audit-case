# Agent Quality Audit — digital-marketing-pro Case Study

用 Claude Code 数字营销插件的 Agent 系统为跨境电商品牌生成营销内容，再用**自研的 4 个检测引擎**（零 DM Pro 依赖）反向审计 Agent 输出质量。

**作者：wzbxjb UIUC Data Science 

## 技术亮点

- **4 个自研检测引擎**替代 DM Pro subprocess 调用
  - `HallucinationDetector` — 多模式幻觉检测（正则模式 + NER + 限定词分析）
  - `ClaimChecker` — 语义级声明验证（embedding 余弦相似度，替代 SequenceMatcher）
  - `StructureValidator` — 语义结构校验（关键词模式检测，替代章节标题正则）
  - `StatisticalAuditor` — Bootstrap CI + 阈值稳定性 + 评分者间信度
- 加权综合评分 + 95% Bootstrap 置信区间
- 交互式 Chart.js 暗色仪表板

## 快速开始

1. 阅读 [案例研究报告](case_study.md)
2. 查看 [审计仪表板](https://wzbxjb.github.io/agent-audit-case/)
3. 或: `python pipeline/evaluate.py` 一键运行审计

## 项目结构

```
pipeline/
  ├── evaluate.py           # 一键全流程入口
  ├── auditor.py            # 审计适配层（调用自研检测器）
  ├── scorer.py             # 加权评分 + Bootstrap CI
  └── detectors/            # 4 个自研检测引擎
      ├── hallucination.py  # 多模式幻觉检测
      ├── claim_checker.py  # 语义声明验证
      ├── structure.py      # 语义结构校验
      └── statistical.py    # 统计审计（Bootstrap + Kappa）
output/
  ├── agent_outputs/        # 4 Agent × 8 份营销内容
  ├── audit_results.json    # 审计结果（Phase 2）
  ├── evidence.json         # 品牌证据文件（7 真 + 3 假）
  └── brand_profile.json    # TechGlow 品牌设定
dashboard/
  └── index.html            # Chart.js 交互仪表板
case_study.md               # 完整案例研究报告
```
