# ADC项目Submodule设置指南

## 🎯 目标

将`docs`和`workspace`目录转换为Git submodule，实现：
- 📚 **文档独立管理** - docs目录独立版本控制
- 🏗️ **工作空间独立管理** - workspace目录独立版本控制  
- 🔗 **模块化开发** - 支持独立开发和协作
- 📦 **版本解耦** - 主项目和子模块可以独立发布版本

## 🚀 快速设置步骤

### 步骤1: 在Gitee上创建两个新仓库

在您的Gitee账号下创建以下两个**空仓库**（不要初始化README）：

1. **zeus_docs** 
   - 描述: ADC项目文档仓库，包含Ares战神级硬件AI专家的完整设计文档
   - 可见性: Public或Private（根据需要）

2. **zeus_workspace**
   - 描述: ADC项目工作空间，包含Agent开发示例和工具
   - 可见性: Public或Private（根据需要）

### 步骤2: 执行自动化设置脚本

```bash
# 使用我们准备好的脚本
./setup_submodules.sh \
  https://gitee.com/fpga1988/zeus_docs.git \
https://gitee.com/fpga1988/zeus_workspace.git
```

**注意**: 请将URL替换为您实际创建的仓库URL。

## 📋 手动设置步骤（如果需要）

如果您希望手动执行，以下是详细步骤：

### 1. 推送docs仓库

```bash
cd docs
git remote add origin https://gitee.com/fpga1988/zeus_docs.git
git branch -M main
git push -u origin main
cd ..
```

### 2. 推送workspace仓库

```bash
cd workspace
git remote add origin https://gitee.com/fpga1988/zeus_workspace.git
git branch -M main
git push -u origin main
cd ..
```

### 3. 从主仓库移除目录并添加submodule

```bash
# 移除目录
git rm -rf docs workspace
git commit -m "refactor: 准备将docs和workspace转换为submodule"

# 添加submodule
git submodule add https://gitee.com/fpga1988/zeus_docs.git docs
git submodule add https://gitee.com/fpga1988/zeus_workspace.git workspace

# 提交更改
git add .gitmodules docs workspace
git commit -m "feat: 添加docs和workspace作为submodule"
git push origin main
```

## 🔧 日常使用

### 克隆项目（包含submodule）

```bash
# 新克隆项目
git clone --recursive https://gitee.com/fpga1988/zeus.git

# 或者先克隆，再初始化submodule
git clone https://gitee.com/fpga1988/zeus.git
cd zeus
git submodule init
git submodule update
```

### 更新submodule

```bash
# 更新所有submodule到最新版本
git submodule update --remote

# 更新特定submodule
git submodule update --remote docs
git submodule update --remote workspace
```

### 在submodule中开发

```bash
# 进入submodule目录
cd docs  # 或 cd workspace

# 正常的Git操作
git checkout -b feature/new-docs
# 进行修改...
git add .
git commit -m "docs: 添加新的设计文档"
git push origin feature/new-docs

# 回到主项目
cd ..
# 提交submodule的版本更新
git add docs
git commit -m "docs: 更新文档submodule到最新版本"
git push origin main
```

### 切换submodule版本

```bash
# 进入submodule
cd docs

# 切换到特定commit或分支
git checkout <commit-hash>
# 或
git checkout <branch-name>

# 回到主项目并提交版本变更
cd ..
git add docs
git commit -m "docs: 切换文档版本到 <version>"
git push origin main
```

## 🎯 优势说明

### ✅ 使用Submodule的优势

1. **📚 独立文档管理**
   - 文档可以有独立的版本号
   - 文档更新不影响主项目稳定性
   - 支持文档团队独立开发

2. **🏗️ 工作空间隔离**
   - Agent示例和工具独立管理
   - 可以有独立的发布周期
   - 支持实验性功能开发

3. **🔗 版本解耦**
   - 主项目可以锁定特定版本的docs和workspace
   - 支持多个版本并行维护
   - 发布时可以精确控制依赖版本

4. **👥 团队协作友好**
   - 不同团队可以专注于不同模块
   - 减少合并冲突
   - 支持细粒度的权限控制

### ⚠️ 注意事项

1. **学习成本**
   - 团队成员需要了解submodule的工作原理
   - 克隆项目时需要记得使用`--recursive`

2. **复杂性增加**
   - 需要管理多个仓库
   - 版本依赖关系需要仔细维护

3. **CI/CD调整**
   - 构建脚本需要处理submodule
   - 部署时需要确保submodule正确更新

## 🆘 故障排除

### 问题1: Submodule目录为空

```bash
git submodule init
git submodule update
```

### 问题2: Submodule指向错误的版本

```bash
cd <submodule-directory>
git checkout main  # 或目标分支
git pull origin main
cd ..
git add <submodule-directory>
git commit -m "update submodule to latest"
```

### 问题3: 删除submodule

```bash
# 1. 删除submodule条目
git submodule deinit <submodule-path>
git rm <submodule-path>

# 2. 删除.git/modules中的目录
rm -rf .git/modules/<submodule-path>

# 3. 提交更改
git commit -m "remove submodule <submodule-path>"
```

## 📞 支持

如果在设置过程中遇到问题，请：

1. 检查仓库URL是否正确
2. 确认有对应仓库的推送权限
3. 查看Git输出的错误信息
4. 参考本文档的故障排除部分

---

**🎉 设置完成后，您的ADC项目将支持模块化开发，文档和工作空间可以独立管理和版本控制！** 