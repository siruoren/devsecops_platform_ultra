<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="page-title">安全漏洞管理</h1>
      <div>
        <button class="btn btn-outline-primary me-2"><i class="fas fa-upload me-2"></i>导入 Dependency-Check</button>
        <button class="btn btn-primary"><i class="fas fa-plus me-2"></i>工件版本变更</button>
      </div>
    </div>
    <ul class="nav nav-tabs mb-4">
      <li class="nav-item"><a class="nav-link active" href="#">代码质量</a></li>
      <li class="nav-item"><a class="nav-link" href="#">工件漏洞</a></li>
    </ul>
    <div class="card p-4">
      <div class="row mb-3">
        <div class="col-md-4">
          <div class="input-group">
            <span class="input-group-text bg-white"><i class="fas fa-search"></i></span>
            <input type="text" class="form-control" placeholder="按项目名搜索...">
          </div>
        </div>
      </div>
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr><th>项目</th><th>Bugs</th><th>漏洞</th><th>代码异味</th><th>覆盖率</th><th>质量门</th></tr>
          </thead>
          <tbody>
            <tr><td>订单服务</td><td>12</td><td>3</td><td>145</td><td>87.3%</td><td><span class="badge bg-success">PASSED</span></td></tr>
            <tr><td>用户中心</td><td>8</td><td>1</td><td>98</td><td>92.1%</td><td><span class="badge bg-success">PASSED</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
