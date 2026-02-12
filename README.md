质量安全平台（QSP）项目需求说明书
版本	日期	作者	变更描述
V1.0	2026-02-12	系统架构师	初始版本创建
1. 引言
1.1 项目背景
随着企业软件开发生命周期的复杂化，质量与安全保障成为研发运维一体化的核心挑战。当前缺乏统一的平台对项目应用、发布版本、安全漏洞进行集中管理，导致信息孤岛，无法有效跟踪代码质量、工件漏洞及版本变更影响。为提升研发效能与系统安全性，决定建设质量安全平台（Quality Security Platform, QSP）。

1.2 项目目标
建立统一的应用及版本管理门户，实现应用信息、发布版本、部署环境的集中维护。

集成 SonarQube 代码质量数据与 Dependency-Check 工件漏洞数据，提供多维度的安全分析视图。

支持工件版本变更通知，自动影响分析并通知相关应用负责人。

提供灵活的权限控制，支持多角色、多菜单的访问管理。

构建高可用、可扩展的系统架构，支持单机、主从、双活等多种部署模式，满足不同规模企业的需求。

1.3 项目范围
本项目涵盖五大核心功能模块：

用户管理：用户账户维护、菜单权限分配、个人信息自助修改。

项目管理：应用及其部署环境的全生命周期信息管理。

版本管理：发布版本状态跟踪、应用版本登记、代码质量指标写入。

安全漏洞管理：代码质量扫描结果查看、工件漏洞导入与检索、项目‑工件关系图谱、工件版本变更通知。

系统管理：系统级配置（Web端口、数据库连接、邮件服务器、站内消息限额）及站内通知管理。

2. 总体描述
2.1 用户角色
角色	描述
普通用户	可查看被授权的菜单，管理个人信息（密码、邮箱），登记/修改自己登记的应用版本。
用户管理员	拥有用户管理菜单权限，可创建用户并分配菜单权限。
项目管理员	拥有项目管理菜单权限，可维护应用及环境信息。
版本管理员	拥有版本管理菜单权限，可管理发布版本状态、查看所有登记信息。
漏洞管理员	拥有安全漏洞管理菜单权限，可导入漏洞数据、查看图谱。
系统管理员	拥有系统管理菜单权限，可配置系统参数。
超级管理员	内置 admin 账户，具备所有权限。
2.2 系统上下文
外部系统集成：

SonarQube：通过 API 写入/读取项目代码质量指标。

Dependency-Check：接收 JSON 格式的漏洞扫描报告。

Git 仓库：记录应用源码位置（不直接交互）。

邮件服务器：发送通知邮件。

用户交互：

浏览器访问 Web UI（前后端分离，提供 REST API）。

API 客户端（如 CI/CD 工具）调用接口导入数据或修改状态。

2.3 约束条件
后端必须使用 Python 3.9+ / Django 3.2 LTS。

数据库需支持 PostgreSQL、MySQL、SQLite 三种引擎，并具备主从读写分离能力。

应用需支持双活多数据中心部署（应用层双写或数据库层同步）。

提供 Docker 镜像及 Docker Compose 编排文件，一键部署。

所有配置项均支持环境变量注入。

