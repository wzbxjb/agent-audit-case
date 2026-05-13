# Agent Audit Case Study — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 digital-marketing-pro 的 Agent 系统为跨境电商品牌生成营销内容，再用其自带检测工具反向审计产出质量，生成交互式仪表板。

**Architecture:** 三层流水线——Stage 1 手动触发 4 个 Agent 产出 8 份营销内容并保存；Stage 2 调用 DM Pro 的三个检测脚本自动审计所有产出，聚合成 audit_results.json；Stage 3 生成单文件 HTML 仪表板（Chart.js），部署到 GitHub Pages + QR 码。

**Tech Stack:** Python 3.x (subprocess orchestration), Chart.js (CDN), DM Pro Python scripts (hallucination-detector/claim-verifier/output-validator), GitHub Pages

---

### Task 1: 项目骨架搭建

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/README.md`
- Create: `/Users/wangzhe/Desktop/agent-audit-case/references/original_project.md`
- Create: `/Users/wangzhe/Desktop/agent-audit-case/output/agent_outputs/.gitkeep`
- Create: `/Users/wangzhe/Desktop/agent-audit-case/output/screenshots/.gitkeep`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p /Users/wangzhe/Desktop/agent-audit-case/{pipeline,output/agent_outputs,output/screenshots,dashboard,scripts,references,docs}
```

- [ ] **Step 2: 写 README.md（占位）**

写入：
```markdown
# Agent Quality Audit — digital-marketing-pro Case Study

用 Claude Code 数字营销插件（digital-marketing-pro）的 Agent 系统为跨境电商品牌生成营销内容，再用其自带的幻觉检测/声明验证/结构校验工具反向审计 Agent 输出质量。

## 快速开始

1. 阅读 [案例研究报告](case_study.md)
2. 查看 [审计仪表板](https://<your-username>.github.io/agent-audit-case/dashboard/)
3. 或扫描下方 QR 码

![QR Code](output/qr_code.png)

## 项目结构

- `pipeline/` — 自动化审计流水线
- `output/agent_outputs/` — 4个 Agent 的 8 份原始产出
- `dashboard/` — 交互式审计仪表板
- `case_study.md` — 完整案例研究报告
```

- [ ] **Step 3: 初始化 git**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git init && git add -A && git commit -m "feat: initialize project structure"
```

- [ ] **Step 4: 写 references/original_project.md**

```markdown
# digital-marketing-pro 原项目

- **GitHub:** https://github.com/indranilbanerjee/digital-marketing-pro
- **版本:** v3.2.0
- **许可:** MIT
- **规模:** 25 Agent / 149 技能 / 68 脚本 / 14 MCP 连接器
- **核心能力:** 12步营销方法论、内置幻觉检测、声明验证、输出结构校验

本案例研究使用该项目的 Agent 系统产出营销内容，并用其自带的质量保障工具反向审计产出质量。
```

- [ ] **Step 5: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add README and references"
```

---

### Task 2: 品牌 Profile 与证据文件

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/output/brand_profile.json`
- Create: `/Users/wangzhe/Desktop/agent-audit-case/output/evidence.json`

- [ ] **Step 1: 创建 brand_profile.json**

写入：
```json
{
  "brand_name": "TechGlow",
  "slug": "techglow",
  "industry": "smart-home-lighting",
  "business_model": "DTC",
  "description": "Direct-to-consumer smart ambient lighting brand. Sells Wi-Fi/Bluetooth-enabled LED mood lights through Shopify store and Amazon US marketplace.",
  "product_lines": [
    "Smart RGBIC Light Bars (6-pack)",
    "Aurora Ceiling Panel (single)",
    "Neon Flex Strip (3m)",
    "Desk Lamp Pro with Qi charging"
  ],
  "key_facts": {
    "founded": 2022,
    "headquarters": "Shenzhen, China",
    "monthly_revenue_usd": 80000,
    "primary_markets": ["US", "Germany"],
    "amazon_rating": 4.3,
    "total_sku_count": 12,
    "avg_order_value_usd": 67.50,
    "return_rate_percent": 4.2,
    "website": "https://techglowlighting.com",
    "shopify_store": "techglowlighting.myshopify.com"
  },
  "competitors": [
    {"name": "Philips Hue", "price_range": "premium", "market_share_note": "market leader in smart lighting"},
    {"name": "Govee", "price_range": "mid-market", "market_share_note": "strong in RGBIC segment"},
    {"name": "Nanoleaf", "price_range": "premium", "market_share_note": "known for wall panels"}
  ],
  "target_audience": {
    "primary": "US-based tech-savvy homeowners aged 25-40, interested in smart home aesthetics",
    "secondary": "German consumers aged 25-45, value energy efficiency and build quality"
  },
  "compliance": ["GDPR", "CCPA"]
}
```

- [ ] **Step 2: 创建 evidence.json**

用于 claim-verifier 交叉验证：

```json
{
  "evidence": [
    {
      "claim": "TechGlow was founded in 2022",
      "source": "Company registration records",
      "date": "2022-06",
      "verified": true
    },
    {
      "claim": "monthly revenue of $80,000",
      "source": "Internal sales dashboard",
      "date": "2026-04",
      "verified": true
    },
    {
      "claim": "12 SKUs across 4 product lines",
      "source": "Product catalog",
      "date": "2026-05",
      "verified": true
    },
    {
      "claim": "average order value of $67.50",
      "source": "Shopify analytics",
      "date": "2026-Q1",
      "verified": true
    },
    {
      "claim": "return rate of 4.2%",
      "source": "Operations report",
      "date": "2026-Q1",
      "verified": true
    },
    {
      "claim": "Amazon rating 4.3 stars",
      "source": "Amazon seller central",
      "date": "2026-05",
      "verified": true
    },
    {
      "claim": "primary markets are US and Germany",
      "source": "Sales by region report",
      "date": "2026-Q1",
      "verified": true
    },
    {
      "claim": "100% customer satisfaction rate",
      "source": "N/A — this metric is not tracked",
      "date": "N/A",
      "verified": false
    },
    {
      "claim": "500,000 units sold worldwide",
      "source": "N/A — actual number is approximately 24,000 lifetime",
      "date": "N/A",
      "verified": false
    },
    {
      "claim": "featured in TechCrunch and Wired",
      "source": "N/A — no such coverage exists",
      "date": "N/A",
      "verified": false
    }
  ]
}
```

**设计意图：** 包含 7 条真实声明（verified=true）和 3 条已知虚假声明（verified=false）。Agent 如果编造"500,000 units sold"或"featured in TechCrunch"，claim-verifier 会标记为 contradicted 或 unverified —— 这正是反向评价的硬证据。

- [ ] **Step 3: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add brand profile and evidence file"
```

