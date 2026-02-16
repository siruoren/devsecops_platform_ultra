from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def home(request):
    """首页视图"""
    return redirect('/admin/')


def login_view(request):
    """登录视图"""
    return redirect('/admin/login/')


def logout_view(request):
    """注销视图"""
    logout(request)
    return redirect('/admin/login/')


@login_required
def dashboard(request):
    """控制面板视图"""
    return redirect('/admin/')


@login_required
def users(request):
    """用户管理视图"""
    return redirect('/admin/users/user/')


@login_required
def projects(request):
    """项目管理视图"""
    return redirect('/admin/projects/project/')


@login_required
def versions(request):
    """版本管理视图"""
    return render(request, 'versions.html')


@login_required
def cicd(request):
    """CI/CD管理视图"""
    return redirect('/admin/ci_cd/pipeline/')


@login_required
def risk(request):
    """风险管理视图"""
    return redirect('/admin/risk/riskprofile/')


@login_required
def system(request):
    """系统管理视图"""
    return redirect('/admin/system/notification/')


@login_required
def vulnerability(request):
    """漏洞管理视图"""
    return redirect('/admin/')