3. 功能需求
3.1 用户管理（菜单1）
编号	功能点	详细描述
U1	用户新建	管理员可创建用户，填写账户名、密码、邮箱、姓名、部门、职位，并分配五个菜单权限（用户管理、项目管理、版本管理、安全漏洞管理、系统管理）。
U2	用户列表与检索	分页展示所有用户，支持按用户名、邮箱、部门搜索。
U3	用户信息编辑	管理员可修改用户的基本信息及权限；普通用户仅能修改自己的邮箱、姓名、电话、头像等，不可修改权限。
U4	密码自助修改	登录用户可修改自己的密码，需验证原密码，新密码长度≥8位，且与确认密码一致。
U5	登录/注销	使用用户名+密码登录，认证成功后返回用户信息及权限标识。
U6	权限鉴权	前端根据后端返回的权限字段动态渲染菜单；API 接口依据登录用户权限进行访问控制。
3.2 项目管理（菜单2）
编号	功能点	详细描述
P1	部署环境维护	增删改查“部署环境”，字段：环境名、服务器地址列表（多个IP逗号间隔）。
P2	应用信息管理	表单形式维护应用信息，字段：应用名、Git仓库地址、仓库内路径、所属环境、部署目录、启动脚本、停止脚本、启动cron、停止cron、SonarQube项目地址、负责人。
P3	应用列表与检索	分页展示所有应用，支持按应用名、仓库地址、环境、负责人进行搜索过滤。
P4	负责人关联	负责人从用户库中选择，仅允许选择有效用户。
3.3 版本管理（菜单3）
编号	功能点	详细描述
V1	发布版本维护	维护发布版本记录，字段：版本号（唯一）、创建时间（自动）、封板时间（手动）、状态（开发中/已封板）。
V2	版本状态变更 API	提供 API 接口用于修改版本状态（如从开发中变更为已封板）。
V3	代码质量写入 API	提供 API 接收 SonarQube 扫描结果（JSON），存储至发布版本的“代码质量”字段中。
V4	应用版本登记	用户在发布版本详情页点击【登记】，选择应用并填写该应用在此版本中的版本号，保存为登记记录。
V5	登记信息修改	用户仅能修改自己登记的应用版本信息；管理员可修改任意记录。
V6	发布版本详情页	点击版本号进入详情页，展示该版本下所有已登记的应用及应用版本列表，支持按应用名搜索。
3.4 安全漏洞管理（菜单4）
3.4.1 代码质量
编号	功能点	详细描述
CQ1	项目筛选	支持按项目名称关键词匹配，过滤出符合条件项目。
CQ2	代码质量展示	展示所选项目的最近一次 SonarQube 扫描摘要（如Bug数、漏洞数、代码异味、覆盖率等）。
CQ3	历史趋势（可选）	（扩展）可查看项目代码质量历史趋势图。
3.4.2 工件漏洞
编号	功能点	详细描述
AV1	漏洞扫描结果导入	页面导入：用户选择项目，上传 Dependency-Check 生成的 JSON 文件，系统解析并存储漏洞详情。
API 导入：提供接口供 CI 调用，直接推送 JSON 内容。
AV2	漏洞数据检索	支持关键词匹配项目名、工件名、工件版本号，多维度搜索筛选。
AV3	项目‑工件关系图谱	筛选项目后，以关系图（力导向图）展示该项目下所有直接依赖的工件及其漏洞状态。
- 每个工件节点按漏洞严重性着色（例如：无漏洞-绿色，低危-蓝色，中危-橙色，高危-红色，致命-深红）。
- 鼠标悬停/点击节点显示该工件的漏洞列表及详细说明。
AV4	工件‑项目关系图谱	筛选工件后，以关系图展示该工件被哪些项目引用，以及这些项目中该工件的版本信息。
- 节点着色规则同 AV3。
- 点击项目节点，弹出浮层显示该项目的登记应用名称、版本、负责人及所在的发布版本。
AV5	工件版本变更通知	申请流程：
1. 申请人选择发布版本。
2. 填写工件组织名（groupId）、工件名（artifactId）、新版本号。
3. 选择通知类型：站内消息、邮件、两者都发。
4. 点击【发布】。
后台任务：
- 检索所选发布版本下所有已登记的应用。
- 分析这些应用所依赖的工件是否包含该工件。
- 若包含，根据通知类型向该应用的负责人发送站内消息和/或邮件。
3.4.3 通用要求
所有图谱支持缩放、拖拽，并可在浏览器中保存为图片。

列表页与图谱页可通过参数联动（如从列表点击项目跳转到图谱）。

3.5 系统管理（菜单5）
编号	功能点	详细描述
S1	Web端口配置	配置应用监听的端口号（主要用于生成前端访问地址或启动脚本）。
S2	数据库连接信息管理	加密存储主库/从库的连接参数（主机、端口、库名、用户名、密码）。支持动态切换数据源（需重启）。
S3	站内消息限额	设置每个用户每日最大接收站内通知数量，防止轰炸。
S4	邮件服务器配置	配置 SMTP 服务器地址、端口、账号、密码、发送人邮箱、发送人名称。
S5	邮件每日限额	设置系统每日最大邮件发送总量，避免触发邮件服务商限制。
S6	站内通知中心	用户登录后查看个人站内消息，支持标为已读、批量已读、删除。顶部导航栏显示未读消息数。
S7	配置持久化	所有配置保存至数据库，并通过缓存加速读取。系统启动时从数据库加载。
4. 非功能需求
4.1 性能
页面加载时间 < 2秒（无大量图谱时）。

API 响应时间 < 500ms（95分位）。

关系图谱渲染支持最多 500 个节点，初始加载时间 < 5秒。

支持 100+ 并发用户。

4.2 安全性
密码使用 PBKDF2 算法加密存储。

所有 API（除登录、注册外）均需认证，支持 Session/Cookie 认证。

敏感配置信息（数据库密码、邮件密码）在数据库中加密存储。

防止 CSRF、XSS、SQL注入（由 Django 框架天然防护）。

前后端分离，CORS 配置严格限制来源。

4.3 可用性
核心服务（Web、数据库）需支持主从切换，故障时从库自动接管读流量。

双活模式下，任一数据中心失效不影响整体服务。

关键业务（漏洞导入、版本变更通知）采用 Celery 异步任务，失败自动重试。

提供健康检查接口 /health/。

4.4 可维护性
遵循 PEP8 编码规范，模块化设计，各应用解耦。

配置与环境分离，通过 .env 文件注入。

提供 Swagger/OpenAPI 文档，接口即文档。

日志分级，生产环境输出 JSON 格式日志，便于 ELK 采集。

4.5 可扩展性
数据库支持动态增加从库（通过路由器配置）。

双活架构支持横向扩展 Web 节点。

漏洞导入支持插件化扩展，未来可增加其他扫描工具（如 OWASP DC、Black Duck）。