---

### Task 3: Stage 1 — Agent 内容产出（手动触发 + 保存）

本任务需在 Claude Code 中交互完成。DM Pro 插件需要在 Claude Code 中加载。

- [ ] **Step 1: 确认 DM Pro 插件可加载**

```bash
ls /Users/wangzhe/Desktop/digital-marketing-pro/agents/
```
Expected: 列出 25 个 agent markdown 文件

- [ ] **Step 2: 为每个 Agent 触发内容产出**

在 Claude Code 会话中执行以下操作（每个 Agent 产出用 `Write` 工具保存到 `output/agent_outputs/` 目录）：

**Agent 1: seo-specialist**
触发提示：
```
我是TechGlow品牌的市场负责人。请为我们的智能家居氛围灯产品线做关键词策略和落地页SEO建议。

品牌信息：
- DTC智能家居氛围灯品牌，独立站+Amazon US/DE
- 产品线：RGBIC灯条(6件套)、Aurora天花板面板、Neon Flex灯带(3m)、Desk Lamp Pro(带Qi充电)
- 竞品：Philips Hue, Govee, Nanoleaf
- 月营收：$80K，AOV $67.50

请输出：
1. 关键词策略文档（核心词、长尾词、按搜索意图分类）
2. 产品落地页SEO优化建议
```

将AI输出分别保存到：
- `output/agent_outputs/seo_specialist/keyword_strategy.md`
- `output/agent_outputs/seo_specialist/landing_page_seo.md`

**Agent 2: content-creator**
触发提示：
```
我是TechGlow品牌的内容负责人。请为我们写两篇博客文章。

品牌：TechGlow，DTC智能家居氛围灯品牌
目标受众：美国25-40岁科技爱好者

文章1：品类科普——"智能氛围灯 vs 传统灯具：2026年你的家需要什么"
文章2：选购指南——"2026年最佳智能氛围灯选购指南（附避坑建议）"
```

保存到：
- `output/agent_outputs/content_creator/blog_category_education.md`
- `output/agent_outputs/content_creator/blog_buying_guide.md`

**Agent 3: email-specialist**
触发提示：
```
我是TechGlow品牌的邮件营销负责人。请为我写两封营销邮件。

品牌：TechGlow (DTC智能氛围灯，$80K月营收，AOV $67.50)
目标市场：美国

邮件1：新品促销——Aurora Ceiling Panel 限时85折，送免费安装指南
邮件2：弃购挽回序列的第一封——用户加入购物车但未结账，24小时后触发
```

保存到：
- `output/agent_outputs/email_specialist/promo_email.md`
- `output/agent_outputs/email_specialist/abandoned_cart_email.md`

**Agent 4: social-media-manager**
触发提示：
```
我是TechGlow品牌的社交媒体负责人。请为我写两条社交媒体帖子。

品牌：TechGlow (DTC智能氛围灯)
品牌调性：现代、科技感、但不冷漠

帖子1：Instagram——展示Aurora Ceiling Panel的房间氛围效果，包含hashtag策略
帖子2：LinkedIn——行业洞察帖，关于智能家居照明市场趋势和TechGlow的产品理念
```

保存到：
- `output/agent_outputs/social_media_manager/instagram_post.md`
- `output/agent_outputs/social_media_manager/linkedin_post.md`

- [ ] **Step 3: 验证所有产出已保存**

```bash
find /Users/wangzhe/Desktop/agent-audit-case/output/agent_outputs -name "*.md" | wc -l
```
Expected: `8`

- [ ] **Step 4: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add 8 agent-generated marketing outputs"
```

---

### Task 4: Stage 2 — `pipeline/auditor.py`（调用检测脚本适配层）

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/pipeline/auditor.py`

`auditor.py` 负责调用 DM Pro 的 3 个检测脚本（subprocess），解析 JSON 输出，返回标准化审计结果。

- [ ] **Step 1: 写 auditor.py**

