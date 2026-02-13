<template>
  <div>
    <h1 class="page-title mb-4">系统管理</h1>
    <div class="row">
      <div class="col-md-6">
        <div class="card p-4 mb-4">
          <h5 class="section-title"><i class="fas fa-envelope me-2"></i>邮件服务器</h5>
          <div class="mb-3"><label class="form-label">SMTP 服务器</label><input type="text" class="form-control" value="smtp.example.com"></div>
          <div class="row mb-3">
            <div class="col"><label class="form-label">端口</label><input type="text" class="form-control" value="587"></div>
            <div class="col"><label class="form-label">加密</label><select class="form-select"><option>TLS</option><option>SSL</option><option>无</option></select></div>
          </div>
          <div class="mb-3"><label class="form-label">用户名</label><input type="text" class="form-control" value="admin@example.com"></div>
          <div class="mb-3"><label class="form-label">密码</label><input type="password" class="form-control" value="••••••••"></div>
          <div class="mb-3"><label class="form-label">发送人邮箱</label><input type="email" class="form-control" value="noreply@qsp.com"></div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card p-4 mb-4">
          <h5 class="section-title"><i class="fas fa-bell me-2"></i>消息限额</h5>
          <div class="mb-3"><label class="form-label">每日最大站内信 (每用户)</label><input type="number" class="form-control" value="100"></div>
          <div class="mb-3"><label class="form-label">每日最大邮件发送量</label><input type="number" class="form-control" value="500"></div>
        </div>
        <div class="card p-4">
          <h5 class="section-title"><i class="fas fa-database me-2"></i>数据库连接</h5>
          <div class="mb-3"><label class="form-label">主机</label><input type="text" class="form-control" value="localhost"></div>
          <div class="row mb-3"><div class="col"><label class="form-label">端口</label><input type="text" class="form-control" value="5432"></div>
          <div class="col"><label class="form-label">库名</label><input type="text" class="form-control" value="qsp"></div></div>
        </div>
      </div>
    </div>
    <div class="row mt-2"><div class="col-12"><div class="card p-4"><div class="d-flex justify-content-end"><button class="btn btn-primary px-5">保存配置</button></div></div></div></div>
  </div>
</template>
