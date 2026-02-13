# 质量安全平台 (QSP) v3.0

## ✨ 特性
- ✅ 完整 RBAC 权限控制
- ✅ 用户/项目/版本/漏洞/系统 五大核心管理
- ✅ CI/CD 流水线管理 + 构建失败自动通知
- ✅ SonarQube 集成与代码质量展示
- ✅ 风险评分系统
- ✅ Swagger 接口文档
- ✅ 支持 PostgreSQL/MySQL/SQLite 主从/双活
- ✅ Docker Compose 一键部署

## 🚀 快速开始
### 本地开发
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python scripts/init_db.py
python manage.py runserver