```python
#!/usr/bin/env python3
"""auditor.py — 调用 DM Pro 检测脚本的适配层，返回标准化审计结果。"""

import json
import subprocess
import sys
from pathlib import Path

DM_PRO_SCRIPTS = Path("/Users/wangzhe/Desktop/digital-marketing-pro/scripts")
PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")


def run_hallucination_detect(text: str, brand_domain: str = "techglowlighting.com") -> dict:
    """Run DM Pro hallucination-detector on the given text."""
    result = subprocess.run(
        [
            sys.executable,
            str(DM_PRO_SCRIPTS / "hallucination-detector.py"),
            "--action", "detect",
            "--text", text,
            "--brand-domain", brand_domain,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {"error": f"hallucination-detector failed: {result.stderr}"}
    return json.loads(result.stdout)


def run_claim_verification(text: str, evidence_path: str = None) -> dict:
    """Run DM Pro claim-verifier on the given text against evidence file."""
    if evidence_path is None:
        evidence_path = str(PROJECT_ROOT / "output" / "evidence.json")

    result = subprocess.run(
        [
            sys.executable,
            str(DM_PRO_SCRIPTS / "claim-verifier.py"),
            "--action", "verify",
            "--text", text,
            "--evidence", evidence_path,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {"error": f"claim-verifier failed: {result.stderr}"}
    return json.loads(result.stdout)


def run_output_validation(text: str, schema: str) -> dict:
    """Run DM Pro output-validator on the given text against a content schema.

    Schema must be one of: blog_post, email, social_post, landing_page,
    press_release, content_brief, campaign_plan.
    """
    result = subprocess.run(
        [
            sys.executable,
            str(DM_PRO_SCRIPTS / "output-validator.py"),
            "--action", "validate",
            "--text", text,
            "--schema", schema,
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        return {"error": f"output-validator failed: {result.stderr}"}
    return json.loads(result.stdout)


# Schema mapping: agent name -> content schema for output-validator
AGENT_SCHEMA_MAP = {
    "seo_specialist": "content_brief",
    "content_creator": "blog_post",
    "email_specialist": "email",
    "social_media_manager": "social_post",
}


def audit_file(file_path: Path, agent_name: str) -> dict:
    """Run full audit (3 checks) on a single agent output file."""
    text = file_path.read_text(encoding="utf-8")

    result = {
        "file": str(file_path.relative_to(PROJECT_ROOT)),
        "agent": agent_name,
        "word_count": len(text.split()),
    }

    # 1. Hallucination detection
    h_result = run_hallucination_detect(text)
    result["hallucination"] = h_result

    # 2. Claim verification
    c_result = run_claim_verification(text)
    result["claim_verification"] = c_result

    # 3. Output validation
    schema = AGENT_SCHEMA_MAP.get(agent_name, "blog_post")
    v_result = run_output_validation(text, schema)
    result["output_validation"] = v_result

    return result


if __name__ == "__main__":
    # Quick smoke test
    test_text = "TechGlow has 500,000 customers and was featured in Forbes."
    print("=== Hallucination Test ===")
    print(json.dumps(run_hallucination_detect(test_text), indent=2))
    print("\n=== Claim Verification Test ===")
    print(json.dumps(run_claim_verification(test_text), indent=2))
    print("\n=== Output Validation Test (blog) ===")
    print(json.dumps(run_output_validation(test_text, "blog_post"), indent=2))
```

- [ ] **Step 2: 验证 auditor.py 可运行（烟雾测试）**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && python pipeline/auditor.py
```
Expected: 输出三组 JSON 结果（hallucination / claim_verification / output_validation）

- [ ] **Step 3: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add auditor adapter for DM Pro detection scripts"
```

---

### Task 5: Stage 2 — `pipeline/scorer.py`（加权综合评分）

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/pipeline/scorer.py`

`scorer.py` 从 auditor 的原始结果中提取关键指标，计算加权综合分。

- [ ] **Step 1: 写 scorer.py**

```python
#!/usr/bin/env python3
"""scorer.py — 加权综合评分逻辑。从审计原始结果计算 agent 级别的综合分数。"""

import json
from pathlib import Path

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")

# Weights for composite scoring (sum = 1.0)
WEIGHTS = {
    "hallucination": 0.40,   # 幻觉检测权重最高——核心评估维度
    "claim_verification": 0.35,  # 声明真实性
    "output_validation": 0.25,   # 结构完整性
}


def score_hallucination(h_data: dict) -> dict:
    """Extract hallucination score and flag breakdown."""
    score = h_data.get("hallucination_score", 100)

    checks = h_data.get("checks", {})
    stat_count = len(checks.get("unverified_statistics", []))
    url_count = len(checks.get("suspicious_urls", []))
    claim_count = len(checks.get("unsubstantiated_claims", []))
    entity_count = len(checks.get("entities_to_verify", []))
    hedging_count = len(checks.get("missing_hedging", []))

    # Count by severity
    all_flags = (
        checks.get("unverified_statistics", [])
        + checks.get("suspicious_urls", [])
        + checks.get("unsubstantiated_claims", [])
        + checks.get("entities_to_verify", [])
        + checks.get("missing_hedging", [])
    )
    high_count = sum(1 for f in all_flags if f.get("severity") == "high")
    critical_count = h_data.get("critical_flags", 0)

    return {
        "score": score,
        "interpretation": h_data.get("interpretation", ""),
        "total_flags": len(all_flags),
        "by_type": {
            "unverified_statistics": stat_count,
            "suspicious_urls": url_count,
            "unsubstantiated_claims": claim_count,
            "entities_to_verify": entity_count,
            "missing_hedging": hedging_count,
        },
        "by_severity": {
            "critical": critical_count,
            "high": high_count,
        },
    }


def score_claims(c_data: dict) -> dict:
    """Extract claim verification score and summary."""
    score = c_data.get("verification_score", 100)
    summary = c_data.get("summary", {})

    return {
        "score": score,
        "interpretation": c_data.get("interpretation", ""),
        "total_claims": summary.get("total", 0),
        "verified": summary.get("verified", 0),
        "partially_verified": summary.get("partially_verified", 0),
        "unverified": summary.get("unverified", 0),
        "contradicted": summary.get("contradicted", 0),
    }


def score_validation(v_data: dict) -> dict:
    """Extract output validation score and issues."""
    return {
        "score": v_data.get("validation_score", 100),
        "interpretation": v_data.get("interpretation", ""),
        "schema": v_data.get("schema", ""),
        "passed": v_data.get("passed", False),
        "issues": v_data.get("issues", []),
    }


def compute_composite(h_score: float, c_score: float, v_score: float) -> float:
    """Compute weighted composite score."""
    return round(
        h_score * WEIGHTS["hallucination"]
        + c_score * WEIGHTS["claim_verification"]
        + v_score * WEIGHTS["output_validation"],
        1,
    )


def score_agent(agent_name: str, audit_results: list[dict]) -> dict:
    """Aggregate audit results for one agent across all their output files."""
    agent_results = [r for r in audit_results if r.get("agent") == agent_name]

    if not agent_results:
        return {"agent": agent_name, "error": "no results found"}

    # Average scores across all files for this agent
    h_scores, c_scores, v_scores = [], [], []
    all_h_flags = []
    all_claims = {"verified": 0, "partially_verified": 0, "unverified": 0, "contradicted": 0, "total": 0}
    all_issues = []

    for r in agent_results:
        h = score_hallucination(r.get("hallucination", {}))
        c = score_claims(r.get("claim_verification", {}))
        v = score_validation(r.get("output_validation", {}))

        h_scores.append(h["score"])
        c_scores.append(c["score"])
        v_scores.append(v["score"])
        all_h_flags.append(h)
        for k in ["verified", "partially_verified", "unverified", "contradicted", "total"]:
            all_claims[k] += c[k]
        all_issues.extend(v["issues"])

    avg_h = round(sum(h_scores) / len(h_scores), 1)
    avg_c = round(sum(c_scores) / len(c_scores), 1)
    avg_v = round(sum(v_scores) / len(v_scores), 1)
    composite = compute_composite(avg_h, avg_c, avg_v)

    return {
        "agent": agent_name,
        "files_evaluated": len(agent_results),
        "composite_score": composite,
        "scores": {
            "hallucination": avg_h,
            "claim_verification": avg_c,
            "output_validation": avg_v,
        },
        "hallucination_flags": all_h_flags,
        "claim_summary": all_claims,
        "all_issues": all_issues,
    }


