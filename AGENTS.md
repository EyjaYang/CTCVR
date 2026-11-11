# 项目协作约定

## 项目目标与参考材料

- 本项目使用 Ali-CCP 构建可复现的 CTR / CVR / CTCVR 离线实验，用于推荐算法实习准备。
- 学习目标、模型优先级和周度验收以根目录的 `推荐算法实习准备学习路径与周计划.md` 为准；数据格式与真实关联示例见 `src/data/README.md`。
- 当前阶段按“数据审计与预处理 → LR → DeepFM 同协议对照 → ESMM 最小运行与调试记录”推进，再进入更复杂的多任务模型。
- 截至 2026-11-11：用户计划在 11/11–11/15 投入约 10–12 小时，补做 W2 并推进 W3。后续安排以用户最新时间预算和实际进度为准。

## 指导与实现方式

- 使用中文交流，解释概念时优先使用本地真实样本，区分业务含义、原始存储和模型张量。
- 采用“说明目的与关键概念 → 小块实现 → 实际运行 → 核对结果 → 下一步”的方式指导；每一步给出明确输入、输出、运行命令和验收标准。
- 用户要求指导学习时，围绕当前步骤讲解代码及其原因，给用户保留独立练习和复述空间。用户授权实现时，完成对应实现与必要验证。
- 每轮优先交付一个可验证的小闭环，避免同时铺开多个模型或一次生成整个项目。
- 发现计划与数据条件冲突时，先明确事实并调整方案。不得为赶进度编造指标、完成记录或模型提升。
- 保留用户已有代码和修改；发现问题时指出原因，修改范围应与当前任务一致。

## Python 环境与运行约定

- 统一使用 conda 的 `llmrec` 环境，不使用默认 `base` 环境运行项目实验。
- 从项目根目录执行命令，推荐显式调用：

  ```bash
  conda run --no-capture-output -n llmrec python path/to/script.py
  ```

- 交互终端也可先执行 `conda activate llmrec`，再运行 Python。
- 2026-11-11 已核验：该环境使用 Python 3.10.19，具备 NumPy、SciPy、Pandas、PyArrow、scikit-learn 和 PyTorch。此记录不代表已验证所有版本兼容性或 GPU 可用性。
- 新增依赖前先检查现有能力，优先复用标准库与已有库；依赖调整应记录到项目依赖文件。
- 不将其他科研项目的环境和代码当成本项目已完成的实现或验证证据。

## 数据处理与实验协议

- 原始数据位于 `src/data/`，包括四个 CSV、两个压缩包及 MD5 文件。原始文件保留不变，处理中间文件和训练产物写入单独目录。
- 当前版本没有可用于逐条排序的显式时间戳。不得将 `sample_id`、行号、压缩包时间或用户历史条目的排列当作时间，不得声称已经做了时间切分或严格还原线上时序。
- 第一版保留原始 train/test 边界，只从原始 train 中划出 validation；不合并 train/test 后重新随机划分。划分规则、比例、稳定哈希算法、种子和数据子集范围必须记录。
- 验证集可按 `common_feature_id` 分组稳定划分，避免同一公共记录跨 train/validation；这不等于用户完全隔离，也不等于时间切分。采用其他方案时说明其评估目标和局限。
- 第一版使用已有曝光日志中的原始正负样本，不人为补造未曝光负例，也不默认做类别平衡。用于调试的等概率数据子集采样与只下采样负例必须区分。
- 后续若对训练负例下采样，记录保留概率与校正方法；validation/test 不做按标签下采样，不能将不同采样协议的结果直接当作模型对照。
- 特征字典、频次阈值、截断长度和归一化统计仅在训练部分确定。validation/test 只应用已固定规则，并统计缺失率和未知类别比例。
- 稀疏特征保留 `(field_id, feature_id, value)`；同一域的多值不可被字典赋值覆盖。类别 ID 不当连续数值，权重不擅自解释为原始行为次数。
- 先核验 `conversion=1, click=0` 等标签异常并报告数量，再明确处理策略；不能在解析时静默丢弃。
- 使用小样本先验证解析、关联、切分和读取，再扩大数据规模。小样本指标和前缀抽样检查必须明确标注范围，不外推成全量结论。
- 预处理产物应具备 schema、数据来源、处理配置与统计报告。可采用分片 Parquet 保存解析后的数据；无需在每次训练时重新解析原始控制字符 CSV。
- 保存公共特征时优先保留复用关系，避免不加评估地把数百条公共特征重复复制到每条曝光中。

