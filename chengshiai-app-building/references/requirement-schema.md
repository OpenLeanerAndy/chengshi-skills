# 需求台账和完整性标准

## 目录

1. 台账状态
2. 大模块定义
3. 推荐 JSON 结构
4. 阶段门

## 1. 台账状态

为每条信息记录以下状态之一：

- `confirmed`：用户明确确认。
- `inferred`：Agent 根据上下文推导，等待确认。
- `unclear`：答案模糊或相互矛盾。
- `deferred`：明确放入后续范围。
- `not_applicable`：已考虑但不适用，并写明原因。

不得把沉默、模糊同意或 Agent 建议标记成 `confirmed`。

## 2. 大模块定义

大模块是相对独立的业务子系统，通常同时具备：

- 独立的主要业务目标。
- 独立的核心业务对象或数据。
- 可以描述一套完整的起点、处理过程和结果。
- 可以单独验收和交付价值。

课程管理、用户管理、学习记录管理可以是三个模块。读取数据、计算、输出结果、通知用户通常是一个模块内的连续步骤。

先确认模块边界，再统计数量。大模块不少于 3 个时才要求记录分期决定；少于 3 个时不得把“未分期”当作缺失项。

## 3. 推荐 JSON 结构

长访谈建议在项目目录维护 `requirements-state.json`：

```json
{
  "project": {
    "wanted_app": "",
    "current_method": "",
    "pain_points": [],
    "final_outputs": []
  },
  "users_access": {
    "users": [],
    "access_scope": "self | lan | internet | mixed",
    "roles_and_permissions": [],
    "data_sharing": "",
    "app_form": "local | lan_web | public_web",
    "local_app_tradeoff_accepted": false
  },
  "scope": {
    "module_boundaries_confirmed": false,
    "phasing_confirmed": false,
    "modules": [
      {
        "name": "",
        "in_current_scope": true,
        "things_to_do": [],
        "workflow": [],
        "data": [
          {
            "name": "",
            "source": "",
            "current_acquisition": ""
          }
        ],
        "rules": [],
        "pages": [],
        "normal_confirmed": false,
        "exceptions": [],
        "exceptions_confirmed": false
      }
    ]
  },
  "design": {
    "theme_color": "",
    "logo": "provided | none | pending",
    "style_notes": "",
    "mockups": [
      {"page": "", "path": ""}
    ],
    "mockups_confirmed": false
  },
  "delivery": {
    "target_os": "windows | macos",
    "deployment_target": "local | lan | public",
    "launcher_required": true,
    "launcher_panel": ["status", "url", "start", "stop"]
  },
  "prd": {
    "path": "产品需求说明书.html",
    "complete": false,
    "confirmed": false,
    "confirmed_at": ""
  },
  "testing": {
    "syntax": false,
    "dependencies": false,
    "startup": false,
    "functions": false,
    "apis": false,
    "ui_match": false,
    "launcher": false,
    "cleanup": false
  },
  "deployment": {
    "deployed": false,
    "url": "",
    "user_trial_requested": false
  }
}
```

字段不适用时写清原因，不要留下空值。例如没有外部 API 时，可在测试记录中说明“不适用：无外部或后端 API”。

## 4. 阶段门

### 模块正常需求确认门

本期每个模块必须具备：要做的事情、正常流程、数据及获取方式、规则、页面或输出，并得到用户明确确认。

### 异常和设计门

本期每个模块必须完成异常检查；主题色和 Logo 必须得到答案或明确采用建议方案。

### 页面效果图门

每个已确认页面必须有对应效果图。效果图必须使用实际字段和代表性数据，路径可访问，并得到用户确认。

### PRD 门

`产品需求说明书.html` 必须包含全部需求、全部最新页面效果图、技术方案、交付运行方式、验收标准和确认记录。只有 `prd.confirmed=true` 才能开发。

### 部署门

全部适用测试项必须通过，双击运行程序必须可用，实际应用必须与确认的 HTML PRD 一致，才能部署给用户试用。