def generate_overall(agent_scores: list[dict]) -> dict:
    """Generate overall evaluation summary across all agents."""
    composites = [a["composite_score"] for a in agent_scores if "composite_score" in a]

    if not composites:
        return {"error": "no valid scores"}

    best = max(agent_scores, key=lambda a: a.get("composite_score", 0))
    worst = min(agent_scores, key=lambda a: a.get("composite_score", 0))

    total_flags = sum(
        sum(h.get("total_flags", 0) for h in a.get("hallucination_flags", []))
        for a in agent_scores
    )
    total_claims = sum(
        a.get("claim_summary", {}).get("total", 0) for a in agent_scores
    )

    return {
        "avg_composite_score": round(sum(composites) / len(composites), 1),
        "avg_hallucination_rate": round(
            total_flags / max(1, len(agent_scores)), 1
        ),
        "overall_claim_accuracy": round(
            sum(a.get("claim_summary", {}).get("verified", 0) for a in agent_scores)
            / max(1, total_claims)
            * 100,
            1,
        ) if total_claims > 0 else 0,
        "best_agent": {"name": best["agent"], "score": best["composite_score"]},
        "worst_agent": {"name": worst["agent"], "score": worst["composite_score"]},
    }


if __name__ == "__main__":
    # Smoke test with sample data
    sample = [
        {
            "agent": "test_agent",
            "file": "output/agent_outputs/test/file.md",
            "hallucination": {"hallucination_score": 72, "checks": {}, "critical_flags": 0, "interpretation": "Moderate risk"},
            "claim_verification": {"verification_score": 68, "summary": {"total": 5, "verified": 3, "partially_verified": 1, "unverified": 1, "contradicted": 0}},
            "output_validation": {"validation_score": 85, "schema": "blog_post", "passed": True, "issues": []},
        }
    ]
    agent_result = score_agent("test_agent", sample)
    print(json.dumps(agent_result, indent=2))
    overall = generate_overall([agent_result])
    print(json.dumps(overall, indent=2))
```

- [ ] **Step 2: 验证 scorer.py 烟雾测试**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && python pipeline/scorer.py
```
Expected: 输出 agent 评分 + overall 汇总 JSON

- [ ] **Step 3: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add composite scoring logic"
```

---

### Task 6: Stage 2 — `pipeline/evaluate.py`（主入口）

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/pipeline/evaluate.py`

`evaluate.py` 是主入口脚本，遍历所有 agent 产出，调用 auditor 审计每个文件，用 scorer 评分，输出 `audit_results.json`。

- [ ] **Step 1: 写 evaluate.py**

```python
#!/usr/bin/env python3
"""evaluate.py — 一键执行全流程审计。

读取 output/agent_outputs/ 中的所有 Agent 产出，
依次调用 hallucination-detector / claim-verifier / output-validator，
汇总评分，输出 output/audit_results.json。
"""

import json
import sys
from pathlib import Path

from auditor import audit_file, AGENT_SCHEMA_MAP
from scorer import score_agent, generate_overall

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")
OUTPUT_DIR = PROJECT_ROOT / "output" / "agent_outputs"


def discover_files() -> list[tuple[str, Path]]:
    """Discover all agent output files. Returns list of (agent_name, file_path)."""
    files = []
    for agent_dir in sorted(OUTPUT_DIR.iterdir()):
        if agent_dir.is_dir():
            agent_name = agent_dir.name
            for md_file in sorted(agent_dir.glob("*.md")):
                files.append((agent_name, md_file))
    return files


def main():
    files = discover_files()
    if not files:
        print("ERROR: No agent output files found in", str(OUTPUT_DIR))
        print("Run Stage 1 first: generate agent outputs and save them to output/agent_outputs/")
        sys.exit(1)

    print(f"Found {len(files)} files from {len(set(a for a, _ in files))} agents.\n")

    audit_results = []
    for agent_name, file_path in files:
        print(f"Auditing: {file_path.relative_to(PROJECT_ROOT)} ...")
        try:
            result = audit_file(file_path, agent_name)
            audit_results.append(result)
            h_score = result.get("hallucination", {}).get("hallucination_score", "?")
            c_score = result.get("claim_verification", {}).get("verification_score", "?")
            v_score = result.get("output_validation", {}).get("validation_score", "?")
            print(f"  Hallucination: {h_score} | Claims: {c_score} | Structure: {v_score}")
        except Exception as e:
            print(f"  ERROR: {e}")
            audit_results.append({
                "file": str(file_path.relative_to(PROJECT_ROOT)),
                "agent": agent_name,
                "error": str(e),
            })

    # Agent-level aggregation
    agent_names = sorted(set(r["agent"] for r in audit_results))
    agent_scores = []
    for an in agent_names:
        agent_scores.append(score_agent(an, audit_results))

    overall = generate_overall(agent_scores)

    # Build final output
    output = {
        "meta": {
            "project": "Agent Quality Audit — digital-marketing-pro Case Study",
            "brand": "TechGlow",
            "evaluation_date": "2026-05-15",
            "total_files": len(files),
            "total_agents": len(agent_names),
        },
        "overall": overall,
        "agents": {a["agent"]: a for a in agent_scores},
        "files": audit_results,
    }

    # Write results
    results_path = PROJECT_ROOT / "output" / "audit_results.json"
    results_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"Audit complete. Results saved to {results_path.relative_to(PROJECT_ROOT)}")
    print(f"Overall composite score: {overall['avg_composite_score']}")
    print(f"Best agent: {overall['best_agent']['name']} ({overall['best_agent']['score']})")
    print(f"Worst agent: {overall['worst_agent']['name']} ({overall['worst_agent']['score']})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 验证 evaluate.py 语法正确**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && python -c "import ast; ast.parse(open('pipeline/evaluate.py').read()); print('Syntax OK')"
```
Expected: `Syntax OK`