## 模型、评估与验收

- CTR 使用曝光样本的 `click` 标签；CVR 是点击条件下的转化概率；CTCVR 是曝光空间的点击并转化概率，三者不可混用。
- LR 与 DeepFM 优先对比同一数据版本、特征与评估集合上的 CTR AUC / LogLoss；类别不平衡时不以 Accuracy 作为主要结论。
- ESMM 的基本关系为 `pCTCVR = pCTR × pCVR`。标准训练监督 CTR 与 CTCVR；CVR 条件指标仅在点击样本上评价。
- 先验证 batch 的 shape、取值范围、标签与输入分离、loss 有限、反向传播和小批次过拟合，再进行正式训练。
- 模型对照必须固定数据协议和评估集合，记录参数量、训练预算、耗时、种子与真实指标。调参使用 validation，test 用于最终选定方案的评估。
- 转化正例不足或某一评估子集只有单一类别时，报告样本量与指标不可计算的原因，不伪造 AUC 或宣称稳定提升。
- 区分“已实现”“已运行”“已通过验收”和“计划做”。运行日志、报告与结论应相互对应。

## 目录建议

- `configs/`：数据协议与实验配置。
- `src/data/`：当前原始数据、数据说明及逐步实现的数据处理代码；新产物不要混入原始 CSV。
- `src/models/`、`src/train/`、`src/metrics/`：按实际任务逐步添加。
- `scripts/`：审计、预处理与训练入口。
- `data/processed/`：派生数据、编码字典与 schema。
- `reports/`：审计报告、实验结果和学习验收记录。
- `artifacts/`：模型权重及其他训练产物。
- 不为了目录齐全而创建空模块；若使用版本控制，不纳入原始数据、派生大文件、缓存或模型权重。

<!-- codebase-memory-mcp:start -->
# Codebase Memory

## Codebase Knowledge Graph (codebase-memory-mcp)

This project uses codebase-memory-mcp to maintain a knowledge graph of the codebase.
ALWAYS prefer MCP graph tools over grep/glob/file-search for code discovery.

### Priority Order
1. `search_graph` — find functions, classes, routes, variables by pattern
2. `trace_path` — trace who calls a function or what it calls
3. `get_code_snippet` — read specific function/class source code
4. `check_index_coverage` — validate candidate paths and missed ranges before claims
5. `query_graph` — run Cypher queries for complex patterns
6. `get_architecture` — high-level project summary

### Evidence tiers
- **Scout (Tier 1):** quick positive lookup with few calls and targeted source checks. Mark it provisional; do not make negative or exhaustive claims.
- **Verify (Tier 2, default):** task-directed graph evidence, relevant trace directions, exact snippets for material claims, and relevant pagination.
- **Auditor (Tier 3):** bounded-scope full verification with current generation, complete relevant pagination, both call directions and broader relationships when material, and every limitation disclosed.
- After candidate paths are known in any tier, call `check_index_coverage` once with every evidence path. Add relevant scopes for negative or exhaustive claims. A clean result means no recorded gap, not proof of completeness. For partial, skipped, excluded, stale, pending, or unknown coverage, read/grep the reported ranges or scope before relying on graph results.

### When to fall back to grep/glob
- Searching for string literals, error messages, config values
- Searching non-code files (Dockerfiles, shell scripts, configs)
- When MCP tools return insufficient results

### Examples
- Find a handler: `search_graph(name_pattern=".*OrderHandler.*")`
- Who calls it: `trace_path(function_name="OrderHandler", direction="inbound")`
- Read source: `get_code_snippet(qualified_name="pkg/orders.OrderHandler")`

### Session resets and subagents
- At session start or after compaction, confirm the nearest graph project and generation with `list_projects` or `index_status`, then choose Scout, Verify, or Auditor.
- Before spawning a subagent, query the graph and coverage in the parent. Pass the tier, project, generation/freshness, bounded scope, queries and pagination state, qualified symbols, paths, call-chain findings, coverage evidence with ranges/reasons, source fallback already performed, and unresolved questions in the delegated task context.
- Do not assume subagents inherit MCP access or the parent conversation. If a child lacks MCP tools, it must not call or claim MCP access. It should use the supplied evidence and read/grep exact source, especially every reported missed-coverage range.
<!-- codebase-memory-mcp:end -->