5. 技术架构
5.1 整体架构图
text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Nginx负载均衡 │────▶│   Django Web    │────▶│  Celery Worker  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
  ┌─────────────┐        ┌─────────────┐          ┌─────────────┐
  │ 静态资源/CDN│        │   Redis     │          │  RabbitMQ   │
  └─────────────┘        │  缓存/队列  │          │  (备用)     │
                         └─────────────┘          └─────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │    PostgreSQL/MySQL │
                     │    主从复制/双活    │
                     └─────────────────────┘
5.2 技术选型
组件	技术栈	说明
后端框架	Django 3.2 LTS + Django REST Framework	提供 ORM、Admin、REST API 快速开发
数据库	PostgreSQL / MySQL / SQLite	主从配置由 DATABASE_ROUTERS 实现
缓存/消息队列	Redis 7	缓存 Session、Celery Broker
异步任务	Celery 5	处理漏洞导入、邮件发送等耗时任务
API 文档	drf-yasg / Swagger	自动生成 OpenAPI 规范
前端	独立前端（Vue/React）或 Django模板	本需求说明书仅定义后端 API，前端分离
部署	Docker + Docker Compose	多环境编排，支持主从/双活扩展
监控	Health check + Flower	Celery 任务监控
5.3 数据库设计要点
读写分离：定义 MasterSlaveRouter，读请求路由到 replica，写请求到 default。

双活支持：预留 ActiveActiveRouter，可配置多组主从；应用层双写需业务代码适配。

数据分片：暂不涉及。

加密存储：敏感字段使用 django-cryptography 或自定义 Fernet 加密。

5.4 关键业务流程
漏洞导入流程

用户上传 JSON → API 接收 → 存入 DependencyCheckScan → 异步解析 → 生成 ArtifactVulnerability 记录 → 更新项目漏洞摘要。

工件版本变更通知流程

用户提交变更申请 → 创建 ArtifactVersionChange 记录 → 触发 Celery 任务 → 检索版本下所有应用 → 解析应用依赖（需集成依赖分析工具或人工录入） → 匹配受影响项目 → 向负责人发送站内消息/邮件。

6. 部署方案
6.1 单机开发模式
使用 SQLite 数据库，Redis 可选。

docker-compose.yml 启动 Web + Redis（可选）。

适用于功能测试、本地开发。

6.2 生产单节点模式（小型团队）
使用 PostgreSQL 单实例。

Docker Compose 编排：postgres + redis + web + celery + nginx。

Web 可扩展多副本，依赖外部负载均衡。

6.3 生产主从模式（中型团队）
PostgreSQL 主从异步流复制，Redis 主从。

启用 MasterSlaveRouter，读流量分发到从库。

Docker Compose 配置示例：postgres_master、postgres_slave、redis_master、redis_slave、web（多副本）、celery、nginx。

6.4 双活数据中心模式（大型团队）
每个数据中心独立部署一套主从 PostgreSQL 和 Redis。

应用层通过 ActiveActiveRouter 实现写双活（同步双写两个数据中心主库）或就近读。

需要全局负载均衡器（如 F5、AWS Route53）进行流量分发。

数据冲突通过业务时间戳或全局唯一ID规避。

7. 数据模型概览
实体	主要属性
User	username, email, password, permissions(5个bool), avatar, phone, department, position
Environment	name, server_ips
Project	name, git_repo, git_path, environment_id, deploy_dir, start_script, stop_script, start_cron, stop_cron, sonarqube_url, owner_id
ReleaseVersion	version, created_at, released_at, status, code_quality(JSON), created_by
VersionRegistration	release_version_id, project_id, app_version, created_by
CodeQualityScan	project_id, scan_date, metrics(JSON), quality_gate, created_by
DependencyCheckScan	project_id, scan_date, json_result(JSON), summary(JSON), created_by
ArtifactVulnerability	scan_id, artifact_name, artifact_version, cve, severity, description, remediation, cvss_score
ArtifactVersionChange	release_version_id, group_id, artifact_id, version, notify_type, status, created_by
SystemConfig	web_port, db_connection(JSON), max_daily_messages, smtp_server, smtp_port, smtp_username, smtp_password, sender_email, sender_name, max_daily_emails
Notification	recipient_id, sender_id, title, content, is_read, read_at
8. 验收标准
完成所有功能点开发并通过测试用例。

API 文档完整，可在线调试。

提供三种数据库（SQLite、PostgreSQL、MySQL）的 Docker Compose 启动验证。

通过压力测试：100 并发用户下主要接口成功率 > 99.5%。

完成主从切换演练，读流量自动转移至新从库。

双活架构（如实现）需通过故障注入测试。

9. 附录
9.1 术语表
术语	解释
工件（Artifact）	编译产物，如 JAR、NPM 包、Docker 镜像
封板	版本开发完成，不再接受新功能变更
SonarQube	开源代码质量管理平台
Dependency-Check	OWASP 提供的软件组成分析工具
9.2 参考文档
Django 官方文档

Django REST Framework 教程

Celery 最佳实践

PostgreSQL 主从复制配置