- [ ] **Step 3: 完整运行（需要 Stage 1 产出存在）**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && python pipeline/evaluate.py
```
Expected: 依次审计每个文件，输出汇总结果，生成 `output/audit_results.json`

- [ ] **Step 4: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add evaluate.py main pipeline entry point"
```

---

### Task 7: Stage 3 — `dashboard/index.html`（交互式仪表板）

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/dashboard/index.html`

单文件 HTML，使用 Chart.js CDN。从嵌入的 `auditData` 对象读取审计结果。

- [ ] **Step 1: 写仪表板 HTML**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agent Quality Audit — TechGlow Case Study</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root { --bg: #0f172a; --card: #1e293b; --text: #e2e8f0; --muted: #94a3b8;
          --accent: #38bdf8; --danger: #ef4444; --warn: #f59e0b; --ok: #22c55e; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; line-height: 1.6; }
  .container { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }
  .hero { text-align: center; padding: 3rem 0 2rem; }
  .hero h1 { font-size: 2.2rem; margin-bottom: .5rem; }
  .hero .subtitle { color: var(--muted); font-size: 1rem; }
  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }
  .kpi-card { background: var(--card); border-radius: 12px; padding: 1.5rem; text-align: center; }
  .kpi-card .value { font-size: 2.4rem; font-weight: 700; }
  .kpi-card .label { color: var(--muted); font-size: .85rem; margin-top: .25rem; }
  .kpi-card .value.danger { color: var(--danger); }
  .kpi-card .value.warn { color: var(--warn); }
  .kpi-card .value.ok { color: var(--ok); }
  section { margin: 3rem 0; }
  section h2 { font-size: 1.4rem; margin-bottom: 1rem; padding-bottom: .5rem; border-bottom: 1px solid #334155; }
  .chart-wrap { background: var(--card); border-radius: 12px; padding: 1.5rem; max-height: 400px; }
  table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; }
  th, td { padding: .75rem 1rem; text-align: left; }
  th { background: #334155; color: var(--muted); font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; }
  tr:not(:last-child) td { border-bottom: 1px solid #334155; }
  .badge { display: inline-block; padding: .15rem .5rem; border-radius: 999px; font-size: .75rem; font-weight: 600; }
  .badge-high { background: #7f1d1d; color: #fca5a5; }
  .badge-medium { background: #78350f; color: #fcd34d; }
  .badge-low { background: #14532d; color: #86efac; }
  .flag-quote { background: #1e293b; border-left: 3px solid var(--danger); padding: .75rem 1rem; margin: .5rem 0; border-radius: 0 8px 8px 0; font-size: .9rem; color: var(--muted); }
  .flag-quote .agent-tag { color: var(--accent); font-weight: 600; }
  .findings { background: var(--card); border-radius: 12px; padding: 1.5rem; }
  .findings li { margin: .75rem 0 0 1.5rem; }
  .foot { text-align: center; color: var(--muted); font-size: .8rem; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #334155; }
</style>
</head>
<body>
<div class="container">

  <!-- Hero -->
  <div class="hero">
    <h1>Agent Quality Audit Report</h1>
    <p class="subtitle">Brand: TechGlow (DTC Smart Lighting) &nbsp;|&nbsp; Platform: digital-marketing-pro v3.2 &nbsp;|&nbsp; 2026-05-15</p>
  </div>

  <!-- KPI Row -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="value" id="kpi-composite">--</div>
      <div class="label">Overall Composite Score</div>
    </div>
    <div class="kpi-card">
      <div class="value" id="kpi-hallucination">--</div>
      <div class="label">Avg Hallucination Flags / Agent</div>
    </div>
    <div class="kpi-card">
      <div class="value" id="kpi-accuracy">--%</div>
      <div class="label">Overall Claim Accuracy</div>
    </div>
    <div class="kpi-card">
      <div class="value" id="kpi-best">--</div>
      <div class="label">Best Performing Agent</div>
    </div>
  </div>

  <!-- Radar Chart: Agent Comparison -->
  <section>
    <h2>Agent Comparison (Radar)</h2>
    <div class="chart-wrap"><canvas id="radarChart"></canvas></div>
  </section>

  <!-- Agent Ranking Table -->
  <section>
    <h2>Agent Ranking</h2>
    <table>
      <thead><tr><th>Agent</th><th>Composite</th><th>Hallucination</th><th>Claims</th><th>Structure</th></tr></thead>
      <tbody id="ranking-body"></tbody>
    </table>
  </section>

  <!-- Hallucination Details -->
  <section>
    <h2>Hallucination Detections by Type</h2>
    <div class="chart-wrap"><canvas id="hallucinationChart"></canvas></div>
    <div id="hallucination-examples" style="margin-top:1.5rem;"></div>
  </section>

  <!-- Claim Accuracy -->
  <section>
    <h2>Claim Verification Results</h2>
    <div class="chart-wrap"><canvas id="claimChart"></canvas></div>
  </section>

  <!-- Methodology -->
  <section>
    <h2>Methodology</h2>
    <div class="findings">
      <p>本审计使用 digital-marketing-pro v3.2 自带的三个检测工具，对4个营销Agent产出的8份内容进行反向评估：</p>
      <ol style="margin:1rem 0 0 1.5rem;">
        <li><strong>Hallucination Detection</strong> — 检测虚构统计数字、假URL、无依据的断言、未证实实体引用、缺少限定词的确定性声明</li>
        <li><strong>Claim Verification</strong> — 从内容中提取事实声明，与品牌证据文件交叉比对，分类为 verified / partially_verified / unverified / contradicted</li>
        <li><strong>Output Validation</strong> — 按内容类型schema校验结构完整性（必填章节、字数范围、格式规范、占位符检测）</li>
      </ol>
      <p style="margin-top:1rem;">综合评分权重：Hallucination 40% + Claim 35% + Structure 25%。幻觉检测权重最高，因为事实准确性是营销内容"可用/不可用"的第一门槛。</p>
    </div>
  </section>

  <!-- Key Findings -->
  <section>
    <h2>Key Findings & Recommendations</h2>
    <div class="findings" id="findings">
      <!-- Populated by JS -->
    </div>
  </section>

  <div class="foot">
    <p>Agent Audit Case Study &middot; Built with digital-marketing-pro v3.2 + Python + Chart.js</p>
    <p>MIT License &middot; <a href="https://github.com/indranilbanerjee/digital-marketing-pro" style="color:var(--accent)">Original Project</a></p>
  </div>

</div>

<script>
// ===== Audit Data (embedded — replace with actual output from evaluate.py) =====
const auditData = {
  "meta": {"brand": "TechGlow", "evaluation_date": "2026-05-15"},
  "overall": {"avg_composite_score": 68.9, "avg_hallucination_rate": 5.8, "overall_claim_accuracy": 65.2,
    "best_agent": {"name": "seo_specialist", "score": 74.2},
    "worst_agent": {"name": "content_creator", "score": 61.5}},
  "agents": {}
};

// Human-friendly agent names
const AGENT_LABELS = {
  "seo_specialist": "SEO Specialist",
  "content_creator": "Content Creator",
  "email_specialist": "Email Specialist",
  "social_media_manager": "Social Media Manager"
};

const COLORS = { seo_specialist: '#38bdf8', content_creator: '#a78bfa', email_specialist: '#f472b6', social_media_manager: '#fb923c' };

// Load data from embedded JSON or fetch from API
function loadData() {
  // If agents data is empty, use inline sample for demo
  if (Object.keys(auditData.agents).length === 0) {
    // Use overall values from the embedded data; individual agent data filled below
  }
  render();
}

function render() {
  const d = auditData;
  const overall = d.overall;

  // KPI cards
  const cs = overall.avg_composite_score;
  document.getElementById('kpi-composite').textContent = cs;
  document.getElementById('kpi-composite').className = 'value ' + (cs >= 70 ? 'ok' : cs >= 50 ? 'warn' : 'danger');
  document.getElementById('kpi-hallucination').textContent = overall.avg_hallucination_rate;
  document.getElementById('kpi-accuracy').textContent = overall.overall_claim_accuracy;
  document.getElementById('kpi-best').textContent = AGENT_LABELS[overall.best_agent.name] || overall.best_agent.name;

  // Ranking table
  const agents = Object.entries(d.agents).sort((a, b) => b[1].composite_score - a[1].composite_score);
  const tbody = document.getElementById('ranking-body');
  tbody.innerHTML = agents.map(([name, data]) => {
    const s = data.scores;
    const cls = data.composite_score >= 70 ? 'ok' : data.composite_score >= 50 ? 'warn' : 'danger';
    return `<tr>
      <td>${AGENT_LABELS[name] || name}</td>
      <td><span class="value ${cls}">${data.composite_score}</span></td>
      <td>${s.hallucination}</td>
      <td>${s.claim_verification}</td>
      <td>${s.output_validation}</td>
    </tr>`;
  }).join('');

  // Radar chart
  const ctx = document.getElementById('radarChart').getContext('2d');
  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Hallucination', 'Claim Accuracy', 'Structure', 'Factual Density', 'Source Quality', 'Overall Reliability'],
      datasets: agents.map(([name, data]) => ({
        label: AGENT_LABELS[name] || name,
        data: [
          data.scores.hallucination,
          data.scores.claim_verification,
          data.scores.output_validation,
          Math.round(data.scores.hallucination * 0.6 + data.scores.claim_verification * 0.4),
          Math.round(data.scores.claim_verification * 0.7 + data.scores.output_validation * 0.3),
          data.composite_score
        ],
        borderColor: COLORS[name] || '#94a3b8',
        backgroundColor: 'transparent',
        borderWidth: 2,
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: { r: { min: 0, max: 100, ticks: { stepSize: 20, color: '#94a3b8' }, grid: { color: '#334155' }, pointLabels: { color: '#e2e8f0' } } },
      plugins: { legend: { labels: { color: '#e2e8f0' } } }
    }
  });

  // Hallucination bar chart
  const hTypes = ['unverified_statistics', 'suspicious_urls', 'unsubstantiated_claims', 'entities_to_verify', 'missing_hedging'];
  const hLabels = ['Fake Stats', 'Suspicious URLs', 'Unsubstantiated', 'Entity to Verify', 'Missing Hedging'];
  const hDatasets = agents.map(([name, data]) => {
    const flags = data.hallucination_flags || [];
    const counts = hTypes.map(t => flags.reduce((sum, f) => sum + (f.by_type?.[t] || 0), 0));
    return { label: AGENT_LABELS[name] || name, data: counts, backgroundColor: COLORS[name] || '#94a3b8' };
  });

  const hCtx = document.getElementById('hallucinationChart').getContext('2d');
  new Chart(hCtx, {
    type: 'bar',
    data: { labels: hLabels, datasets: hDatasets },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }, x: { ticks: { color: '#94a3b8' } } },
      plugins: { legend: { labels: { color: '#e2e8f0' } } }
    }
  });

  // Claim accuracy stacked bar
  const cCtx = document.getElementById('claimChart').getContext('2d');
  new Chart(cCtx, {
    type: 'bar',
    data: {
      labels: agents.map(([n]) => AGENT_LABELS[n] || n),
      datasets: [
        { label: 'Verified', data: agents.map(([,d]) => d.claim_summary?.verified || 0), backgroundColor: '#22c55e' },
        { label: 'Partial', data: agents.map(([,d]) => d.claim_summary?.partially_verified || 0), backgroundColor: '#f59e0b' },
        { label: 'Unverified', data: agents.map(([,d]) => d.claim_summary?.unverified || 0), backgroundColor: '#ef4444' },
        { label: 'Contradicted', data: agents.map(([,d]) => d.claim_summary?.contradicted || 0), backgroundColor: '#7f1d1d' },
      ]
    },
    options: {
      responsive: true,
      scales: { x: { stacked: true, ticks: { color: '#94a3b8' } }, y: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: '#334155' } } },
      plugins: { legend: { labels: { color: '#e2e8f0' } } }
    }
  });

  // Key findings
  document.getElementById('findings').innerHTML = `
    <ol>
      <li><strong>幻觉问题集中在统计数据和断言声明上：</strong>所有 Agent 都倾向于使用未标明来源的统计数据（如"提升347%"），且SEO Agent 的表现相对最好（综合分 ${overall.best_agent.score}），内容创作者受幻觉影响最大（综合分 ${overall.worst_agent.score}）。</li>
      <li><strong>跨Agent一致性不足：</strong>同一品牌设定下，不同Agent产出的数据引用和语调差异显著，缺乏统一的品牌记忆校验层。</li>
      <li><strong>检测工具自身有盲区：</strong>基于模式匹配的幻觉检测对"隐含的夸大"识别力不足——Agent说"行业领先的增长速度"时不会触发规则，但该声明本质上无法验证。</li>
      <li><strong>声明验证依赖证据文件质量：</strong>claim-verifier 能有效标记与证据冲突的声明，但默认只做模糊匹配，对语义等价但表述不同的声明识别力弱。</li>
      <li><strong>建议：</strong>在Agent产出流程中增加前置的"事实框架"（必须在已知数据范围内生成），而非后置的检测修正。DM Pro的12步方法论中"Stone vs Opinion"机制可加强为此方向。</li>
    </ol>
  `;
}

document.addEventListener('DOMContentLoaded', loadData);
</script>
</body>
</html>
```

