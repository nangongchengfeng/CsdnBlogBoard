# -*- coding: utf-8 -*-
# @Time    : 2024/12/15 15:40
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : code.py.py
# @Software: PyCharm


# 错误码和消息字典
codes = {
    200: "操作成功",
    501: "操作失败",
    401: "请求头的auth为空",
    405: "请求头的auth格式错误",
    406: "无效的Token或者登录过期,请重新登录！",
    407: "认证异常，请重新登录",
    408: "用户名不存在，请重新输入",
    409: "验证码不正确，请重新输入",
    410: "密码不正确",
    411: "您的账号已被停用,请联系管理员",
    412: "非标准接口JSON数据",
    413: "菜单名称已存在，请重新输入",
    414: "菜单已分配，不能删除",
    415: "部门名称已存在，请重新输入",
    416: "部门已分配，不能删除",
    417: "岗位名称或岗位编码已存在，请重新输入",
    418: "缺少新增管理员参数",
    419: "用户名称已存在，请重新输入",
    420: "缺少修改个人参数",
    421: "缺少修改密码参数",
    422: "两次输入的密码不一致，请重新输入",
    427: "文件上传错误",
}


def get_message(code):
    """根据状态码获取消息"""
    return codes.get(code, "未知错误,请联系管理员")


if __name__ == "__main__":
    print(get_message(200))
    print(get_message(120))