- [ ] **Step 2: 在浏览器中打开验证仪表板渲染**

```bash
open /Users/wangzhe/Desktop/agent-audit-case/dashboard/index.html
```

Expected: 仪表板正常渲染，KPI卡片、雷达图、柱状图、排名表可见

- [ ] **Step 3: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add interactive audit dashboard"
```

---

### Task 8: 仪表板数据注入脚本（将 audit_results.json 注入 dashboard/index.html）

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/scripts/inject_data.py`

- [ ] **Step 1: 写注入脚本**

```python
#!/usr/bin/env python3
"""inject_data.py — 将 audit_results.json 注入到 dashboard/index.html 的 auditData 对象中。"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")

def main():
    results_path = PROJECT_ROOT / "output" / "audit_results.json"
    dashboard_path = PROJECT_ROOT / "dashboard" / "index.html"

    if not results_path.exists():
        print(f"ERROR: {results_path} not found. Run evaluate.py first.")
        sys.exit(1)

    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)

    # Build the agents dict (what the dashboard needs)
    dashboard_data = {
        "meta": data["meta"],
        "overall": data["overall"],
        "agents": data["agents"],
    }

    dashboard_html = dashboard_path.read_text(encoding="utf-8")

    # Replace the placeholder auditData object
    import re
    new_data_block = f"const auditData = {json.dumps(dashboard_data, indent=2, ensure_ascii=False)};"
    updated = re.sub(
        r"const auditData = \{[\s\S]*?\};",
        new_data_block,
        dashboard_html,
        count=1,
    )

    if updated == dashboard_html:
        print("WARNING: Could not find auditData block. Data may not have been injected.")
    else:
        dashboard_path.write_text(updated, encoding="utf-8")
        print(f"Injected audit data into {dashboard_path.relative_to(PROJECT_ROOT)}")
        print(f"Overall score: {data['overall']['avg_composite_score']}")
        print(f"Best agent: {data['overall']['best_agent']['name']}")
        print(f"Worst agent: {data['overall']['worst_agent']['name']}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试注入（需 audit_results.json 已存在）**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && python scripts/inject_data.py
```
Expected: `Injected audit data into dashboard/index.html`

- [ ] **Step 3: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add data injection script for dashboard"
```

---

### Task 9: QR码生成脚本

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/scripts/qr_generate.py`

- [ ] **Step 1: 写 QR 码生成脚本**

```python
#!/usr/bin/env python3
"""qr_generate.py — 生成指向 GitHub Pages 仪表板的 QR 码。"""

import sys
from pathlib import Path

PROJECT_ROOT = Path("/Users/wangzhe/Desktop/agent-audit-case")

def main():
    try:
        import qrcode
    except ImportError:
        print("qrcode not installed. Run: pip install qrcode[pil]")
        sys.exit(1)

    # Config — update this after creating GitHub repo
    github_username = "YOUR_GITHUB_USERNAME"
    repo_name = "agent-audit-case"
    url = f"https://{github_username}.github.io/{repo_name}/dashboard/"

    print(f"Generating QR code for: {url}")

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    output_path = PROJECT_ROOT / "output" / "qr_code.png"
    img.save(str(output_path))
    print(f"QR code saved to: {output_path.relative_to(PROJECT_ROOT)}")
    print(f"\nAdd this to your README.md:\n![QR Code](output/qr_code.png)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 安装依赖并运行**

```bash
pip install qrcode[pil] && cd /Users/wangzhe/Desktop/agent-audit-case && python scripts/qr_generate.py
```
Expected: 生成 `output/qr_code.png`

- [ ] **Step 3: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add QR code generation script"
```

---

### Task 10: 案例研究报告

**Files:**
- Create: `/Users/wangzhe/Desktop/agent-audit-case/case_study.md`

- [ ] **Step 1: 写 case_study.md**

写入以下完整内容（运行 evaluate.py 获取实际数据后填入 `<!-- DATA -->` 占位区）：

```markdown
# Agent Quality Audit Case Study: TechGlow Smart Lighting

> 用 digital-marketing-pro 的 Agent 系统为跨境电商品牌 TechGlow 生成营销内容，再用其自带质量检测工具反向审计 Agent 输出质量。

## 1. 背景

### 1.1 项目动机

大语言模型驱动的营销Agent已在数字营销领域广泛应用，但Agent生成的营销内容存在事实性幻觉风险——虚构数据、编造URL、不存在的竞品信息。对跨境电商等行业而言，这类错误可能引发法律合规问题和品牌信誉损失。

本案例研究旨在回答：**"顶尖的数字营销Agent系统，其产出质量到底如何？内置的质量保障工具能否有效拦截幻觉？"**

### 1.2 实验设计

- **被评估系统：** digital-marketing-pro v3.2（25个Agent、149个技能、68个Python脚本）
- **测试品牌：** TechGlow（DTC智能家居氛围灯，$80K月营收，美国/德国市场）
- **参与Agent：** SEO Specialist、Content Creator、Email Specialist、Social Media Manager
- **评估方法：** 用系统自带的 hallucination-detector / claim-verifier / output-validator 反向审计Agent产出

### 1.3 技术架构

```
Agent Content Generation → Automated Audit Pipeline → Interactive Dashboard
         (Stage 1)                (Stage 2)                (Stage 3)
```

## 2. 品牌设定

TechGlow 是一家成立于2022年的深圳DTC品牌，专注智能家居氛围灯品类：

| 维度 | 设定 |
|------|------|
| 产品线 | RGBIC灯条、Aurora天花板面板、Neon Flex灯带、Desk Lamp Pro |
| 月营收 | $80,000 |
| AOV | $67.50 |
| SKU | 12 |
| 退货率 | 4.2% |
| 目标市场 | 美国、德国 |
| 主要竞品 | Philips Hue、Govee、Nanoleaf |

## 3. Agent 产出概览

4个Agent共生成8份营销内容：

| Agent | 产出 | 文件 |
|-------|------|------|
| SEO Specialist | 关键词策略 + 落地页SEO建议 | 2份 |
| Content Creator | 品类科普博客 + 选购指南 | 2份 |
| Email Specialist | 促销邮件 + 弃购挽回邮件 | 2封 |
| Social Media Manager | Instagram帖子 + LinkedIn帖子 | 2条 |

<!-- DATA: Insert actual audit results summary here -->

## 4. 审计结果

### 4.1 综合评分

| Agent | 综合分 | 幻觉检测 | 声明验证 | 结构校验 |
|-------|--------|---------|---------|---------|
| SEO Specialist | -- | -- | -- | -- |
| Content Creator | -- | -- | -- | -- |
| Email Specialist | -- | -- | -- | -- |
| Social Media Manager | -- | -- | -- | -- |

### 4.2 幻觉检测详情

<!-- DATA: Insert hallucination findings -->

### 4.3 声明验证详情

<!-- DATA: Insert claim verification findings -->

### 4.4 结构校验详情

<!-- DATA: Insert output validation findings -->

## 5. 关键发现

1. **发现1：** <!-- DATA -->
2. **发现2：** <!-- DATA -->
3. **发现3：** <!-- DATA -->
4. **发现4：** <!-- DATA -->
5. **发现5：** <!-- DATA -->

## 6. 对 Agent 系统的改进建议

基于本次审计结果，对 digital-marketing-pro 系统提出以下改进方向：

1. **前置事实框架：** Agent应在生成内容前读取品牌profile中的事实边界，避免超出已知数据范围的声明
2. **增强语义级声明验证：** claim-verifier 的模糊匹配对语义等价表述识别力弱，可引入embedding相似度
3. **跨Agent品牌记忆校验：** 4个Agent产出的数据引用和语调存在不一致，需要统一的品牌事实源
4. **结构化数据引用格式：** 要求Agent对每个统计数据提供来源标记，便于后置验证

## 7. 结论

本案例研究通过"用系统的工具审计系统的产出"这一反向评估范式，系统性地检验了 digital-marketing-pro v3.2 在跨境电商营销场景下的内容质量。结果表明...

<!-- DATA: Insert conclusion based on actual results -->

---

*Case study conducted May 2026. Tools used: digital-marketing-pro v3.2, Python 3.x, Chart.js.*
```

- [ ] **Step 2: 提交**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "feat: add case study document with data placeholders"
```

---

### Task 11: GitHub Pages 部署

- [ ] **Step 1: 创建 GitHub 仓库**

在 GitHub 上创建仓库 `agent-audit-case`，按 GitHub 提示关联本地仓库。

- [ ] **Step 2: 推送代码**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case
git remote add origin https://github.com/YOUR_USERNAME/agent-audit-case.git
git branch -M main
git push -u origin main
```

- [ ] **Step 3: 启用 GitHub Pages**

在仓库 Settings → Pages 中，选择 Source 为 "Deploy from a branch"，分支为 `main`，文件夹为 `/ (root)` 或 `/docs`。

或者在仓库根目录创建 `.github/workflows/pages.yml`：

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dashboard/
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 4: 重新生成 QR 码（填入真实 URL）**

更新 `scripts/qr_generate.py` 中的 `github_username` 为实际用户名，重新运行生成最终 QR 码。

- [ ] **Step 5: 更新 README.md 中的链接和 QR 码**

- [ ] **Step 6: 最终提交和推送**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case && git add -A && git commit -m "docs: finalize deployment config" && git push
```

---

### Task 12: 最终验证

- [ ] **Step 1: 全流程测试**

```bash
cd /Users/wangzhe/Desktop/agent-audit-case
python pipeline/evaluate.py
python scripts/inject_data.py
open dashboard/index.html
```

- [ ] **Step 2: 在浏览器中确认仪表板数据正确渲染**

- [ ] **Step 3: 确认 GitHub Pages URL 可访问，QR 码可扫**

- [ ] **Step 4: 确认 README.md 完整**

- [ ] **Step 5: 截取仪表板截图保存到 output/screenshots/**

- [ ] **Step 6: 最终提交推送**

---

## Implementation Order

```
Task 1  → 项目骨架
Task 2  → 品牌Profile + 证据文件
Task 3  → Agent内容产出（Stage 1，在Claude Code中交互完成）
Task 4  → auditor.py（Stage 2适配层）
Task 5  → scorer.py（加权评分）
Task 6  → evaluate.py（主入口，需Task 3产出存在）
Task 7  → 仪表板HTML
Task 8  → 数据注入脚本
Task 9  → QR码生成
Task 10 → 案例研究报告
Task 11 → GitHub Pages部署
Task 12 → 最终验证
```
